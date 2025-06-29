from __future__ import annotations

from typing import Any

import numpy as np

from .base import BaseShape
from engine.core.geometry_data import GeometryData


def cylinder_data(radius: float = 0.3, height: float = 0.6, segments: int = 32, center=(0, 0, 0), **params) -> GeometryData:
    """GeometryDataを直接返すcylinder生成関数（API層に依存しない）。
    
    Args:
        radius: 円柱の半径
        height: 円柱の高さ
        segments: 周囲のセグメント数
        center: 中心点
        **params: 追加パラメータ
        
    Returns:
        GeometryData: 生成された円柱データ
    """
    vertices_list = []
    
    # 上下の円を生成
    angles = np.linspace(0, 2 * np.pi, segments + 1)
    
    # 上の円
    top_circle = []
    for angle in angles:
        x = radius * np.cos(angle)
        y = radius * np.sin(angle)
        z = height / 2
        top_circle.append([x, y, z])
    vertices_list.append(np.array(top_circle, dtype=np.float32))
    
    # 下の円
    bottom_circle = []
    for angle in angles:
        x = radius * np.cos(angle)
        y = radius * np.sin(angle)
        z = -height / 2
        bottom_circle.append([x, y, z])
    vertices_list.append(np.array(bottom_circle, dtype=np.float32))
    
    # 垂直線
    for i in range(segments):
        angle = 2 * np.pi * i / segments
        x = radius * np.cos(angle)
        y = radius * np.sin(angle)
        
        vertical_line = np.array([
            [x, y, -height / 2],
            [x, y, height / 2]
        ], dtype=np.float32)
        vertices_list.append(vertical_line)
    
    # 中心を適用
    if center != (0, 0, 0):
        center_array = np.asarray(center, dtype=np.float32)
        for i, vertices in enumerate(vertices_list):
            vertices_list[i] = vertices + center_array
    
    return GeometryData.from_lines(vertices_list)


class Cylinder(BaseShape):
    """Cylinder shape generator."""
    
    def generate(self, radius: float = 0.3, height: float = 0.6, 
                segments: int = 32, **params: Any) -> GeometryData:
        """Generate a cylinder.
        
        Args:
            radius: Cylinder radius
            height: Cylinder height
            segments: Number of segments around circumference
            **params: Additional parameters (ignored)
            
        Returns:
            GeometryData object containing cylinder lines
        """
        vertices_list = []
        
        # Generate top and bottom circles
        angles = np.linspace(0, 2 * np.pi, segments + 1)
        
        # Top circle
        top_circle = []
        for angle in angles:
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            z = height / 2
            top_circle.append([x, y, z])
        vertices_list.append(np.array(top_circle, dtype=np.float32))
        
        # Bottom circle
        bottom_circle = []
        for angle in angles:
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            z = -height / 2
            bottom_circle.append([x, y, z])
        vertices_list.append(np.array(bottom_circle, dtype=np.float32))
        
        # Vertical lines
        for i in range(segments):
            angle = 2 * np.pi * i / segments
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            
            vertical_line = np.array([
                [x, y, -height / 2],
                [x, y, height / 2]
            ], dtype=np.float32)
            vertices_list.append(vertical_line)
        
        return GeometryData.from_lines(vertices_list)