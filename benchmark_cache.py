#!/usr/bin/env python3
"""
キャッシュリファクタリング前後のパフォーマンス比較用ベンチマーク
重めの描画処理で実行速度を測定します。
"""

import time
import numpy as np
from typing import List, Tuple

from api.geometry_api import GeometryAPI
from api.effect_chain import E
from engine.core.geometry_data import GeometryData


def create_heavy_geometry(n_points: int = 10000) -> GeometryAPI:
    """重めの描画用ジオメトリを生成"""
    # 複雑な3Dメッシュを生成
    coords = np.random.rand(n_points, 3).astype(np.float32) * 100
    
    # より複雑なoffsets（ポリゴンを構成）
    n_polygons = n_points // 10
    offsets = []
    for i in range(n_polygons):
        # 各ポリゴンは3-8頂点
        poly_size = np.random.randint(3, 9)
        start_idx = i * 10
        end_idx = min(start_idx + poly_size, n_points)
        offsets.extend(range(start_idx, end_idx))
        if len(offsets) >= n_points:
            break
    
    offsets_array = np.array(offsets[:n_points], dtype=np.int32)
    
    geometry_data = GeometryData(coords, offsets_array)
    return GeometryAPI(geometry_data)


def benchmark_heavy_processing() -> List[float]:
    """重い処理のベンチマーク"""
    times = []
    
    # 複数の重いジオメトリを作成
    geometries = [create_heavy_geometry(5000) for _ in range(3)]
    
    test_cases = [
        # 複数エフェクトのチェーン
        lambda g: E.add(g).noise(intensity=1.0, frequency=(2.0, 2.0, 2.0)).rotation(rotate=(0.5, 0.5, 0.5)).scaling(scale=(1.2, 1.2, 1.2)).result(),
        
        # 同じエフェクトを複数回（キャッシュの効果を測定）
        lambda g: E.add(g).noise(intensity=0.5, frequency=(1.0, 1.0, 1.0)).result(),
        lambda g: E.add(g).noise(intensity=0.5, frequency=(1.0, 1.0, 1.0)).result(),  # 同じパラメータ
        
        # 異なるパラメータでのノイズ
        lambda g: E.add(g).noise(intensity=0.8, frequency=(1.5, 1.5, 1.5)).result(),
        
        # 長いエフェクトチェーン
        lambda g: E.add(g).noise(intensity=0.3).subdivision(n_divisions=0.8).rotation(rotate=(0.2, 0.2, 0.2)).scaling(scale=(0.9, 0.9, 0.9)).translation(offset_x=1.0).result(),
    ]
    
    for i, geometry in enumerate(geometries):
        for j, test_case in enumerate(test_cases):
            start_time = time.perf_counter()
            
            # テストケースを実行
            result = test_case(geometry)
            
            end_time = time.perf_counter()
            execution_time = end_time - start_time
            times.append(execution_time)
            
            print(f"Geometry {i+1}, Test {j+1}: {execution_time:.4f}s")
    
    return times


def benchmark_cache_effectiveness():
    """キャッシュの効果を測定"""
    print("\n=== キャッシュ効果測定 ===")
    
    geometry = create_heavy_geometry(3000)
    
    # 同じ処理を繰り返し実行
    def repeated_operation():
        return E.add(geometry).noise(intensity=0.7, frequency=(1.0, 1.0, 1.0)).rotation(rotate=(0.3, 0.3, 0.3)).result()
    
    # 初回実行（キャッシュなし）
    start_time = time.perf_counter()
    result1 = repeated_operation()
    first_time = time.perf_counter() - start_time
    
    # 2回目実行（キャッシュ有り）
    start_time = time.perf_counter()
    result2 = repeated_operation()
    second_time = time.perf_counter() - start_time
    
    # 3回目実行（キャッシュ有り）
    start_time = time.perf_counter()
    result3 = repeated_operation()
    third_time = time.perf_counter() - start_time
    
    print(f"1回目（キャッシュなし）: {first_time:.4f}s")
    print(f"2回目（キャッシュ有り）: {second_time:.4f}s")
    print(f"3回目（キャッシュ有り）: {third_time:.4f}s")
    print(f"キャッシュによる高速化: {first_time/second_time:.2f}倍")
    
    return [first_time, second_time, third_time]


def main():
    """メインベンチマーク実行"""
    print("=== キャッシュリファクタリング パフォーマンスベンチマーク ===\n")
    
    # キャッシュをクリア
    E.clear_cache()
    
    print("重い処理のベンチマーク開始...")
    heavy_times = benchmark_heavy_processing()
    
    cache_times = benchmark_cache_effectiveness()
    
    print(f"\n=== 結果サマリー ===")
    print(f"重い処理の平均実行時間: {np.mean(heavy_times):.4f}s")
    print(f"重い処理の合計実行時間: {np.sum(heavy_times):.4f}s")
    print(f"キャッシュ効果: 初回 {cache_times[0]:.4f}s → 2回目 {cache_times[1]:.4f}s")
    
    return {
        'heavy_times': heavy_times,
        'cache_times': cache_times,
        'total_time': np.sum(heavy_times),
        'avg_time': np.mean(heavy_times)
    }


if __name__ == "__main__":
    results = main()