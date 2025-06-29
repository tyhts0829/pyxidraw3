from __future__ import annotations

from typing import Any

import numpy as np
from numba import njit

from engine.core.geometry import Geometry

from .base import BaseEffect


class Subdivision(BaseEffect):
    """中間点を追加して線を細分化します。"""

    MAX_DIVISIONS = 10  # 最大分割回数

    def apply(self, geometry: Geometry, n_divisions: float = 0.5, **_params: Any) -> Geometry:
        """細分化エフェクトを適用します。

        Args:
            geometry: 入力Geometryオブジェクト
            n_divisions: 細分化レベル (0.0 = 変化なし, 1.0 = 最大分割) - デフォルト 0.5
            **_params: 追加パラメータ（無視される）

        Returns:
            細分化されたGeometry
        """
        if n_divisions <= 0.0:
            return geometry

        # Convert 0.0-1.0 to 0-MAX_DIVISIONS
        divisions = int(n_divisions * self.MAX_DIVISIONS)
        if divisions <= 0:
            return geometry

        # 既存の線を取得し、細分化を適用
        coords, offsets = geometry.as_arrays()
        result = []
        
        for i in range(len(offsets) - 1):
            vertices = coords[offsets[i]:offsets[i+1]]
            subdivided = _subdivide_core(vertices, divisions)
            result.append(subdivided)

        return Geometry.from_lines(result)


@njit(fastmath=True, cache=True)
def _subdivide_core(vertices: np.ndarray, n_divisions: int) -> np.ndarray:
    """単一頂点配列の細分化処理（Numba最適化）"""
    if len(vertices) < 2 or n_divisions <= 0:
        return vertices

    # 最小長チェック - 短すぎる線分は分割しない
    MIN_LENGTH = 0.01
    if np.linalg.norm(vertices[0] - vertices[1]) < MIN_LENGTH:
        return vertices

    # 分割回数制限 - フリーズ防止
    MAX_DIVISIONS = 10
    n_divisions = min(n_divisions, MAX_DIVISIONS)

    result = vertices.copy()
    for _ in range(n_divisions):
        n = len(result)
        new_vertices = np.zeros((2 * n - 1, result.shape[1]), dtype=result.dtype)

        # 偶数インデックスに元の頂点を配置
        new_vertices[::2] = result

        # 奇数インデックスに中点を配置
        new_vertices[1::2] = (result[:-1] + result[1:]) / 2

        result = new_vertices

        # 再度最小長チェック
        if len(result) >= 2 and np.linalg.norm(result[0] - result[1]) < MIN_LENGTH:
            break

    return result
