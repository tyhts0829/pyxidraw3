#!/usr/bin/env python3
"""
新しいキャッシュシステムのテストと統計情報確認
"""

import time
import numpy as np
from api.geometry_api import GeometryAPI
from api.effect_chain import E
from engine.core.geometry_data import GeometryData


def create_test_geometry(n_points: int = 1000) -> GeometryAPI:
    """テスト用ジオメトリを生成"""
    coords = np.random.rand(n_points, 3).astype(np.float32) * 10
    offsets = np.arange(n_points, dtype=np.int32)
    geometry_data = GeometryData(coords, offsets)
    return GeometryAPI(geometry_data)


def test_cache_effectiveness():
    """キャッシュの効果をテスト"""
    print("=== 新しいキャッシュシステムのテスト ===\n")
    
    # キャッシュをクリア
    E.clear_cache()
    print("初期キャッシュ状態:")
    print(E.cache_info())
    print()
    
    geometry = create_test_geometry(2000)
    
    print("1. 同一パラメータでの複数回実行テスト")
    
    # 1回目実行
    start_time = time.perf_counter()
    result1 = E.add(geometry).noise(intensity=0.5, frequency=(1.0, 1.0, 1.0)).result()
    time1 = time.perf_counter() - start_time
    
    print(f"1回目実行時間: {time1:.4f}s")
    print("キャッシュ状態（1回目実行後）:")
    print(E.cache_info())
    print()
    
    # 2回目実行（同じパラメータ）
    start_time = time.perf_counter()
    result2 = E.add(geometry).noise(intensity=0.5, frequency=(1.0, 1.0, 1.0)).result()
    time2 = time.perf_counter() - start_time
    
    print(f"2回目実行時間: {time2:.4f}s")
    print("キャッシュ状態（2回目実行後）:")
    print(E.cache_info())
    
    if time1 > 0 and time2 > 0:
        speedup = time1 / time2
        print(f"高速化倍率: {speedup:.2f}倍")
    print()
    
    print("2. 異なるパラメータでの実行テスト")
    
    # 異なるパラメータで実行
    start_time = time.perf_counter()
    result3 = E.add(geometry).noise(intensity=0.8, frequency=(2.0, 2.0, 2.0)).result()
    time3 = time.perf_counter() - start_time
    
    print(f"異なるパラメータ実行時間: {time3:.4f}s")
    print("キャッシュ状態（異なるパラメータ実行後）:")
    print(E.cache_info())
    print()
    
    print("3. 複数エフェクトチェーンのテスト")
    
    # 複数エフェクトのチェーン
    start_time = time.perf_counter()
    result4 = E.add(geometry).noise(intensity=0.3).rotation(rotate=(0.1, 0.1, 0.1)).scaling(scale=(1.1, 1.1, 1.1)).result()
    time4 = time.perf_counter() - start_time
    
    print(f"複数エフェクト実行時間: {time4:.4f}s")
    print("キャッシュ状態（複数エフェクト実行後）:")
    print(E.cache_info())
    print()
    
    # 同じチェーンを再実行
    start_time = time.perf_counter()
    result5 = E.add(geometry).noise(intensity=0.3).rotation(rotate=(0.1, 0.1, 0.1)).scaling(scale=(1.1, 1.1, 1.1)).result()
    time5 = time.perf_counter() - start_time
    
    print(f"同じチェーン再実行時間: {time5:.4f}s")
    print("最終キャッシュ状態:")
    print(E.cache_info())
    
    if time4 > 0 and time5 > 0:
        chain_speedup = time4 / time5
        print(f"チェーンキャッシュ高速化倍率: {chain_speedup:.2f}倍")


if __name__ == "__main__":
    test_cache_effectiveness()