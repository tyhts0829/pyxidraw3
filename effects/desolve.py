from __future__ import annotations

from typing import Any

import numpy as np

from engine.core.geometry import Geometry

from .base import BaseEffect
from .registry import effect


@effect("desolve")
class Desolve(BaseEffect):
    """線を個別のセグメントに分解/分割します。"""
    
    def apply(self, coords: np.ndarray, offsets: np.ndarray, **params: Any) -> tuple[np.ndarray, np.ndarray]:
        """分解エフェクトを適用します。
        
        連続したポリラインを個別の線セグメントに分割します。
        
        Args:
            coords: 入力座標配列
            offsets: 入力オフセット配列
            factor: 分解率 (0.0-1.0) - ランダム性を制御（基本実装では使用しない）
            seed: 再現可能性のためのランダムシード（基本実装では使用しない）
            **params: 追加パラメータ
            
        Returns:
            (desolve_coords, desolve_offsets): 個別の線セグメントに分割された座標配列とオフセット配列
        """
        factor = params.get('factor', 0.5)
        seed = params.get('seed', None)
        
        # エッジケース: 空の座標配列
        if len(coords) == 0:
            return coords.copy(), offsets.copy()

        # 座標配列をGeometryに変換してから頂点リストに変換
        geometry = Geometry(coords, offsets)
        vertices_list = []
        for i in range(len(geometry.offsets) - 1):
            start_idx = geometry.offsets[i]
            end_idx = geometry.offsets[i + 1]
            line = geometry.coords[start_idx:end_idx]
            vertices_list.append(line)

        new_vertices_list = []
        
        for vertices in vertices_list:
            dissolved_segments = self._desolve_core(vertices, factor, seed)
            new_vertices_list.extend(dissolved_segments)
        
        # 結果をGeometryに変換してから座標とオフセットに戻す
        if not new_vertices_list:
            return coords.copy(), offsets.copy()
        
        result_geometry = Geometry.from_lines(new_vertices_list)
        return result_geometry.coords, result_geometry.offsets
    
    def _desolve_core(self, vertices: np.ndarray, factor: float, seed: int | None) -> list[np.ndarray]:
        """ポリラインを個別の線セグメントに分割します。
        
        Args:
            vertices: ポリラインを形成する(N, 3)の頂点配列
            factor: 分解率（現在未使用、将来の拡張用）
            seed: ランダムシード（現在未使用、将来の拡張用）
            
        Returns:
            (2, 3)配列のリスト、各配列は1つの線セグメントを表す
        """
        # If vertices has 2 or fewer points, return as is
        if len(vertices) <= 2:
            return [vertices]
        
        # Break polyline into individual segments
        segments = []
        for i in range(len(vertices) - 1):
            segment = vertices[i:i+2].copy()
            segments.append(segment)
        
        return segments