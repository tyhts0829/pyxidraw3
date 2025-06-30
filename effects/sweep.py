from __future__ import annotations

from typing import Any

import numpy as np

from engine.core.geometry import Geometry

from .base import BaseEffect
from .registry import effect


@effect("sweep")
class Sweep(BaseEffect):
    """頂点リストから重複した線セグメントを除去します。"""
    
    def apply(self, coords: np.ndarray, offsets: np.ndarray, **params: Any) -> tuple[np.ndarray, np.ndarray]:
        """スイープエフェクトを適用します。
        
        すべての頂点配列から重複した線セグメントを除去します。
        これは重なり合うジオメトリのクリーンアップに有用です。
        
        Args:
            coords: 入力座標配列
            offsets: 入力オフセット配列
            path: スイープするパス（現在の実装では未使用）
            profile: スイープするプロファイル（現在の実装では未使用）
            **params: 追加パラメータ
            
        Returns:
            (swept_coords, swept_offsets): 重複した線セグメントが除去された座標配列とオフセット配列
        """
        path = params.get('path', None)
        profile = params.get('profile', None)
        
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

        # For now, implement the duplicate removal functionality
        # Future versions could implement actual profile sweeping
        new_vertices_list = self._remove_duplicate_segments(vertices_list)
        
        # 結果をGeometryに変換してから座標とオフセットに戻す
        if not new_vertices_list:
            return coords.copy(), offsets.copy()
        
        result_geometry = Geometry.from_lines(new_vertices_list)
        return result_geometry.coords, result_geometry.offsets
    
    def _remove_duplicate_segments(self, vertices_list: list[np.ndarray]) -> list[np.ndarray]:
        """頂点リストから重複した線セグメントを除去します。
        
        Args:
            vertices_list: 頂点配列のリスト
            
        Returns:
            重複セグメントが除去された頂点配列のリスト
        """
        # Track seen segments to avoid duplicates
        # Use normalized tuple representation (smaller vertex first)
        seen_segments = set()
        new_vertices_list = []
        
        for vertices in vertices_list:
            # Skip if too few vertices to form line segments
            if len(vertices) < 2:
                new_vertices_list.append(vertices.copy())
                continue
            
            # Start with first vertex
            filtered_points = [vertices[0]]
            
            # Check each line segment
            for i in range(len(vertices) - 1):
                p = vertices[i]
                q = vertices[i + 1]
                
                # Create direction-independent segment key
                p_tuple = tuple(p.round(decimals=10))  # Round to avoid floating point issues
                q_tuple = tuple(q.round(decimals=10))
                segment_key = (p_tuple, q_tuple) if p_tuple <= q_tuple else (q_tuple, p_tuple)
                
                # If segment hasn't been seen before, add it
                if segment_key not in seen_segments:
                    seen_segments.add(segment_key)
                    filtered_points.append(q)
                # If segment is duplicate, skip adding the endpoint
                # This effectively removes the duplicate segment
            
            # Only add if we have at least 2 points (1 segment)
            if len(filtered_points) >= 2:
                new_vertices_list.append(np.array(filtered_points))
        
        return new_vertices_list