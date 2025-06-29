from __future__ import annotations

from typing import Any

import numpy as np

from .base import BaseShape
from engine.core.geometry_data import GeometryData


def cone_data(radius: float = 0.3, height: float = 0.6, segments: int = 32, center=(0, 0, 0), **params) -> GeometryData:
    """GeometryDataを直接返すcone生成関数（API層に依存しない）。
    
    Args:
        radius: 底面半径
        height: 円錐の高さ
        segments: 周囲のセグメント数
        center: 中心点
        **params: 追加パラメータ
        
    Returns:
        GeometryData: 生成された円錐データ
    """
    vertices_list = []
    
    # 底面の円
    angles = np.linspace(0, 2 * np.pi, segments + 1)
    base_circle = []
    for angle in angles:
        x = radius * np.cos(angle)
        y = radius * np.sin(angle)
        z = -height / 2
        base_circle.append([x, y, z])
    vertices_list.append(np.array(base_circle, dtype=np.float32))
    
    # 頂点から底面への線
    apex = np.array([0, 0, height / 2], dtype=np.float32)
    for i in range(segments):
        angle = 2 * np.pi * i / segments
        x = radius * np.cos(angle)
        y = radius * np.sin(angle)
        z = -height / 2
        
        line = np.array([
            apex,
            [x, y, z]
        ], dtype=np.float32)
        vertices_list.append(line)
    
    # 中心を適用
    if center != (0, 0, 0):
        center_array = np.asarray(center, dtype=np.float32)
        for i, vertices in enumerate(vertices_list):
            vertices_list[i] = vertices + center_array
    
    return GeometryData.from_lines(vertices_list)


class Cone(BaseShape):
    """Cone shape generator."""
    
    def generate(self, radius: float = 0.3, height: float = 0.6,
                segments: int = 32, **params: Any) -> GeometryData:
        """Generate a cone.
        
        Args:
            radius: Base radius
            height: Cone height
            segments: Number of segments around circumference
            **params: Additional parameters (ignored)
            
        Returns:
            GeometryData object containing cone lines
        """
        vertices_list = []
        
        # Base circle
        angles = np.linspace(0, 2 * np.pi, segments + 1)
        base_circle = []
        for angle in angles:
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            z = -height / 2
            base_circle.append([x, y, z])
        vertices_list.append(np.array(base_circle, dtype=np.float32))
        
        # Lines from apex to base
        apex = np.array([0, 0, height / 2], dtype=np.float32)
        for i in range(segments):
            angle = 2 * np.pi * i / segments
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            z = -height / 2
            
            line = np.array([
                apex,
                [x, y, z]
            ], dtype=np.float32)
            vertices_list.append(line)
        
        return GeometryData.from_lines(vertices_list)