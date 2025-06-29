from __future__ import annotations

from typing import Any

import numpy as np
from numba import njit

from .base import BaseShape
from engine.core.geometry_data import GeometryData


@njit(fastmath=True, cache=True)
def _generate_cylinder_vertical_lines(segments: int, radius: float, half_height: float) -> np.ndarray:
    """円柱部分の縦線を生成する。"""
    lines = np.empty((segments, 2, 3), dtype=np.float32)
    
    for i in range(segments):
        angle = 2 * np.pi * i / segments
        x = radius * np.cos(angle)
        y = radius * np.sin(angle)
        
        lines[i, 0, 0] = x
        lines[i, 0, 1] = y
        lines[i, 0, 2] = half_height
        
        lines[i, 1, 0] = x
        lines[i, 1, 1] = y
        lines[i, 1, 2] = -half_height
    
    return lines


@njit(fastmath=True, cache=True)
def _generate_cylinder_horizontal_lines(segments: int, radius: float, z: float) -> np.ndarray:
    """円柱部分の横線を生成する。"""
    lines = np.empty((segments, 2, 3), dtype=np.float32)
    
    for i in range(segments):
        angle1 = 2 * np.pi * i / segments
        angle2 = 2 * np.pi * (i + 1) / segments
        
        x1 = radius * np.cos(angle1)
        y1 = radius * np.sin(angle1)
        x2 = radius * np.cos(angle2)
        y2 = radius * np.sin(angle2)
        
        lines[i, 0, 0] = x1
        lines[i, 0, 1] = y1
        lines[i, 0, 2] = z
        
        lines[i, 1, 0] = x2
        lines[i, 1, 1] = y2
        lines[i, 1, 2] = z
    
    return lines


@njit(fastmath=True, cache=True)
def _generate_hemisphere_latitude_lines(segments: int, latitude_segments: int, radius: float, 
                                       z_offset: float, z_sign: float) -> np.ndarray:
    """半球の緯度線を生成する。"""
    num_lines = (latitude_segments - 1) * segments
    lines = np.empty((num_lines, 2, 3), dtype=np.float32)
    
    line_idx = 0
    for lat in range(1, latitude_segments):
        phi = np.pi * lat / (2 * latitude_segments)  # 0 to π/2
        z = z_offset + z_sign * radius * np.cos(phi)
        r = radius * np.sin(phi)
        
        for i in range(segments):
            angle1 = 2 * np.pi * i / segments
            angle2 = 2 * np.pi * (i + 1) / segments
            
            x1 = r * np.cos(angle1)
            y1 = r * np.sin(angle1)
            x2 = r * np.cos(angle2)
            y2 = r * np.sin(angle2)
            
            lines[line_idx, 0, 0] = x1
            lines[line_idx, 0, 1] = y1
            lines[line_idx, 0, 2] = z
            
            lines[line_idx, 1, 0] = x2
            lines[line_idx, 1, 1] = y2
            lines[line_idx, 1, 2] = z
            
            line_idx += 1
    
    return lines


@njit(fastmath=True, cache=True)
def _generate_hemisphere_meridian_lines(segments: int, latitude_segments: int, radius: float,
                                       z_offset: float, z_sign: float) -> np.ndarray:
    """半球の経度線を生成する。"""
    num_lines = segments * latitude_segments
    lines = np.empty((num_lines, 2, 3), dtype=np.float32)
    
    line_idx = 0
    for i in range(segments):
        angle = 2 * np.pi * i / segments
        cos_angle = np.cos(angle)
        sin_angle = np.sin(angle)
        
        for lat in range(latitude_segments):
            phi1 = np.pi * lat / (2 * latitude_segments)
            phi2 = np.pi * (lat + 1) / (2 * latitude_segments)
            
            z1 = z_offset + z_sign * radius * np.cos(phi1)
            r1 = radius * np.sin(phi1)
            z2 = z_offset + z_sign * radius * np.cos(phi2)
            r2 = radius * np.sin(phi2)
            
            x1 = r1 * cos_angle
            y1 = r1 * sin_angle
            x2 = r2 * cos_angle
            y2 = r2 * sin_angle
            
            lines[line_idx, 0, 0] = x1
            lines[line_idx, 0, 1] = y1
            lines[line_idx, 0, 2] = z1
            
            lines[line_idx, 1, 0] = x2
            lines[line_idx, 1, 1] = y2
            lines[line_idx, 1, 2] = z2
            
            line_idx += 1
    
    return lines


@njit(fastmath=True, cache=True)
def _apply_scaling_to_capsule(lines_array: np.ndarray, scale_x: float, scale_y: float, scale_z: float) -> np.ndarray:
    """カプセルの線配列にスケーリングを適用する。"""
    scaled_lines = lines_array.copy()
    
    # 各線の各頂点にスケーリングを適用
    for i in range(scaled_lines.shape[0]):
        for j in range(scaled_lines.shape[1]):
            scaled_lines[i, j, 0] *= scale_x  # x軸
            scaled_lines[i, j, 1] *= scale_y  # y軸
            scaled_lines[i, j, 2] *= scale_z  # z軸
    
    return scaled_lines


@njit(fastmath=True, cache=True)
def _generate_scaled_capsule_fast(segments: int, latitude_segments: int, 
                                 scale_x: float, scale_y: float, scale_z: float) -> np.ndarray:
    """スケーリング済みのカプセルを直接生成する。"""
    # ユニットカプセルを生成
    unit_capsule = _generate_unit_capsule_fast(segments, latitude_segments)
    
    # スケーリングを適用
    scaled_capsule = _apply_scaling_to_capsule(unit_capsule, scale_x, scale_y, scale_z)
    
    return scaled_capsule


@njit(fastmath=True, cache=True)
def _generate_unit_capsule_fast(segments: int, latitude_segments: int) -> np.ndarray:
    """njitを使用してユニットカプセルを高速生成する。"""
    radius = 0.5
    half_height = 0.5
    
    # 線の総数を計算
    total_lines = (
        segments +  # 縦線
        2 * segments +  # 上下の横線
        2 * (latitude_segments - 1) * segments +  # 上下半球の緯度線
        2 * segments * latitude_segments  # 上下半球の経度線
    )
    
    all_lines = np.empty((total_lines, 2, 3), dtype=np.float32)
    
    # 円柱部分の縦線
    vertical_lines = _generate_cylinder_vertical_lines(segments, radius, half_height)
    all_lines[:segments] = vertical_lines
    
    # 円柱部分の横線（上端と下端）
    upper_horizontal = _generate_cylinder_horizontal_lines(segments, radius, half_height)
    lower_horizontal = _generate_cylinder_horizontal_lines(segments, radius, -half_height)
    
    start_idx = segments
    all_lines[start_idx:start_idx + segments] = upper_horizontal
    start_idx += segments
    all_lines[start_idx:start_idx + segments] = lower_horizontal
    start_idx += segments
    
    # 上半球の緯度線
    upper_latitude = _generate_hemisphere_latitude_lines(segments, latitude_segments, radius, half_height, 1.0)
    num_upper_lat = (latitude_segments - 1) * segments
    all_lines[start_idx:start_idx + num_upper_lat] = upper_latitude
    start_idx += num_upper_lat
    
    # 下半球の緯度線
    lower_latitude = _generate_hemisphere_latitude_lines(segments, latitude_segments, radius, -half_height, -1.0)
    num_lower_lat = (latitude_segments - 1) * segments
    all_lines[start_idx:start_idx + num_lower_lat] = lower_latitude
    start_idx += num_lower_lat
    
    # 上半球の経度線
    upper_meridian = _generate_hemisphere_meridian_lines(segments, latitude_segments, radius, half_height, 1.0)
    num_upper_mer = segments * latitude_segments
    all_lines[start_idx:start_idx + num_upper_mer] = upper_meridian
    start_idx += num_upper_mer
    
    # 下半球の経度線
    lower_meridian = _generate_hemisphere_meridian_lines(segments, latitude_segments, radius, -half_height, -1.0)
    num_lower_mer = segments * latitude_segments
    all_lines[start_idx:start_idx + num_lower_mer] = lower_meridian
    
    return all_lines


class Capsule(BaseShape):
    """数学的計算によるカプセル（半球+円柱）形状生成器。njitで高速化済み。"""

    def generate(
        self, radius: float = 0.2, height: float = 0.4, segments: int = 32, latitude_segments: int = 16, **params: Any
    ) -> GeometryData:
        """カプセル形状を生成する。

        Args:
            radius: 半球の半径
            height: 円柱部分の高さ
            segments: 経度方向のセグメント数（周方向の分割数）
            latitude_segments: 緯度方向のセグメント数（半球の分割数）
            **params: 追加パラメータ（無視される）

        Returns:
            GeometryData object containing カプセル線
        """
        # スケーリング係数を計算
        # ユニットカプセルは半径=0.5、高さ=1.0
        scale_xy = radius / 1.0  # 半径のスケール
        scale_z = height / 2.0  # 高さのスケール

        # njitで高速化されたスケーリング済みカプセルを直接生成
        scaled_lines_array = _generate_scaled_capsule_fast(segments, latitude_segments, scale_xy, scale_xy, scale_z)
        
        # numpy配列のリストに変換（互換性のため）
        lines = [scaled_lines_array[i] for i in range(scaled_lines_array.shape[0])]

        return GeometryData.from_lines(lines)
