from __future__ import annotations

from typing import Any

import numpy as np

from .base import BaseShape
from engine.core.geometry_data import GeometryData
from api.shape_registry import register_shape




@register_shape("cone")
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