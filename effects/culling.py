from __future__ import annotations

from typing import Any

import numpy as np

from engine.core.geometry import Geometry

from .base import BaseEffect
from .registry import effect


@effect("culling")
class Culling(BaseEffect):
    """指定された範囲外の頂点を除去します。"""
    
    def apply(self, coords: np.ndarray, offsets: np.ndarray,
             min_x: float = -1.0, max_x: float = 1.0,
             min_y: float = -1.0, max_y: float = 1.0,
             min_z: float = -1.0, max_z: float = 1.0,
             mode: str = "clip",
             **params: Any) -> tuple[np.ndarray, np.ndarray]:
        """カリングエフェクトを適用します。
        
        Args:
            coords: 入力座標配列
            offsets: 入力オフセット配列
            min_x, max_x: X軸の範囲
            min_y, max_y: Y軸の範囲
            min_z, max_z: Z軸の範囲
            mode: 線を範囲でクリップする"clip"、線全体を除去する"remove"
            **params: 追加パラメータ（無視される）
            
        Returns:
            (culled_coords, culled_offsets): カリングされた座標配列とオフセット配列
        """
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
            if len(vertices) == 0:
                continue
            
            if mode == "remove":
                # Check if any vertex is outside bounds
                in_bounds = (
                    (vertices[:, 0] >= min_x) & (vertices[:, 0] <= max_x) &
                    (vertices[:, 1] >= min_y) & (vertices[:, 1] <= max_y) &
                    (vertices[:, 2] >= min_z) & (vertices[:, 2] <= max_z)
                )
                if np.all(in_bounds):
                    new_vertices_list.append(vertices)
            else:  # clip mode
                # Clip vertices to bounds
                clipped = self._clip_line_to_bounds(
                    vertices, min_x, max_x, min_y, max_y, min_z, max_z
                )
                if len(clipped) > 0:
                    new_vertices_list.append(clipped)
        
        # 結果をGeometryに変換してから座標とオフセットに戻す
        if not new_vertices_list:
            return coords.copy(), offsets.copy()
        
        result_geometry = Geometry.from_lines(new_vertices_list)
        return result_geometry.coords, result_geometry.offsets
    
    def _clip_line_to_bounds(self, vertices: np.ndarray,
                            min_x: float, max_x: float,
                            min_y: float, max_y: float,
                            min_z: float, max_z: float) -> np.ndarray:
        """指定された範囲に線をクリップします。"""
        # For simplicity, just clamp vertices to bounds
        # A more sophisticated implementation would compute intersections
        clipped = vertices.copy()
        clipped[:, 0] = np.clip(clipped[:, 0], min_x, max_x)
        clipped[:, 1] = np.clip(clipped[:, 1], min_y, max_y)
        clipped[:, 2] = np.clip(clipped[:, 2], min_z, max_z)
        
        # Remove duplicate consecutive vertices
        if len(clipped) > 1:
            diff = np.sum(np.abs(clipped[1:] - clipped[:-1]), axis=1)
            mask = np.concatenate([[True], diff > 1e-6])
            clipped = clipped[mask]
        
        return clipped.astype(np.float32)