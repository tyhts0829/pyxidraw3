from __future__ import annotations

from typing import Any

import numpy as np

from .base import BaseEffect


class Trimming(BaseEffect):
    """線を指定されたパラメータ範囲にトリミングします。"""
    
    def apply(self, vertices_list: list[np.ndarray], **params: Any) -> list[np.ndarray]:
        """トリミングエフェクトを適用します。
        
        指定された開始と終了パラメータに線をトリミングします。
        
        Args:
            vertices_list: 入力頂点配列
            start_param: 開始パラメータ (0.0 = 開始) - デフォルト 0.0
            end_param: 終了パラメータ (1.0 = 終了) - デフォルト 1.0
            **params: 追加パラメータ
            
        Returns:
            トリミングされた頂点配列
        """
        start_param = params.get('start_param', 0.0)
        end_param = params.get('end_param', 1.0)
        
        # Clamp parameters to valid range
        start_param = max(0.0, min(1.0, start_param))
        end_param = max(0.0, min(1.0, end_param))
        
        if start_param >= end_param:
            return []
        
        trimmed_results = []
        
        for vertices in vertices_list:
            if len(vertices) < 2:
                trimmed_results.append(vertices)
                continue
            
            trimmed = self._trim_path(vertices, start_param, end_param)
            if trimmed is not None and len(trimmed) >= 2:
                trimmed_results.append(trimmed)
        
        return trimmed_results
    
    def _trim_path(self, vertices: np.ndarray, start_param: float, end_param: float) -> np.ndarray | None:
        """単一のパスを指定されたパラメータ範囲にトリミングします。"""
        if len(vertices) < 2:
            return vertices
        
        # Calculate cumulative distances along path
        distances = [0.0]
        for i in range(len(vertices) - 1):
            dist = np.linalg.norm(vertices[i + 1] - vertices[i])
            distances.append(distances[-1] + dist)
        
        total_length = distances[-1]
        if total_length == 0:
            return vertices
        
        # Convert parameters to actual distances
        start_dist = start_param * total_length
        end_dist = end_param * total_length
        
        # Find trimmed vertices
        trimmed_vertices = []
        
        # Add start point if needed
        start_point = self._interpolate_at_distance(vertices, distances, start_dist)
        if start_point is not None:
            trimmed_vertices.append(start_point)
        
        # Add intermediate vertices
        for i, dist in enumerate(distances):
            if start_dist < dist < end_dist:
                trimmed_vertices.append(vertices[i])
        
        # Add end point if needed
        end_point = self._interpolate_at_distance(vertices, distances, end_dist)
        if end_point is not None and not np.allclose(trimmed_vertices[-1], end_point) if trimmed_vertices else True:
            trimmed_vertices.append(end_point)
        
        return np.array(trimmed_vertices) if len(trimmed_vertices) >= 2 else None
    
    def _interpolate_at_distance(self, vertices: np.ndarray, distances: list[float], target_dist: float) -> np.ndarray | None:
        """パス上の特定距離で点を補間します。"""
        if target_dist <= 0:
            return vertices[0]
        if target_dist >= distances[-1]:
            return vertices[-1]
        
        # Find segment containing target distance
        for i in range(len(distances) - 1):
            if distances[i] <= target_dist <= distances[i + 1]:
                # Interpolate within this segment
                segment_start = distances[i]
                segment_end = distances[i + 1]
                segment_length = segment_end - segment_start
                
                if segment_length == 0:
                    return vertices[i]
                
                t = (target_dist - segment_start) / segment_length
                return vertices[i] + t * (vertices[i + 1] - vertices[i])
        
        return None