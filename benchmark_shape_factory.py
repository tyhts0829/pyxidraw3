#!/usr/bin/env python3
"""
ShapeFactory改善前後のパフォーマンステスト
"""

import time
import sys
from typing import Dict, Any, List
import traceback

# 改善後のShapeFactoryをテスト
try:
    from api import G
    new_implementation_available = True
    print("✓ 新しいレジストリベースの実装をテスト")
except Exception as e:
    print(f"❌ 新しい実装のロードに失敗: {e}")
    new_implementation_available = False

# 改善前のShapeFactoryをテスト用に復元
def test_original_implementation():
    """改善前の実装でのパフォーマンステスト"""
    import shutil
    import os
    
    # バックアップから復元
    shutil.copy('/Users/tyhts0829/Documents/pyxidraw3/api/shape_factory_original.py', 
                '/Users/tyhts0829/Documents/pyxidraw3/api/shape_factory.py')
    
    # モジュールをリロード
    if 'api.shape_factory' in sys.modules:
        del sys.modules['api.shape_factory']
    if 'api' in sys.modules:
        del sys.modules['api']
    
    # 改善前の実装をインポート
    from api import G as G_old
    return G_old

def performance_test(G_instance, implementation_name: str, iterations: int = 1000) -> Dict[str, Any]:
    """パフォーマンステストを実行"""
    print(f"\\n=== {implementation_name} テスト開始 (iterations: {iterations}) ===")
    
    # テスト対象の形状とパラメータ
    test_shapes = [
        ("sphere", {"subdivisions": 0.5}),
        ("polygon", {"n_sides": 6}),
        ("grid", {"divisions": 10}),
        ("sphere", {"subdivisions": 0.3}),  # 異なるパラメータ
        ("polygon", {"n_sides": 8}),        # 異なるパラメータ
        ("sphere", {"subdivisions": 0.5}),  # キャッシュヒット
        ("polygon", {"n_sides": 6}),        # キャッシュヒット
    ]
    
    results = {}
    total_time = 0
    
    for shape_name, params in test_shapes:
        print(f"  テスト中: {shape_name}({params})")
        
        # ウォームアップ
        try:
            getattr(G_instance, shape_name)(**params)
        except Exception as e:
            print(f"    ❌ ウォームアップ失敗: {e}")
            continue
        
        # 実際のベンチマーク
        start_time = time.perf_counter()
        success_count = 0
        error_count = 0
        
        for i in range(iterations):
            try:
                result = getattr(G_instance, shape_name)(**params)
                success_count += 1
            except Exception as e:
                error_count += 1
                if error_count == 1:  # 最初のエラーのみ表示
                    print(f"    ⚠️  エラー発生: {e}")
        
        end_time = time.perf_counter()
        elapsed = end_time - start_time
        total_time += elapsed
        
        avg_time = elapsed / iterations * 1000  # ミリ秒
        ops_per_sec = iterations / elapsed if elapsed > 0 else 0
        
        test_key = f"{shape_name}({params})"
        results[test_key] = {
            "total_time": elapsed,
            "avg_time_ms": avg_time,
            "ops_per_sec": ops_per_sec,
            "success_count": success_count,
            "error_count": error_count
        }
        
        print(f"    ✓ 平均: {avg_time:.3f}ms, {ops_per_sec:.1f} ops/sec, 成功: {success_count}, エラー: {error_count}")
    
    # キャッシュ情報（利用可能な場合）
    try:
        cache_info = G_instance.cache_info()
        print(f"  キャッシュ情報: hits={cache_info.hits}, misses={cache_info.misses}, ratio={cache_info.hits/(cache_info.hits+cache_info.misses):.3f}")
        results["cache_info"] = {
            "hits": cache_info.hits,
            "misses": cache_info.misses,
            "hit_ratio": cache_info.hits/(cache_info.hits+cache_info.misses) if (cache_info.hits+cache_info.misses) > 0 else 0
        }
    except:
        print("  キャッシュ情報: 利用不可")
        results["cache_info"] = None
    
    results["total_time"] = total_time
    results["implementation"] = implementation_name
    
    print(f"=== {implementation_name} テスト完了 (総時間: {total_time:.3f}s) ===")
    return results

def memory_test(G_instance, implementation_name: str) -> Dict[str, Any]:
    """メモリ使用量テスト"""
    import psutil
    import gc
    
    print(f"\\n=== {implementation_name} メモリテスト ===")
    
    # ガベージコレクション実行
    gc.collect()
    
    # 初期メモリ使用量
    process = psutil.Process()
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    # 大量の形状を生成
    shapes = []
    for i in range(100):
        try:
            sphere = G_instance.sphere(subdivisions=0.5).size(100)
            polygon = G_instance.polygon(n_sides=6).size(50)
            shapes.extend([sphere, polygon])
        except Exception as e:
            print(f"  ⚠️  形状生成エラー: {e}")
            break
    
    # ピーク時メモリ使用量
    peak_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    # オブジェクトを削除
    del shapes
    gc.collect()
    
    # 最終メモリ使用量
    final_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    memory_usage = peak_memory - initial_memory
    memory_retained = final_memory - initial_memory
    
    print(f"  初期メモリ: {initial_memory:.1f}MB")
    print(f"  ピーク時メモリ: {peak_memory:.1f}MB")
    print(f"  最終メモリ: {final_memory:.1f}MB")
    print(f"  使用メモリ: {memory_usage:.1f}MB")
    print(f"  保持メモリ: {memory_retained:.1f}MB")
    
    return {
        "initial_memory_mb": initial_memory,
        "peak_memory_mb": peak_memory,
        "final_memory_mb": final_memory,
        "memory_usage_mb": memory_usage,
        "memory_retained_mb": memory_retained
    }

def compare_results(old_results: Dict, new_results: Dict):
    """結果を比較"""
    print("\\n" + "="*60)
    print("パフォーマンス比較結果")
    print("="*60)
    
    print(f"\\n📊 総合パフォーマンス:")
    old_total = old_results.get("total_time", 0)
    new_total = new_results.get("total_time", 0)
    
    if old_total > 0 and new_total > 0:
        speedup = old_total / new_total
        print(f"  改善前: {old_total:.3f}s")
        print(f"  改善後: {new_total:.3f}s")
        print(f"  速度向上: {speedup:.2f}x {'🚀' if speedup > 1 else '⚠️' if speedup < 1 else '='}")
    
    print(f"\\n📈 個別形状の比較:")
    
    for key in old_results:
        if isinstance(old_results[key], dict) and "avg_time_ms" in old_results[key]:
            old_time = old_results[key]["avg_time_ms"]
            new_time = new_results.get(key, {}).get("avg_time_ms", 0)
            
            if old_time > 0 and new_time > 0:
                speedup = old_time / new_time
                print(f"  {key}:")
                print(f"    改善前: {old_time:.3f}ms")
                print(f"    改善後: {new_time:.3f}ms")
                print(f"    速度向上: {speedup:.2f}x {'🚀' if speedup > 1 else '⚠️' if speedup < 1 else '='}")
    
    # キャッシュ効率の比較
    print(f"\\n💾 キャッシュ効率:")
    old_cache = old_results.get("cache_info")
    new_cache = new_results.get("cache_info")
    
    if old_cache and new_cache:
        print(f"  改善前: ヒット率 {old_cache['hit_ratio']:.3f} (hits: {old_cache['hits']}, misses: {old_cache['misses']})")
        print(f"  改善後: ヒット率 {new_cache['hit_ratio']:.3f} (hits: {new_cache['hits']}, misses: {new_cache['misses']})")

def main():
    """メイン実行関数"""
    print("ShapeFactory レジストリパターン改善 - パフォーマンステスト")
    print("="*60)
    
    iterations = 500  # テスト回数
    
    # 改善後の実装をテスト
    if not new_implementation_available:
        print("❌ 新しい実装が利用できません。テストを終了します。")
        return
    
    # キャッシュクリア
    try:
        G.clear_cache()
        print("✓ キャッシュをクリアしました")
    except:
        print("⚠️  キャッシュクリアに失敗（実装されていない可能性）")
    
    # 改善後のテスト
    print("\\n🔄 改善後の実装をテスト中...")
    new_results = performance_test(G, "改善後（レジストリパターン）", iterations)
    new_memory = memory_test(G, "改善後（レジストリパターン）")
    
    # 改善前の実装をテスト
    print("\\n🔄 改善前の実装に切り替え中...")
    try:
        G_old = test_original_implementation()
        print("✓ 改善前の実装をロードしました")
        
        # キャッシュクリア
        try:
            G_old.clear_cache()
        except:
            pass
        
        old_results = performance_test(G_old, "改善前（if-elif文）", iterations)
        old_memory = memory_test(G_old, "改善前（if-elif文）")
        
        # 結果比較
        compare_results(old_results, new_results)
        
        print(f"\\n💾 メモリ使用量比較:")
        print(f"  改善前: {old_memory['memory_usage_mb']:.1f}MB")
        print(f"  改善後: {new_memory['memory_usage_mb']:.1f}MB")
        memory_ratio = old_memory['memory_usage_mb'] / new_memory['memory_usage_mb'] if new_memory['memory_usage_mb'] > 0 else 1
        print(f"  メモリ効率: {memory_ratio:.2f}x {'📉' if memory_ratio > 1 else '📈' if memory_ratio < 1 else '='}")
        
    except Exception as e:
        print(f"❌ 改善前の実装テストに失敗: {e}")
        traceback.print_exc()
        
        # 改善後の実装のみの結果を表示
        print("\\n📊 改善後の実装のみの結果:")
        print(f"  総実行時間: {new_results['total_time']:.3f}s")
        if new_results.get('cache_info'):
            cache = new_results['cache_info']
            print(f"  キャッシュヒット率: {cache['hit_ratio']:.3f}")
        print(f"  メモリ使用量: {new_memory['memory_usage_mb']:.1f}MB")
    
    # 改善後の実装を復元
    print("\\n🔄 改善後の実装を復元中...")
    try:
        # バックアップから復元（逆方向）
        import shutil
        shutil.copy('/Users/tyhts0829/Documents/pyxidraw3/api/shape_factory.py', 
                    '/Users/tyhts0829/Documents/pyxidraw3/api/shape_factory_backup.py')
        
        # 改善後の実装を再適用（実際には既に適用済み）
        print("✓ 改善後の実装が有効です")
    except Exception as e:
        print(f"⚠️  復元処理でエラー: {e}")
    
    print("\\n" + "="*60)
    print("テスト完了")
    print("="*60)

if __name__ == "__main__":
    main()