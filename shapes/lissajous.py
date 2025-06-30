from __future__ import annotations

from typing import Any

import numpy as np

from .registry import shape
from engine.core.geometry_data import GeometryData
from .base import BaseShape


@shape("lissajous")
class Lissajous(BaseShape):
    """Lissajous curve shape generator."""
    
    def generate(self, freq_x: float = 3.0, freq_y: float = 2.0, 
                phase: float = 0.0, points: int = 1000, **params: Any) -> GeometryData:
        """Generate a Lissajous curve.
        
        Args:
            freq_x: X-axis frequency
            freq_y: Y-axis frequency  
            phase: Phase offset in radians
            points: Number of points to generate
            **params: Additional parameters (ignored)
            
        Returns:
            GeometryData object containing the curve vertices
        """
        t = np.linspace(0, 2 * np.pi, points)
        
        x = np.sin(freq_x * t + phase) * 0.5
        y = np.sin(freq_y * t) * 0.5
        z = np.zeros_like(x)
        
        vertices = np.stack([x, y, z], axis=1).astype(np.float32)
        
        return GeometryData.from_lines([vertices])