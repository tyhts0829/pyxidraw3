#!/usr/bin/env python3
"""
PyxiDraw 次期API（2025-06版） - ユーザーコード例

形状チェーンとエフェクトチェーンを分離した新しいAPIの使用例を示します。
高性能キャッシュ、メソッドチェーン、ユーザー拡張機能のすべてをカバー。
"""

import numpy as np
from api import G, E, GeometryAPI

# ===================================================================
# 1. 基本的な使用例
# ===================================================================

print("=== 1. 基本的な使用例 ===")

# 形状チェーン - 球体を作成して変形
sphere = (G.sphere(subdivisions=0.5)
            .size(100, 100, 100)
            .at(100, 100, 0))

print(f"Sphere: {sphere}")
print(f"Center: {sphere.center()}")
print(f"Points: {sphere.num_points()}, Lines: {sphere.num_lines()}")

# エフェクトチェーン - 球体にエフェクトを適用
processed_sphere = (E.add(sphere)
                     .noise(intensity=0.3)
                     .filling(density=0.5)
                     .result())

print(f"Processed sphere: {processed_sphere}")
print()

# ===================================================================
# 2. 様々な形状の作成
# ===================================================================

print("=== 2. 様々な形状の作成 ===")

# 多角形 - 六角形を作成
hexagon = (G.polygon(n_sides=6)
             .size(50)
             .at(0, 0, 0))

# グリッド - 10x10のグリッド
grid = (G.grid(divisions=10)
          .size(200, 200, 1))

# 正多面体 - 正二十面体
icosahedron = (G.polyhedron(polyhedron_type=0.8)
                 .size(80))

# テキスト
text_shape = (G.text(text_content="PyxiDraw")
                .size(30)
                .at(-50, 50, 0))

print(f"Hexagon: {hexagon}")
print(f"Grid: {grid}")
print(f"Icosahedron: {icosahedron}")
print(f"Text: {text_shape}")
print()

# ===================================================================
# 3. 複雑なエフェクトチェーン
# ===================================================================

print("=== 3. 複雑なエフェクトチェーン ===")

# 複数エフェクトの組み合わせ
complex_shape = (E.add(hexagon)
                  .noise(intensity=0.2, frequency=2.0)
                  .rotation(angle=45)
                  .scaling(factor=1.5)
                  .buffer(distance=5)
                  .subdivision(level=2)
                  .filling(density=0.7)
                  .result())

print(f"Complex processed shape: {complex_shape}")
print()

# ===================================================================
# 4. ユーザー拡張 - カスタム形状作成
# ===================================================================

print("=== 4. ユーザー拡張 - カスタム形状作成 ===")

# 線分リストから形状を作成
custom_lines = [
    np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0], [0, 0, 0]]),  # 正方形
    np.array([[0.5, 0.5, 0], [0.5, 0.5, 1]]),                           # 中心から上への線
    np.array([[0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1], [0, 0, 1]]),  # 上面の正方形
]

custom_shape = (G.from_lines(custom_lines)
                  .size(60)
                  .at(50, -50, 0))

print(f"Custom shape from lines: {custom_shape}")

# より複雑なカスタム形状 - 螺旋
spiral_points = []
for i in range(100):
    t = i * 0.1
    x = t * np.cos(t)
    y = t * np.sin(t)
    z = t * 0.1
    spiral_points.append([x, y, z])

spiral_lines = [np.array(spiral_points)]
spiral = (G.from_lines(spiral_lines)
            .size(20)
            .at(0, 0, 50))

print(f"Spiral: {spiral}")
print()

# ===================================================================
# 5. ワンショット効果 - apply() の使用
# ===================================================================

print("=== 5. ワンショット効果 - apply() の使用 ===")

# lambda関数でのワンショット効果
twisted_sphere = (E.add(sphere)
                   .apply(lambda g: g.rotate(z=np.radians(45)))
                   .apply(lambda g: g.size(0.8, 0.8, 1.2))
                   .apply(lambda g: g.translate(0, 0, 20))
                   .result())

print(f"Twisted sphere: {twisted_sphere}")

# 複雑な変形関数
def wave_distortion(g: GeometryAPI) -> GeometryAPI:
    """座標に波状の歪みを適用"""
    coords = g.coords.copy()
    coords[:, 2] += 10 * np.sin(coords[:, 0] * 0.1) * np.cos(coords[:, 1] * 0.1)
    
    # 新しいGeometryDataを作成
    from engine.core.geometry_data import GeometryData
    new_data = GeometryData(coords, g.offsets)
    return GeometryAPI(new_data)

wavy_grid = (E.add(grid)
              .apply(wave_distortion)
              .noise(intensity=0.1)
              .result())

print(f"Wavy grid: {wavy_grid}")
print()

# ===================================================================
# 6. カスタムエフェクトの登録と使用
# ===================================================================

print("=== 6. カスタムエフェクトの登録と使用 ===")

# カスタムエフェクト1: 回転渦巻き効果
@E.register("swirl")
def swirl(g: GeometryAPI, strength: float = 1.0) -> GeometryAPI:
    """座標のX値に基づいてZ軸回転を適用"""
    coords = g.coords.copy()
    
    # X座標に基づいて回転角度を計算
    angles = coords[:, 0] * strength * 0.01
    
    # 各点を個別に回転
    for i, angle in enumerate(angles):
        cos_a, sin_a = np.cos(angle), np.sin(angle)
        x, y = coords[i, 0], coords[i, 1]
        coords[i, 0] = x * cos_a - y * sin_a
        coords[i, 1] = x * sin_a + y * cos_a
    
    from engine.core.geometry_data import GeometryData
    new_data = GeometryData(coords, g.offsets)
    return GeometryAPI(new_data)

# カスタムエフェクト2: パルス効果
@E.register("pulse")
def pulse(g: GeometryAPI, frequency: float = 1.0, amplitude: float = 0.1) -> GeometryAPI:
    """中心からの距離に基づいてサイズを変動"""
    coords = g.coords.copy()
    center = np.array(g.center())
    
    # 中心からの距離を計算
    distances = np.linalg.norm(coords - center, axis=1)
    
    # パルス効果を適用
    pulse_factor = 1.0 + amplitude * np.sin(distances * frequency)
    coords = center + (coords - center) * pulse_factor[:, np.newaxis]
    
    from engine.core.geometry_data import GeometryData
    new_data = GeometryData(coords, g.offsets)
    return GeometryAPI(new_data)

# カスタムエフェクトの使用
swirled_shape = (E.add(hexagon)
                  .swirl(strength=2.0)
                  .pulse(frequency=2.0, amplitude=0.2)
                  .filling(density=0.6)
                  .result())

print(f"Swirled and pulsed shape: {swirled_shape}")
print()

# ===================================================================
# 7. 形状の組み合わせ
# ===================================================================

print("=== 7. 形状の組み合わせ ===")

# 複数の形状を結合
triangle = G.polygon(n_sides=3).size(30).at(-30, 0, 0)
square = G.polygon(n_sides=4).size(30).at(0, 0, 0)
pentagon = G.polygon(n_sides=5).size(30).at(30, 0, 0)

combined_shapes = triangle + square + pentagon

print(f"Combined shapes: {combined_shapes}")

# 結合した形状にエフェクトを適用
processed_combined = (E.add(combined_shapes)
                       .rotation(angle=30)
                       .noise(intensity=0.15)
                       .array(count=3)
                       .result())

print(f"Processed combined shapes: {processed_combined}")
print()

# ===================================================================
# 8. 高度な使用例 - アニメーション的な変形
# ===================================================================

print("=== 8. 高度な使用例 - アニメーション的な変形 ===")

def create_morphing_sequence(base_shape: GeometryAPI, steps: int = 5):
    """形状の段階的な変形シーケンスを作成"""
    sequence = []
    
    for i in range(steps):
        t = i / (steps - 1)  # 0.0 to 1.0
        
        # 時間に基づいた変形パラメータ
        rotation_angle = t * 360  # 0度から360度まで回転
        scale_factor = 1.0 + 0.5 * np.sin(t * np.pi)  # サイズの変動
        noise_intensity = 0.2 * t  # ノイズの増加
        
        morphed = (E.add(base_shape)
                    .rotation(angle=rotation_angle)
                    .scaling(factor=scale_factor)
                    .noise(intensity=noise_intensity)
                    .swirl(strength=t * 2.0)
                    .result())
        
        sequence.append(morphed)
        print(f"Step {i+1}: rotation={rotation_angle:.1f}°, scale={scale_factor:.2f}, noise={noise_intensity:.2f}")
    
    return sequence

# 螺旋の変形シーケンス
morph_sequence = create_morphing_sequence(spiral, steps=5)
print(f"Created morphing sequence with {len(morph_sequence)} steps")
print()

# ===================================================================
# 9. パフォーマンステスト - キャッシュ効果の確認
# ===================================================================

print("=== 9. パフォーマンステスト - キャッシュ効果の確認 ===")

import time

# 同じ形状を複数回生成（キャッシュが効くはず）
start_time = time.time()
for i in range(10):
    cached_sphere = G.sphere(subdivisions=0.5).size(100)
first_run_time = time.time() - start_time

# 同じパラメータで再度実行
start_time = time.time()
for i in range(10):
    cached_sphere = G.sphere(subdivisions=0.5).size(100)
second_run_time = time.time() - start_time

print(f"First run (10 spheres): {first_run_time:.4f}s")
print(f"Second run (cached): {second_run_time:.4f}s")
print(f"Cache speedup: {first_run_time/second_run_time:.1f}x")

# エフェクトチェーンのキャッシュテスト
base_for_effects = G.polygon(n_sides=8).size(50)

start_time = time.time()
for i in range(5):
    effect_result = (E.add(base_for_effects)
                      .noise(intensity=0.2)
                      .filling(density=0.5)
                      .result())
first_effect_time = time.time() - start_time

start_time = time.time()
for i in range(5):
    effect_result = (E.add(base_for_effects)
                      .noise(intensity=0.2)
                      .filling(density=0.5)
                      .result())
second_effect_time = time.time() - start_time

print(f"First effect run: {first_effect_time:.4f}s")
print(f"Second effect run (cached): {second_effect_time:.4f}s")
print(f"Effect cache speedup: {first_effect_time/second_effect_time:.1f}x")
print()

# ===================================================================
# 10. 実用的な作例 - 建築的な構造
# ===================================================================

print("=== 10. 実用的な作例 - 建築的な構造 ===")

def create_building():
    """建築物のような複雑な構造を作成"""
    
    # 基礎
    foundation = (G.polygon(n_sides=4)
                    .size(100, 100, 10)
                    .at(0, 0, 0))
    
    # 柱
    columns = []
    for x in [-30, 30]:
        for y in [-30, 30]:
            column = (G.cylinder()
                        .size(5, 5, 60)
                        .at(x, y, 30))
            columns.append(column)
    
    # 屋根
    roof = (G.polygon(n_sides=3)
              .size(120, 120, 5)
              .at(0, 0, 70))
    
    # 全体を結合
    building_parts = [foundation] + columns + [roof]
    building = building_parts[0]
    for part in building_parts[1:]:
        building = building + part
    
    # 建物全体にエフェクトを適用
    detailed_building = (E.add(building)
                          .subdivision(level=1)
                          .noise(intensity=0.05)  # 微細なディテール
                          .buffer(distance=1)     # 僅かな太さの追加
                          .result())
    
    return detailed_building

building = create_building()
print(f"Architectural structure: {building}")
print()

# ===================================================================
# 11. キャッシュ情報とデバッグ
# ===================================================================

print("=== 11. キャッシュ情報とデバッグ ===")

# 形状キャッシュの情報
cache_info = G.cache_info()
print(f"Shape cache info: {cache_info}")

# エフェクトの一覧
available_effects = E.list_effects()
print(f"Available standard effects: {available_effects['standard']}")
print(f"Available custom effects: {available_effects['custom']}")

# エフェクトチェーンの詳細情報
sample_chain = E.add(sphere).noise(0.1).swirl(1.0).filling(0.3)
print(f"Effect chain steps: {sample_chain.steps()}")
print(f"Effect chain representation: {sample_chain}")

print()
print("=== PyxiDraw 次期API デモンストレーション完了 ===")
print("高性能キャッシュ、メソッドチェーン、ユーザー拡張機能のすべてが正常に動作します。")