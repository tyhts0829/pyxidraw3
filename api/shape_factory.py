"""
G - 形状ファクトリクラス（次期API仕様）
高性能キャッシュ付きの形状生成API。
"""

from __future__ import annotations

from functools import lru_cache
from typing import List, Sequence, Union

import numpy as np

from engine.core.geometry_data import GeometryData
from shapes.asemic_glyph import AsemicGlyph
from shapes.attractor import Attractor
from shapes.capsule import Capsule
from shapes.cone import cone_data
from shapes.cylinder import cylinder_data
from shapes.grid import grid_data

# _data関数が存在しないshapeはクラスを直接インポート
from shapes.lissajous import Lissajous

# 既存のshape生成関数とクラスをインポート
from shapes.polygon import polygon_data
from shapes.polyhedron import Polyhedron
from shapes.sphere import sphere_data
from shapes.text import Text
from shapes.torus import torus_data

from .geometry_api import GeometryAPI


class ShapeFactory:
    """高性能キャッシュ付き形状ファクトリ（G）。

    Usage:
        from api import G
        sphere = G.sphere(subdivisions=0.5)
        polygon = G.polygon(n_sides=6)
    """

    @staticmethod
    @lru_cache(maxsize=128)
    def _cached_shape(shape_name: str, params_tuple: tuple) -> GeometryData:
        """内部キャッシュ機能。パラメータのタプルでキャッシュ。"""
        params_dict = dict(params_tuple)

        # 形状名に基づいて適切な生成関数またはクラスを呼び出し
        if shape_name == "sphere":
            return sphere_data(**params_dict)
        elif shape_name == "polygon":
            return polygon_data(**params_dict)
        elif shape_name == "grid":
            return grid_data(**params_dict)
        elif shape_name == "polyhedron":
            return Polyhedron().generate(**params_dict)
        elif shape_name == "torus":
            return torus_data(**params_dict)
        elif shape_name == "cylinder":
            return cylinder_data(**params_dict)
        elif shape_name == "cone":
            return cone_data(**params_dict)
        elif shape_name == "lissajous":
            return Lissajous().generate(**params_dict)
        elif shape_name == "capsule":
            return Capsule().generate(**params_dict)
        elif shape_name == "attractor":
            return Attractor().generate(**params_dict)
        elif shape_name == "text":
            return Text().generate(**params_dict)
        elif shape_name == "asemic_glyph":
            return AsemicGlyph().generate(**params_dict)
        else:
            raise ValueError(f"Unknown shape: {shape_name}")

    @staticmethod
    def _params_to_tuple(**params) -> tuple:
        """パラメータ辞書をキャッシュ可能なタプルに変換。"""

        # ネストした値も含めて再帰的にソート・変換
        def make_hashable(obj):
            if isinstance(obj, dict):
                return tuple(sorted((k, make_hashable(v)) for k, v in obj.items()))
            elif isinstance(obj, (list, tuple)):
                return tuple(make_hashable(item) for item in obj)
            elif isinstance(obj, np.ndarray):
                return tuple(obj.flatten())
            else:
                return obj

        return tuple(sorted((k, make_hashable(v)) for k, v in params.items()))

    # === 形状生成メソッド ===

    @classmethod
    def sphere(cls, subdivisions: float = 0.5, sphere_type: float = 0.5, **params) -> GeometryAPI:
        """球体を生成。

        Args:
            subdivisions: 細分化レベル（0.0-1.0）
            sphere_type: 球体タイプ（0.0=wireframe, 1.0=zigzag）
            **params: 追加パラメータ

        Returns:
            GeometryAPI: 生成された球体
        """
        all_params = {"subdivisions": subdivisions, "sphere_type": sphere_type, **params}
        params_tuple = cls._params_to_tuple(**all_params)
        data = cls._cached_shape("sphere", params_tuple)
        return GeometryAPI(data)

    @classmethod
    def polygon(cls, n_sides: Union[int, float] = 6, **params) -> GeometryAPI:
        """多角形を生成。

        Args:
            n_sides: 辺の数
            **params: 追加パラメータ

        Returns:
            GeometryAPI: 生成された多角形
        """
        all_params = {"n_sides": n_sides, **params}
        params_tuple = cls._params_to_tuple(**all_params)
        data = cls._cached_shape("polygon", params_tuple)
        return GeometryAPI(data)

    @classmethod
    def grid(cls, divisions: Union[int, float] = 10, **params) -> GeometryAPI:
        """グリッドを生成。

        Args:
            divisions: 分割数
            **params: 追加パラメータ

        Returns:
            GeometryAPI: 生成されたグリッド
        """
        # grid_dataはn_divisionsパラメータを期待
        n_divisions = (divisions, divisions) if isinstance(divisions, (int, float)) else divisions
        all_params = {"n_divisions": n_divisions, **params}
        params_tuple = cls._params_to_tuple(**all_params)
        data = cls._cached_shape("grid", params_tuple)
        return GeometryAPI(data)

    @classmethod
    def polyhedron(cls, polyhedron_type: float = 0.0, **params) -> GeometryAPI:
        """正多面体を生成。

        Args:
            polyhedron_type: 多面体タイプ
            **params: 追加パラメータ

        Returns:
            GeometryAPI: 生成された正多面体
        """
        all_params = {"polyhedron_type": polyhedron_type, **params}
        params_tuple = cls._params_to_tuple(**all_params)
        data = cls._cached_shape("polyhedron", params_tuple)
        return GeometryAPI(data)

    @classmethod
    def lissajous(cls, **params) -> GeometryAPI:
        """リサージュ曲線を生成。

        Args:
            **params: パラメータ

        Returns:
            GeometryAPI: 生成されたリサージュ曲線
        """
        params_tuple = cls._params_to_tuple(**params)
        data = cls._cached_shape("lissajous", params_tuple)
        return GeometryAPI(data)

    @classmethod
    def torus(cls, **params) -> GeometryAPI:
        """トーラスを生成。

        Args:
            **params: パラメータ

        Returns:
            GeometryAPI: 生成されたトーラス
        """
        params_tuple = cls._params_to_tuple(**params)
        data = cls._cached_shape("torus", params_tuple)
        return GeometryAPI(data)

    @classmethod
    def cylinder(cls, radius: float = 0.3, height: float = 0.6, segments: int = 32, **params) -> GeometryAPI:
        """円柱を生成。

        Args:
            radius: 円柱の半径
            height: 円柱の高さ
            segments: 周囲のセグメント数
            **params: 追加パラメータ

        Returns:
            GeometryAPI: 生成された円柱
        """
        all_params = {"radius": radius, "height": height, "segments": segments, **params}
        params_tuple = cls._params_to_tuple(**all_params)
        data = cls._cached_shape("cylinder", params_tuple)
        return GeometryAPI(data)

    @classmethod
    def cone(cls, **params) -> GeometryAPI:
        """円錐を生成。

        Args:
            **params: パラメータ

        Returns:
            GeometryAPI: 生成された円錐
        """
        params_tuple = cls._params_to_tuple(**params)
        data = cls._cached_shape("cone", params_tuple)
        return GeometryAPI(data)

    @classmethod
    def capsule(cls, **params) -> GeometryAPI:
        """カプセルを生成。

        Args:
            **params: パラメータ

        Returns:
            GeometryAPI: 生成されたカプセル
        """
        params_tuple = cls._params_to_tuple(**params)
        data = cls._cached_shape("capsule", params_tuple)
        return GeometryAPI(data)

    @classmethod
    def attractor(cls, **params) -> GeometryAPI:
        """ストレンジアトラクターを生成。

        Args:
            **params: パラメータ

        Returns:
            GeometryAPI: 生成されたアトラクター
        """
        params_tuple = cls._params_to_tuple(**params)
        data = cls._cached_shape("attractor", params_tuple)
        return GeometryAPI(data)

    @classmethod
    def text(cls, text_content: str = "PyxiDraw", **params) -> GeometryAPI:
        """テキストを生成。

        Args:
            text_content: テキスト内容
            **params: パラメータ

        Returns:
            GeometryAPI: 生成されたテキスト
        """
        all_params = {"text_content": text_content, **params}
        params_tuple = cls._params_to_tuple(**all_params)
        data = cls._cached_shape("text", params_tuple)
        return GeometryAPI(data)

    @classmethod
    def asemic_glyph(cls, **params) -> GeometryAPI:
        """抽象グリフを生成。

        Args:
            **params: パラメータ

        Returns:
            GeometryAPI: 生成された抽象グリフ
        """
        params_tuple = cls._params_to_tuple(**params)
        data = cls._cached_shape("asemic_glyph", params_tuple)
        return GeometryAPI(data)

    # === ユーザー拡張 ===

    @staticmethod
    def from_lines(lines: Sequence[Union[np.ndarray, List]]) -> GeometryAPI:
        """線分リストから形状を作成。

        Args:
            lines: 線分のリスト

        Returns:
            GeometryAPI: 作成された形状
        """
        return GeometryAPI.from_lines(lines)

    @staticmethod
    def empty() -> GeometryAPI:
        """空の形状を作成。

        Returns:
            GeometryAPI: 空の形状
        """
        return GeometryAPI.empty()

    # === キャッシュ管理 ===

    @classmethod
    def clear_cache(cls):
        """形状キャッシュをクリア。"""
        cls._cached_shape.cache_clear()

    @classmethod
    def cache_info(cls):
        """キャッシュ情報を取得。"""
        return cls._cached_shape.cache_info()


# シングルトンインスタンス（G）
G = ShapeFactory()
