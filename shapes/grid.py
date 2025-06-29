from __future__ import annotations

from typing import Any

import numpy as np

from engine.core.geometry_data import GeometryData
from .base import BaseShape


def _generate_grid(nx: int, ny: int) -> list[np.ndarray]:
    """Generate grid vertices.

    Args:
        nx: Number of vertical lines
        ny: Number of horizontal lines

    Returns:
        List of vertex arrays for grid lines
    """
    if max(nx, ny) < 1:
        # Return empty grid if divisions are too small
        return []

    x_coords = np.linspace(-0.5, 0.5, nx)
    y_coords = np.linspace(-0.5, 0.5, ny)

    # Pre-allocate memory
    total_lines = nx + ny
    vertices_list: list[np.ndarray] = []

    # Generate vertical lines vectorized
    vertical_lines = np.empty((nx, 2, 3), dtype=np.float32)
    vertical_lines[:, :, 0] = x_coords[:, np.newaxis]  # x coordinates
    vertical_lines[:, 0, 1] = -0.5  # start y coordinate
    vertical_lines[:, 1, 1] = 0.5  # end y coordinate
    vertical_lines[:, :, 2] = 0.0  # z coordinate

    # Generate horizontal lines vectorized
    horizontal_lines = np.empty((ny, 2, 3), dtype=np.float32)
    horizontal_lines[:, 0, 0] = -0.5  # start x coordinate
    horizontal_lines[:, 1, 0] = 0.5  # end x coordinate
    horizontal_lines[:, :, 1] = y_coords[:, np.newaxis]  # y coordinates
    horizontal_lines[:, :, 2] = 0.0  # z coordinate

    # Store in vertices_list
    vertices_list.extend(vertical_lines)
    vertices_list.extend(horizontal_lines)

    return vertices_list


def grid_data(n_divisions: tuple[float, float] = (0.1, 0.1), center=(0, 0, 0), **params) -> GeometryData:
    """GeometryDataを直接返すgrid生成関数（API層に依存しない）。
    
    Args:
        n_divisions: (x_divisions, y_divisions) 分割数
        center: 中心点
        **params: 追加パラメータ
        
    Returns:
        GeometryData: 生成されたグリッドデータ
    """
    MAX_DIVISIONS = 50
    nx, ny = n_divisions
    nx = int(nx * MAX_DIVISIONS)
    ny = int(ny * MAX_DIVISIONS)
    
    # グリッド生成
    vertices_list = _generate_grid(nx, ny)
    
    # 中心を適用
    if center != (0, 0, 0):
        center_array = np.asarray(center, dtype=np.float32)
        for i, vertices in enumerate(vertices_list):
            vertices_list[i] = vertices + center_array
    
    return GeometryData.from_lines(vertices_list)


class Grid(BaseShape):
    """Grid shape generator."""

    MAX_DIVISIONS = 50

    def generate(self, n_divisions: tuple[float, float] = (0.1, 0.1), **params: Any) -> GeometryData:
        """Generate a 1x1 square grid with specified divisions.

        Args:
            n_divisions: (x_divisions, y_divisions) as floats 0.0-1.0
            **params: Additional parameters (ignored)

        Returns:
            GeometryData object containing grid lines
        """
        nx, ny = n_divisions
        nx = int(nx * Grid.MAX_DIVISIONS)
        ny = int(ny * Grid.MAX_DIVISIONS)

        # Generate grid (caching handled by BaseShape)
        vertices_list = _generate_grid(nx, ny)
        return GeometryData.from_lines(vertices_list)
