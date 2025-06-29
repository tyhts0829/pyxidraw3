from __future__ import annotations

from typing import Any

import numpy as np

from .base import BaseEffect


class Dashify(BaseEffect):
    """連続線を破線に変換します。"""
    
    def apply(self, vertices_list: list[np.ndarray],
             dash_length: float = 0.1,
             gap_length: float = 0.05,
             **params: Any) -> list[np.ndarray]:
        """破線化エフェクトを適用します。
        
        Args:
            vertices_list: 入力頂点配列
            dash_length: 各ダッシュの長さ
            gap_length: ダッシュ間のギャップの長さ
            **params: 追加パラメータ（無視される）
            
        Returns:
            破線化された頂点配列
        """
        new_vertices_list = []
        pattern_length = dash_length + gap_length
        
        for vertices in vertices_list:
            if len(vertices) < 2:
                new_vertices_list.append(vertices)
                continue
            
            # Calculate cumulative distances
            segments = vertices[1:] - vertices[:-1]
            distances = np.sqrt(np.sum(segments ** 2, axis=1))
            cumulative_distances = np.concatenate([[0], np.cumsum(distances)])
            total_length = cumulative_distances[-1]
            
            if total_length <= 0:
                new_vertices_list.append(vertices)
                continue
            
            # Generate dashes
            current_distance = 0
            while current_distance < total_length:
                # Find start point of dash
                start_distance = current_distance
                end_distance = min(current_distance + dash_length, total_length)
                
                # Interpolate vertices for this dash
                dash_vertices = self._interpolate_segment(
                    vertices, cumulative_distances, start_distance, end_distance
                )
                
                if len(dash_vertices) > 1:
                    new_vertices_list.append(dash_vertices)
                
                current_distance += pattern_length
        
        return new_vertices_list
    
    def _interpolate_segment(self, vertices: np.ndarray, cumulative_distances: np.ndarray,
                           start_dist: float, end_dist: float) -> np.ndarray:
        """線上の2つの距離間で頂点を補間します。"""
        # Find indices
        start_idx = np.searchsorted(cumulative_distances, start_dist)
        end_idx = np.searchsorted(cumulative_distances, end_dist)
        
        if start_idx >= len(vertices):
            return np.array([], dtype=np.float32).reshape(0, 3)
        
        # Interpolate start point
        if start_idx > 0 and start_dist > cumulative_distances[start_idx - 1]:
            t = (start_dist - cumulative_distances[start_idx - 1]) / \
                (cumulative_distances[start_idx] - cumulative_distances[start_idx - 1])
            start_point = vertices[start_idx - 1] + t * (vertices[start_idx] - vertices[start_idx - 1])
        else:
            start_point = vertices[start_idx]
        
        # Interpolate end point
        if end_idx > 0 and end_idx < len(vertices) and end_dist < cumulative_distances[end_idx]:
            t = (end_dist - cumulative_distances[end_idx - 1]) / \
                (cumulative_distances[end_idx] - cumulative_distances[end_idx - 1])
            end_point = vertices[end_idx - 1] + t * (vertices[end_idx] - vertices[end_idx - 1])
        else:
            end_point = vertices[min(end_idx, len(vertices) - 1)]
        
        # Collect intermediate vertices
        if start_idx == end_idx:
            return np.array([start_point, end_point], dtype=np.float32)
        else:
            intermediate = vertices[start_idx:end_idx]
            if len(intermediate) == 0:
                return np.array([start_point, end_point], dtype=np.float32)
            return np.vstack([start_point[np.newaxis, :], intermediate, end_point[np.newaxis, :]]).astype(np.float32)