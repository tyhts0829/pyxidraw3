"""
EffectChain - エフェクトチェーン実装（次期API仕様）
E.add()から始まるメソッドチェーンAPIと高性能キャッシュを提供。
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any, Callable, Dict, List
from weakref import WeakValueDictionary

from effects.array import Array
from effects.buffer import Buffer
from effects.extrude import Extrude
from effects.filling import Filling

# 既存のエフェクトクラスをインポート
from effects.noise import Noise
from effects.rotation import Rotation
from effects.scaling import Scaling
from effects.subdivision import Subdivision
from effects.transform import Transform
from effects.translation import Translation
from engine.core.geometry import Geometry
from engine.core.geometry_data import GeometryData

from .geometry_api import GeometryAPI


class EffectStep:
    """エフェクトチェーンの1つのステップを表すクラス。"""

    def __init__(self, effect_name: str, params: dict):
        self.effect_name = effect_name
        self.params = params
        self.params_hash = self._compute_hash(params)

    def _compute_hash(self, params: dict) -> int:
        """パラメータのハッシュ値を計算。"""

        def make_hashable(obj):
            if isinstance(obj, dict):
                return tuple(sorted((k, make_hashable(v)) for k, v in obj.items()))
            elif isinstance(obj, (list, tuple)):
                return tuple(make_hashable(item) for item in obj)
            else:
                return obj

        hashable_params = make_hashable(params)
        return hash(hashable_params)

    def __eq__(self, other):
        if not isinstance(other, EffectStep):
            return False
        return self.effect_name == other.effect_name and self.params_hash == other.params_hash

    def __hash__(self):
        return hash((self.effect_name, self.params_hash))


class EffectChain:
    """エフェクトチェーン実装クラス。"""

    # エフェクトクラスのレジストリ
    _effect_registry: Dict[str, Any] = {
        "noise": Noise,
        "filling": Filling,
        "rotation": Rotation,
        "scaling": Scaling,
        "translation": Translation,
        "transform": Transform,
        "subdivision": Subdivision,
        "extrude": Extrude,
        "buffer": Buffer,
        "array": Array,
    }

    # カスタムエフェクトのレジストリ
    _custom_effects: Dict[str, Callable] = {}

    # キャッシュ
    _cache: WeakValueDictionary[tuple, GeometryAPI] = WeakValueDictionary()

    def __init__(self, base_geometry: GeometryAPI):
        """
        Args:
            base_geometry: ベースとなるGeometryAPI
        """
        self._base_geometry = base_geometry
        self._steps: List[EffectStep] = []

    def _get_cache_key(self) -> tuple:
        """キャッシュキーを生成。"""
        base_guid = self._base_geometry.guid
        steps_hash = tuple(self._steps)
        return (base_guid, steps_hash)

    def _apply_effects(self) -> GeometryAPI:
        """全エフェクトを順次適用（統一API処理）。"""
        current_api = self._base_geometry
        
        for step in self._steps:
            current_api = self._apply_single_effect(current_api, step)
        
        return current_api
    
    def _apply_single_effect(self, geometry_api: GeometryAPI, step: EffectStep) -> GeometryAPI:
        """単一エフェクトの適用。"""
        if step.effect_name in self._effect_registry:
            return self._wrap_legacy_effect(
                self._effect_registry[step.effect_name], 
                geometry_api, 
                step.params
            )
        elif step.effect_name in self._custom_effects:
            return self._custom_effects[step.effect_name](geometry_api, **step.params)
        else:
            raise ValueError(f"Unknown effect: {step.effect_name}")
    
    def _wrap_legacy_effect(self, effect_class, geometry_api: GeometryAPI, params: dict) -> GeometryAPI:
        """旧エフェクトをGeometryAPI対応にラップ。"""
        coords, offsets = geometry_api.data.as_arrays()
        legacy_geom = Geometry(coords, offsets)
        
        # キャッシュ無効化されたエフェクトインスタンスを作成
        effect_instance = self._create_effect_instance(effect_class)
        result = effect_instance.apply(legacy_geom, **params)
        
        return GeometryAPI(GeometryData(result.coords, result.offsets))
    
    def _create_effect_instance(self, effect_class):
        """キャッシュ無効化されたエフェクトインスタンスを作成。"""
        instance = effect_class()
        if hasattr(instance, 'disable_cache'):
            instance.disable_cache()  # EffectChainレベルでキャッシュ管理
        return instance

    def _get_result(self) -> GeometryAPI:
        """結果を取得（キャッシュ使用）。"""
        cache_key = self._get_cache_key()

        if cache_key in self._cache:
            return self._cache[cache_key]

        # エフェクトを適用して結果を計算
        result = self._apply_effects()
        self._cache[cache_key] = result
        return result

    def _add_step(self, effect_name: str, params: dict = None, **kwargs) -> "EffectChain":
        """新しいエフェクトステップを追加。"""
        if params is None:
            params = kwargs if kwargs else {}
        else:
            params = {**params, **kwargs}
            
        new_chain = EffectChain(self._base_geometry)
        new_chain._steps = self._steps.copy()
        new_chain._steps.append(EffectStep(effect_name, params))
        return new_chain

    # === 標準エフェクトメソッド ===

    def noise(
        self,
        intensity: float = 0.5,
        frequency: tuple[float, float, float] | float = (0.5, 0.5, 0.5),
        t: float = 0.0,
        **params,
    ) -> "EffectChain":
        """ノイズエフェクトを追加。"""
        all_params = {"intensity": intensity, "frequency": frequency, "t": t, **params}
        return self._add_step("noise", all_params)

    def filling(self, pattern: str = "lines", density: float = 0.5, angle: float = 0.0, **params) -> "EffectChain":
        """塗りつぶしエフェクトを追加。"""
        all_params = {"pattern": pattern, "density": density, "angle": angle, **params}
        return self._add_step("filling", all_params)

    def rotation(
        self, center: tuple[float, float, float] = (0, 0, 0), rotate: tuple[float, float, float] = (0, 0, 0), **params
    ) -> "EffectChain":
        """回転エフェクトを追加。"""
        all_params = {"center": center, "rotate": rotate, **params}
        return self._add_step("rotation", all_params)

    def scaling(
        self, center: tuple[float, float, float] = (0, 0, 0), scale: tuple[float, float, float] = (1, 1, 1), **params
    ) -> "EffectChain":
        """拡大縮小エフェクトを追加。"""
        all_params = {"center": center, "scale": scale, **params}
        return self._add_step("scaling", all_params)

    def translation(
        self, offset_x: float = 0.0, offset_y: float = 0.0, offset_z: float = 0.0, **params
    ) -> "EffectChain":
        """平行移動エフェクトを追加。"""
        all_params = {"offset_x": offset_x, "offset_y": offset_y, "offset_z": offset_z, **params}
        return self._add_step("translation", all_params)

    def transform(self, **params) -> "EffectChain":
        """複合変換エフェクトを追加。"""
        return self._add_step("transform", params)

    def subdivision(self, n_divisions: float = 0.5, **params) -> "EffectChain":
        """細分化エフェクトを追加。"""
        all_params = {"n_divisions": n_divisions, **params}
        return self._add_step("subdivision", all_params)

    def extrude(
        self,
        direction: tuple[float, float, float] = (0.0, 0.0, 1.0),
        distance: float = 0.5,
        scale: float = 0.5,
        subdivisions: float = 0.5,
        **params,
    ) -> "EffectChain":
        """押し出しエフェクトを追加。"""
        all_params = {
            "direction": direction,
            "distance": distance,
            "scale": scale,
            "subdivisions": subdivisions,
            **params,
        }
        return self._add_step("extrude", all_params)

    def buffer(
        self, distance: float = 0.5, join_style: float = 0.5, resolution: float = 0.5, **params
    ) -> "EffectChain":
        """バッファエフェクトを追加。"""
        all_params = {"distance": distance, "join_style": join_style, "resolution": resolution, **params}
        return self._add_step("buffer", all_params)

    def array(
        self,
        n_duplicates: float = 0.5,
        offset: tuple[float, float, float] = (0.0, 0.0, 0.0),
        rotate: tuple[float, float, float] = (0.5, 0.5, 0.5),
        scale: tuple[float, float, float] = (0.5, 0.5, 0.5),
        center: tuple[float, float, float] = (0.0, 0.0, 0.0),
        **params,
    ) -> "EffectChain":
        """配列エフェクトを追加。"""
        all_params = {
            "n_duplicates": n_duplicates,
            "offset": offset,
            "rotate": rotate,
            "scale": scale,
            "center": center,
            **params,
        }
        return self._add_step("array", all_params)

    # === 拡張機能 ===

    def apply(self, func: Callable[[GeometryAPI], GeometryAPI]) -> "EffectChain":
        """ワンショット効果を適用。

        Args:
            func: GeometryAPIを受け取りGeometryAPIを返す関数

        Returns:
            新しいEffectChain
        """
        func_id = f"apply_{id(func)}"
        self._custom_effects[func_id] = func
        return self._add_step(func_id, {})

    # === 動的メソッド生成 ===

    def __getattr__(self, name: str):
        """未定義メソッドの動的生成。"""
        if name in self._custom_effects:

            def custom_effect(**params):
                return self._add_step(name, params)

            return custom_effect
        else:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    # === 結果取得 ===

    def result(self) -> GeometryAPI:
        """最終結果を取得。"""
        return self._get_result()

    def __call__(self) -> GeometryAPI:
        """() で結果を取得。"""
        return self.result()

    # 仕様書との互換性のため、チェーン終端で自動的にGeometryAPIを返す
    def __repr__(self) -> str:
        """文字列表現。"""
        steps_str = " → ".join(step.effect_name for step in self._steps)
        return f"EffectChain({steps_str})"

    # プロパティとして結果を取得（仕様書の例に対応）
    @property
    def geometry(self) -> GeometryAPI:
        """プロパティとして結果を取得。"""
        return self._get_result()

    def steps(self) -> List[str]:
        """適用されるエフェクトのリストを取得。"""
        return [step.effect_name for step in self._steps]


class EffectFactory:
    """エフェクトファクトリクラス（E）。"""

    # カスタムエフェクトのグローバルレジストリ
    _global_custom_effects: Dict[str, Callable] = {}

    @staticmethod
    def add(geometry: GeometryAPI) -> EffectChain:
        """エフェクトチェーンを開始。

        Args:
            geometry: ベースとなるGeometryAPI

        Returns:
            EffectChain: 新しいエフェクトチェーン
        """
        return EffectChain(geometry)

    @classmethod
    def register(cls, name: str):
        """エフェクト登録デコレータ。

        Args:
            name: エフェクト名

        Returns:
            デコレータ関数
        """

        def decorator(func: Callable[[GeometryAPI], GeometryAPI]):
            cls._global_custom_effects[name] = func
            EffectChain._custom_effects[name] = func
            return func

        return decorator

    @classmethod
    def list_effects(cls) -> Dict[str, List[str]]:
        """利用可能なエフェクトのリストを取得。"""
        return {
            "standard": list(EffectChain._effect_registry.keys()),
            "custom": list(cls._global_custom_effects.keys()),
        }

    @classmethod
    def clear_cache(cls):
        """エフェクトキャッシュをクリア。"""
        EffectChain._cache.clear()


# シングルトンインスタンス（E）
E = EffectFactory()
