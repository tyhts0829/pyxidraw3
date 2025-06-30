from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import numpy as np

from .registry import shape
from .base import BaseShape
from engine.core.geometry_data import GeometryData


@shape("attractor")
class Attractor(BaseShape):
    """Strange attractor shape generator."""

    def generate(
        self, attractor_type: str = "aizawa", points: int = 10000, dt: float = 0.01, scale: float = 1.0, **params: Any
    ) -> GeometryData:
        """Generate a strange attractor.

        Args:
            attractor_type: Type of attractor ("lorenz", "rossler", "aizawa", "three_scroll", "dejong")
            points: Number of points to generate
            dt: Time step for integration
            scale: Scale factor for the attractor
            **params: Additional parameters passed to specific attractors

        Returns:
            GeometryData object containing attractor trajectory
        """
        if attractor_type == "lorenz":
            attractor = LorenzAttractor(dt=dt, steps=points, scale=scale, **params)
        elif attractor_type == "rossler":
            attractor = RosslerAttractor(dt=dt, steps=points, scale=scale, **params)
        elif attractor_type == "aizawa":
            attractor = AizawaAttractor(dt=dt, steps=points, scale=scale, **params)
        elif attractor_type == "three_scroll":
            attractor = ThreeScrollAttractor(dt=dt, steps=points, scale=scale, **params)
        elif attractor_type == "dejong":
            attractor = DeJongAttractor(steps=points, scale=scale, **params)
        else:
            # Default to Lorenz
            attractor = LorenzAttractor(dt=dt, steps=points, scale=scale, **params)

        vertices = attractor.integrate()

        # Normalize to fit in unit cube if scale is 1.0
        if scale == 1.0:
            vertices = self._normalize_vertices(vertices)

        return GeometryData.from_lines([vertices])

    def _normalize_vertices(self, vertices: np.ndarray) -> np.ndarray:
        """Normalize vertices to fit in unit cube centered at origin."""
        # Find bounds
        min_vals = np.min(vertices, axis=0)
        max_vals = np.max(vertices, axis=0)

        # Center and scale
        center = (min_vals + max_vals) * 0.5
        scale = np.max(max_vals - min_vals)

        if scale > 0:
            normalized = (vertices - center) / scale
        else:
            normalized = vertices - center

        return normalized


class BaseAttractor(ABC):
    """Base class for all attractors to reduce code duplication."""
    
    def __init__(self, dt: float = 0.01, steps: int = 10000, scale: float = 1.0):
        self.dt = dt
        self.steps = steps
        self.scale = scale
    
    @abstractmethod
    def _derivatives(self, state: np.ndarray) -> np.ndarray:
        """Calculate derivatives for the attractor system."""
        pass
    
    @abstractmethod
    def _get_initial_state(self) -> np.ndarray:
        """Get default initial state for the attractor."""
        pass
    
    def integrate(self, initial_state: np.ndarray | None = None) -> np.ndarray:
        """Integrate the attractor using RK4 method."""
        if initial_state is None:
            state = self._get_initial_state()
        else:
            state = np.array(initial_state, dtype=np.float32)
        
        # Pre-allocate trajectory array
        trajectory = np.empty((self.steps, len(state)), dtype=np.float32)
        
        # Vectorized RK4 integration
        for i in range(self.steps):
            trajectory[i] = state
            k1 = self._derivatives(state)
            k2 = self._derivatives(state + 0.5 * self.dt * k1)
            k3 = self._derivatives(state + 0.5 * self.dt * k2)
            k4 = self._derivatives(state + self.dt * k3)
            state = state + (self.dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
        
        return trajectory * self.scale


class LorenzAttractor(BaseAttractor):
    def __init__(self, sigma=10.0, rho=28.0, beta=8 / 3, dt=0.01, steps=10000, scale=1.0):
        super().__init__(dt, steps, scale)
        self.sigma = sigma
        self.rho = rho
        self.beta = beta

    def _derivatives(self, state: np.ndarray) -> np.ndarray:
        x, y, z = state
        dx = self.sigma * (y - x)
        dy = x * (self.rho - z) - y
        dz = x * y - self.beta * z
        return np.array([dx, dy, dz], dtype=np.float32)
    
    def _get_initial_state(self) -> np.ndarray:
        return np.array([1.0, 1.0, 1.0], dtype=np.float32)


class RosslerAttractor(BaseAttractor):
    def __init__(self, a=0.2, b=0.2, c=5.7, dt=0.01, steps=10000, scale=1.0):
        super().__init__(dt, steps, scale)
        self.a = a
        self.b = b
        self.c = c

    def _derivatives(self, state: np.ndarray) -> np.ndarray:
        x, y, z = state
        dx = -y - z
        dy = x + self.a * y
        dz = self.b + z * (x - self.c)
        return np.array([dx, dy, dz], dtype=np.float32)
    
    def _get_initial_state(self) -> np.ndarray:
        return np.array([0.0, 0.0, 0.0], dtype=np.float32)


class AizawaAttractor(BaseAttractor):
    def __init__(self, a=0.95, b=0.7, c=0.6, d=3.5, dt=0.01, steps=10000, scale=1.0):
        super().__init__(dt, steps, scale)
        self.a = a
        self.b = b
        self.c = c
        self.d = d

    def _derivatives(self, state: np.ndarray) -> np.ndarray:
        x, y, z = state
        dx = (z - self.b) * x - self.d * y
        dy = self.d * x + (z - self.b) * y
        dz = self.c - self.a * z - z * (x**2 + y**2)
        return np.array([dx, dy, dz], dtype=np.float32)
    
    def _get_initial_state(self) -> np.ndarray:
        return np.array([0.1, 0.0, 0.0], dtype=np.float32)


class ThreeScrollAttractor(BaseAttractor):
    def __init__(self, a=40, b=0.833, c=0.5, d=0.5, e=0.65, dt=0.01, steps=10000, scale=1.0):
        super().__init__(dt, steps, scale)
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.e = e

    def _derivatives(self, state: np.ndarray) -> np.ndarray:
        x, y, z = state
        dx = self.a * (y - x) + self.d * x * z
        dy = self.b * x - x * z + self.c * y
        dz = self.e * z + x * y
        return np.array([dx, dy, dz], dtype=np.float32)
    
    def _get_initial_state(self) -> np.ndarray:
        return np.array([0.1, 0.0, 0.0], dtype=np.float32)


class DeJongAttractor:
    def __init__(self, a=1.4, b=-2.3, c=2.4, d=-2.1, steps=10000, scale=1.0, initial_state=(0, 0)):
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.steps = steps
        self.scale = scale
        self.initial_state = initial_state

    def _map(self, state: tuple[float, float]) -> tuple[float, float]:
        x, y = state
        x_new = np.sin(self.a * y) - np.cos(self.b * x)
        y_new = np.sin(self.c * x) - np.cos(self.d * y)
        return (x_new, y_new)

    def integrate(self, initial_state: tuple[float, float] | None = None) -> np.ndarray:
        if initial_state is None:
            state = self.initial_state
        else:
            state = tuple(initial_state)

        # Pre-allocate with dtype for better performance
        trajectory = np.empty((self.steps, 3), dtype=np.float32)
        
        # Vectorized time calculation
        time_values = np.arange(self.steps, dtype=np.float32) * self.scale * 0.001
        
        for i in range(self.steps):
            trajectory[i, 0], trajectory[i, 1] = state
            trajectory[i, 2] = time_values[i]
            state = self._map(state)
        
        trajectory[:, 0:2] *= self.scale
        return trajectory
