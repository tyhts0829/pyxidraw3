from __future__ import annotations

from typing import Any

import numpy as np

from effects import (
    Array,
    Boldify,
    Buffer,
    Collapse,
    Connect,
    Culling,
    Dashify,
    Desolve,
    EffectPipeline,
    Extrude,
    Filling,
    Noise,
    Rotation,
    Scaling,
    Subdivision,
    Sweep,
    Transform,
    Translation,
    Trimming,
    Webify,
    Wobble,
)
from engine.core.geometry import Geometry

# def boldify(
#     vertices_list: list[np.ndarray],
#     boldness: float = 1.0,
#     **params: Any,
# ) -> list[np.ndarray]:
#     """平行線を追加してラインを太く見せます。

#     Args:
#         vertices_list: 入力頂点配列
#         offset: 太さ係数 (0.0-1.0、内部で0.1倍される)
#         num_offset: 適応的手法の密度制御
#         method: 実装手法 ("normal" または "adaptive")
#         **params: 追加パラメータ

#     Returns:
#         太字化された頂点配列
#     """
#     effect = Boldify()
#     return effect(vertices_list, offset=boldness, **params)


# def connect(
#     vertices_list: list[np.ndarray], n_points: float = 0.5, alpha: float = 0.0, cyclic: bool = False, **params: Any
# ) -> list[np.ndarray]:
#     """Catmull-Romスプラインを使用して複数の線を滑らかに接続します。

#     Args:
#         vertices_list: 入力頂点配列
#         n_points: 補間点の数 (0.0-1.0、0-50にマップ)
#         alpha: スプライン張力パラメータ (0.0-1.0、0-2にマップ)
#         cyclic: 最後の線を最初の線に接続するかどうか
#         **params: 追加パラメータ

#     Returns:
#         接続された頂点配列
#     """
#     effect = Connect()
#     return effect(vertices_list, n_points=n_points, alpha=alpha, cyclic=cyclic, **params)


def rotation(
    geometry: Geometry,
    center: tuple[float, float, float] = (0, 0, 0),
    rotate: tuple[float, float, float] = (0, 0, 0),
    **params: Any,
) -> Geometry:
    """指定した軸の周りで頂点を回転させます。

    Args:
        geometry: 入力Geometry
        center: 回転の中心点 (x, y, z)
        rotate: 各軸周りの回転角度（ラジアン）(x, y, z) 0.0-1.0の範囲を想定。内部でmath.tauを掛けてラジアンに変換される。
        **params: 追加パラメータ

    Returns:
        回転したGeometry
    """
    effect = Rotation()
    return effect(geometry, center=center, rotate=rotate, **params)


def scaling(
    geometry: Geometry,
    center: tuple[float, float, float] = (0, 0, 0),
    scale: tuple[float, float, float] = (1, 1, 1),
    **params: Any,
) -> Geometry:
    """指定した軸に沿って頂点をスケールします。

    Args:
        geometry: 入力Geometry
        center: スケーリングの中心点 (x, y, z)
        scale: 各軸のスケール係数 (x, y, z)
        **params: 追加パラメータ

    Returns:
        スケールされたGeometry
    """
    effect = Scaling()
    return effect(geometry, center=center, scale=scale, **params)


def translation(
    geometry: Geometry, offset_x: float = 0.0, offset_y: float = 0.0, offset_z: float = 0.0, **params: Any
) -> Geometry:
    """指定したオフセットで頂点を移動します。

    Args:
        geometry: 入力Geometry
        offset_x: X軸の移動オフセット
        offset_y: Y軸の移動オフセット
        offset_z: Z軸の移動オフセット
        **params: 追加パラメータ

    Returns:
        移動したGeometry
    """
    effect = Translation()
    return effect(geometry, offset_x=offset_x, offset_y=offset_y, offset_z=offset_z, **params)


# def dashify(
#     vertices_list: list[np.ndarray], dash_length: float = 0.1, gap_length: float = 0.05, **params: Any
# ) -> list[np.ndarray]:
#     """連続線を破線に変換します。

#     Args:
#         vertices_list: 入力頂点配列
#         dash_length: 各破線の長さ
#         gap_length: 破線間のギャップ長
#         **params: 追加パラメータ

#     Returns:
#         破線化された頂点配列
#     """
#     effect = Dashify()
#     return effect(vertices_list, dash_length=dash_length, gap_length=gap_length, **params)


def subdivision(geometry: Geometry, n_divisions: float = 0.5, **params: Any) -> Geometry:
    """中間点を追加して線を細分化します。

    Args:
        geometry: 入力Geometry
        n_divisions: 細分化レベル (0.0 = 変化なし, 1.0 = 最大分割) - デフォルト 0.5
        **params: 追加パラメータ

    Returns:
        細分化されたGeometry
    """
    effect = Subdivision()
    return effect(geometry, n_divisions=n_divisions, **params)


# def culling(
#     vertices_list: list[np.ndarray],
#     min_x: float = -1.0,
#     max_x: float = 1.0,
#     min_y: float = -1.0,
#     max_y: float = 1.0,
#     min_z: float = -1.0,
#     max_z: float = 1.0,
#     mode: str = "clip",
#     **params: Any,
# ) -> list[np.ndarray]:
#     """指定した範囲外の頂点を除去します。

#     Args:
#         vertices_list: 入力頂点配列
#         min_x, max_x: X軸の範囲
#         min_y, max_y: Y軸の範囲
#         min_z, max_z: Z軸の範囲
#         mode: "クリップ"で範囲で線を切り取り、"除去"で線全体を除去
#         **params: 追加パラメータ

#     Returns:
#         カリングされた頂点配列
#     """
#     effect = Culling()
#     return effect(
#         vertices_list, min_x=min_x, max_x=max_x, min_y=min_y, max_y=max_y, min_z=min_z, max_z=max_z, mode=mode, **params
#     )


# def wobble(
#     vertices_list: list[np.ndarray],
#     amplitude: float = 0.05,
#     frequency: float = 5.0,
#     phase: float = 0.0,
#     axis: str = "y",
#     **params: Any,
# ) -> list[np.ndarray]:
#     """線にワブル/波の歪みを追加します。

#     Args:
#         vertices_list: 入力頂点配列
#         amplitude: 波の振幅
#         frequency: 波の周波数
#         phase: 位相オフセット
#         axis: ワブルを適用する軸 ("x"、"y"、または "z")
#         **params: 追加パラメータ

#     Returns:
#         ワブルした頂点配列
#     """
#     effect = Wobble()
#     return effect(vertices_list, amplitude=amplitude, frequency=frequency, phase=phase, **params)


# def array(
#     vertices_list: list[np.ndarray],
#     n_duplicates: float = 0.5,
#     offset: tuple[float, float, float] = (0.0, 0.0, 0.0),
#     rotate: tuple[float, float, float] = (0.0, 0.0, 0.0),
#     scale: tuple[float, float, float] = (0.5, 0.5, 0.5),
#     center: tuple[float, float, float] = (0.0, 0.0, 0.0),
#     **params: Any,
# ) -> list[np.ndarray]:
#     """入力のコピーを配列状に生成します。

#     Args:
#         vertices_list: 入力頂点配列
#         n_duplicates: 複製数の係数（0.0-1.0、最大10個まで）
#         intervals: 各複製間のオフセット（x, y, z）
#         rotate: 各複製における回転角度の増分（x, y, z軸、ラジアン）
#         scale: 各複製におけるスケールの縮小率（1.0で縮小なし）
#         **params: 追加パラメータ

#     Returns:
#         配列化された頂点配列
#     """
#     effect = Array()
#     return effect(
#         vertices_list,
#         n_duplicates=n_duplicates,
#         offset=offset,
#         rotate=rotate,
#         scale=scale,
#         center=center,
#         **params,
#     )


# def sweep(
#     vertices_list: list[np.ndarray], path: np.ndarray | None = None, profile: np.ndarray | None = None, **params: Any
# ) -> list[np.ndarray]:
#     """パスに沿ってプロファイルをスイープします。

#     Args:
#         vertices_list: 入力頂点配列（pathが提供されない場合はパスとして使用）
#         path: スイープするパス
#         profile: スイープするプロファイル（Noneの場合はシンプルな円形プロファイルを使用）
#         **params: 追加パラメータ

#     Returns:
#         スイープされた頂点配列
#     """
#     effect = Sweep()
#     return effect(vertices_list, path=path, profile=profile, **params)


def extrude(
    geometry: Geometry,
    direction: tuple[float, float, float] = (0.0, 0.0, 1.0),
    distance: float = 0.5,
    scale: float = 0.5,
    subdivisions: float = 0.5,
    **params: Any,
) -> Geometry:
    """2D形状を3Dに押し出します。

    Args:
        geometry: 入力Geometry
        direction: 押し出し方向ベクトル (x, y, z) - デフォルト (0, 0, 1)
        distance: 押し出し距離 (0.0-1.0) - デフォルト 0.5
        scale: 押し出したジオメトリのスケール率 (0.0-1.0) - デフォルト 0.5
        subdivisions: 細分化ステップ数 (0.0-1.0) - デフォルト 0.5
        **params: 追加パラメータ

    Returns:
        押し出しされたGeometry
    """
    effect = Extrude()
    return effect(geometry, direction=direction, distance=distance, scale=scale, subdivisions=subdivisions, **params)


def filling(
    geometry: Geometry, 
    pattern: str = "lines", 
    density: float = 0.5, 
    angle: float = 0.0, 
    **params: Any
) -> Geometry:
    """ハッチングパターンで閉じた形状を塗りつぶします。

    Args:
        geometry: 入力Geometry（閉じた形状を形成する必要があります）
        pattern: 塗りつぶしパターンタイプ ("lines"、"cross"、"dots") - デフォルト "lines"
        density: 塗りつぶしの密度 (0.0-1.0) - デフォルト 0.5
        angle: パターンの角度（ラジアン） - デフォルト 0.0
        **params: 追加パラメータ

    Returns:
        塗りつぶしされたGeometry
    """
    effect = Filling()
    return effect(geometry, pattern=pattern, density=density, angle=angle, **params)


# def trimming(
#     vertices_list: list[np.ndarray], start_param: float = 0.0, end_param: float = 1.0, **params: Any
# ) -> list[np.ndarray]:
#     """指定したパラメータ範囲で線をトリムします。

#     Args:
#         vertices_list: 入力頂点配列
#         start_param: 開始パラメータ（0.0 = 線の開始点）
#         end_param: 終了パラメータ（1.0 = 線の終点）
#         **params: 追加パラメータ

#     Returns:
#         トリムされた頂点配列
#     """
#     effect = Trimming()
#     return effect(vertices_list, start_param=start_param, end_param=end_param, **params)


# def webify(
#     vertices_list: list[np.ndarray], connection_probability: float = 0.5, max_distance: float = 1.0, **params: Any
# ) -> list[np.ndarray]:
#     """頂点間にウェブ状の接続を作成します。

#     Args:
#         vertices_list: 入力頂点配列
#         connection_probability: 近くの頂点を接続する確率
#         max_distance: 接続の最大距離
#         **params: 追加パラメータ

#     Returns:
#         ウェブ化された頂点配列
#     """
#     effect = Webify()
#     return effect(vertices_list, connection_probability=connection_probability, max_distance=max_distance, **params)


# def desolve(
#     vertices_list: list[np.ndarray], factor: float = 0.5, seed: int | None = None, **params: Any
# ) -> list[np.ndarray]:
#     """線をランダムに溶解/断片化します。

#     Args:
#         vertices_list: 入力頂点配列
#         factor: 溶解係数 (0.0 = 変化なし1.0 = 最大溶解)
#         seed: 再現性のためのランダムシード
#         **params: 追加パラメータ

#     Returns:
#         溶解された頂点配列
#     """
#     effect = Desolve()
#     return effect(vertices_list, factor=factor, seed=seed, **params)


# def collapse(
#     vertices_list: list[np.ndarray],
#     intensity: float = 0.5,
#     n_divisions: float = 0.5,
#     **params: Any,
# ) -> list[np.ndarray]:
#     """頂点を中心点に向かって崩壊させます。

#     Args:
#         vertices_list: 入力頂点配列
#         **params: 追加パラメータ

#     Returns:
#         崩壊された頂点配列
#     """
#     effect = Collapse()
#     return effect(vertices_list, intensity=intensity, n_divisions=n_divisions, **params)


def transform(
    geometry: Geometry,
    center: tuple[float, float, float] = (0, 0, 0),
    scale: tuple[float, float, float] = (1, 1, 1),
    rotate: tuple[float, float, float] = (0, 0, 0),
    **params: Any,
) -> Geometry:
    """任意の変換行列を適用します。

    Args:
        geometry: 入力Geometry
        center: 中心点
        scale: スケール
        rotate: 回転
        **params: 追加パラメータ

    Returns:
        変換されたGeometry
    """
    effect = Transform()
    return effect(geometry, center=center, scale=scale, rotate=rotate, **params)


def noise(
    geometry: Geometry,
    intensity: float = 0.5,
    frequency: tuple[float, float, float] | float = (0.5, 0.5, 0.5),
    time: float = 0.0,
    **params: Any,
) -> Geometry:
    """GeometryにPerlinノイズを適用します。

    Args:
        geometry: 入力Geometry
        intensity: ノイズの強度 (0.0-1.0)
        frequency: ノイズの周波数（tuple or float）
        time: 時間パラメータ
        **params: 追加パラメータ

    Returns:
        ノイズが適用されたGeometry
    """
    effect = Noise()
    return effect.apply(geometry, intensity=intensity, frequency=frequency, t=time, **params)


def buffer(
    geometry: Geometry, 
    distance: float = 0.5, 
    join_style: float = 0.5, 
    resolution: float = 0.5,
    **params: Any
) -> Geometry:
    """パスの周りにバッファ/オフセットを作成します。

    Args:
        geometry: 入力Geometry
        distance: バッファ距離 (0.0-1.0、内部で25倍される) - デフォルト 0.5
        join_style: 角の接合スタイル (0.0-1.0でround/mitre/bevelを選択) - デフォルト 0.5
        resolution: バッファーの解像度 (0.0-1.0で1-10の整数値に変換) - デフォルト 0.5
        **params: 追加パラメータ

    Returns:
        バッファされたGeometry
    """
    effect = Buffer()
    return effect(geometry, distance=distance, join_style=join_style, resolution=resolution, **params)


def array(
    geometry: Geometry,
    n_duplicates: float = 0.5,
    offset: tuple[float, float, float] = (0.0, 0.0, 0.0),
    rotate: tuple[float, float, float] = (0.5, 0.5, 0.5),
    scale: tuple[float, float, float] = (0.5, 0.5, 0.5),
    center: tuple[float, float, float] = (0.0, 0.0, 0.0),
    **params: Any,
) -> Geometry:
    """入力のコピーを配列状に生成します。

    Args:
        geometry: 入力Geometry
        n_duplicates: 複製数の係数（0.0-1.0、最大10個まで）- デフォルト 0.5
        offset: 各複製間のオフセット（x, y, z）- デフォルト (0.0, 0.0, 0.0)
        rotate: 各複製における回転増分（0.0-1.0、0.5が中立）- デフォルト (0.5, 0.5, 0.5)
        scale: 各複製におけるスケール係数（0.0-1.0、0.5が中立）- デフォルト (0.5, 0.5, 0.5)
        center: 配列の中心点（x, y, z）- デフォルト (0.0, 0.0, 0.0)
        **params: 追加パラメータ

    Returns:
        配列化されたGeometry
    """
    effect = Array()
    return effect(
        geometry,
        n_duplicates=n_duplicates,
        offset=offset,
        rotate=rotate,
        scale=scale,
        center=center,
        **params,
    )


# 便利なパイプライン関数を作成
def pipeline(*effects: Any) -> EffectPipeline:
    """エフェクトパイプラインを作成します。

    Args:
        *effects: パイプラインに追加するエフェクトインスタンス

    Returns:
        EffectPipelineインスタンス
    """
    return EffectPipeline(effects)
