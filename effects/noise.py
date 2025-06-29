from __future__ import annotations

import numpy as np
from numba import njit

from engine.core.geometry import Geometry
from util.constants import NOISE_CONST

from .base import BaseEffect


@njit(fastmath=True, cache=True)
def fade(t):
    """Perlinノイズ用のフェード関数"""
    return t * t * t * (t * (t * 6 - 15) + 10)


@njit(fastmath=True, cache=True)
def lerp(a, b, t):
    """線形補間"""
    return a + t * (b - a)


@njit(fastmath=True, cache=True)
def grad(hash_val, x, y, z, grad3_array):
    """勾配ベクトル計算"""
    # 安全なインデックスアクセス
    idx = int(hash_val) % 12
    g = grad3_array[idx]
    return g[0] * x + g[1] * y + g[2] * z


@njit(fastmath=True, cache=True)
def perlin_noise_3d(x, y, z, perm_table, grad3_array):
    """3次元Perlinノイズ生成"""
    # セル空間上の位置を求める
    X = int(np.floor(x)) & 255
    Y = int(np.floor(y)) & 255
    Z = int(np.floor(z)) & 255

    # 内部点（小数部分）
    x -= np.floor(x)
    y -= np.floor(y)
    z -= np.floor(z)

    # フェード関数
    u = fade(x)
    v = fade(y)
    w = fade(z)

    # Numba最適化：配列長は定数として扱う
    perm_len = perm_table.shape[0]

    A = perm_table[X] + Y
    AA = perm_table[A & 511] + Z  # 511 = 2*256-1
    AB = perm_table[(A + 1) & 511] + Z
    B = perm_table[(X + 1) & 255] + Y
    BA = perm_table[B & 511] + Z
    BB = perm_table[(B + 1) & 511] + Z

    # 8つのコーナーでのグラディエントドット
    gAA = grad(perm_table[AA & 511], x, y, z, grad3_array)
    gBA = grad(perm_table[BA & 511], x - 1, y, z, grad3_array)
    gAB = grad(perm_table[AB & 511], x, y - 1, z, grad3_array)
    gBB = grad(perm_table[BB & 511], x - 1, y - 1, z, grad3_array)
    gAA1 = grad(perm_table[(AA + 1) & 511], x, y, z - 1, grad3_array)
    gBA1 = grad(perm_table[(BA + 1) & 511], x - 1, y, z - 1, grad3_array)
    gAB1 = grad(perm_table[(AB + 1) & 511], x, y - 1, z - 1, grad3_array)
    gBB1 = grad(perm_table[(BB + 1) & 511], x - 1, y - 1, z - 1, grad3_array)

    # trilinear補間
    return lerp(lerp(lerp(gAA, gBA, u), lerp(gAB, gBB, u), v), lerp(lerp(gAA1, gBA1, u), lerp(gAB1, gBB1, u), v), w)


@njit(fastmath=True, cache=True)
def perlin_core(vertices: np.ndarray, frequency: tuple, perm_table: np.ndarray, grad3_array: np.ndarray):
    """コア Perlin ノイズ計算（3次元頂点専用）"""
    n = vertices.shape[0]

    if n == 0:
        return np.zeros((0, 3), dtype=np.float32)

    result = np.zeros((n, 3), dtype=np.float32)
    for i in range(n):
        x, y, z = vertices[i, 0] * frequency[0], vertices[i, 1] * frequency[1], vertices[i, 2] * frequency[2]
        # 3成分のノイズをオフセットを変えて生成
        nx = perlin_noise_3d(x, y, z, perm_table, grad3_array)
        ny = perlin_noise_3d(x + 100.0, y + 100.0, z + 100.0, perm_table, grad3_array)
        nz = perlin_noise_3d(x + 200.0, y + 200.0, z + 200.0, perm_table, grad3_array)
        result[i, 0] = np.float32(nx)
        result[i, 1] = np.float32(ny)
        result[i, 2] = np.float32(nz)

    return result


@njit(fastmath=True, cache=True)
def _apply_noise_to_coords(
    coords: np.ndarray, intensity: float, frequency: tuple, t: float, perm_table: np.ndarray, grad3_array: np.ndarray
) -> np.ndarray:
    """座標配列にPerlinノイズを適用します。"""
    if coords.size == 0 or not intensity:
        return coords.copy()

    # 係数調整
    intensity = intensity * 10
    t_offset = np.float32(t * 0.01 + 1000.0)

    # オフセット付き頂点を作成
    offset_coords = coords + t_offset

    # Perlinノイズ計算
    noise_offset = perlin_core(
        offset_coords, (frequency[0] * 0.1, frequency[1] * 0.1, frequency[2] * 0.1), perm_table, grad3_array
    )

    return coords + noise_offset * np.float32(intensity)


# Perlinノイズ用のPermutationテーブルを作成
perm = np.array(NOISE_CONST["PERM"], dtype=np.int32)
perm = np.concatenate([perm, perm])  # 0-255までの順列を2回連結

# Perlinノイズで使用するグラディエントベクトル
grad3 = np.array(NOISE_CONST["GRAD3"], dtype=np.float32)


class Noise(BaseEffect):
    """3次元頂点にPerlinノイズを追加します。"""

    def apply(
        self,
        geometry: Geometry,
        intensity: float = 0.5,
        frequency: tuple | float = (0.5, 0.5, 0.5),
        t: float = 0.0,
        **params,
    ) -> Geometry:
        """GeometryにPerlinノイズエフェクトを適用します。

        Args:
            geometry: 入力Geometry
            intensity: ノイズの強度
            frequency: ノイズの周波数（tuple or float）
            t: 時間パラメータ
            **params: 追加パラメータ（BaseEffectとの互換性のため）

        Returns:
            Perlinノイズが適用されたGeometry
        """
        # 周波数の正規化
        if isinstance(frequency, (int, float)):
            frequency = (frequency, frequency, frequency)
        elif len(frequency) == 1:
            frequency = (frequency[0], frequency[0], frequency[0])

        # 座標にノイズを適用
        new_coords = _apply_noise_to_coords(geometry.coords, intensity, frequency, t, perm, grad3)
        
        # 新しいGeometryを作成して返す
        return Geometry(new_coords, geometry.offsets.copy())


# api.effects用のラッパー関数
def noise(
    geometry: Geometry,
    intensity: float = 0.5,
    frequency: tuple | float = (0.5, 0.5, 0.5),
    time: float = 0.0,
) -> Geometry:
    """GeometryにPerlinノイズを適用します。

    Args:
        geometry: 入力Geometry
        intensity: ノイズの強度 (0.0-1.0)
        frequency: ノイズの周波数
        time: 時間パラメータ

    Returns:
        ノイズが適用されたGeometry
    """
    effect = Noise()
    return effect.apply(geometry, intensity=intensity, frequency=frequency, t=time)