#!/usr/bin/env python3
"""
EffectChain実装の動作確認用テストスクリプト

改善されたEffectChain実装が正しく動作することを検証します：
1. 必要なモジュールのインポート
2. 簡単なテストジオメトリの作成
3. ノイズエフェクトの適用テスト
4. 結果がGeometryAPIオブジェクトかどうかの検証
5. 標準エフェクトとカスタムエフェクトのテスト
6. 結果の出力と機能確認
"""

import math
import numpy as np
from api import E, G
from api.geometry_api import GeometryAPI
from engine.core.geometry_data import GeometryData

def print_separator(title):
    """セクション区切りを出力"""
    print(f"\n{'='*50}")
    print(f" {title}")
    print(f"{'='*50}")

def create_test_geometry():
    """テスト用の簡単なジオメトリを作成"""
    print("シンプルなテストジオメトリを作成中...")
    
    # 簡単な三角形を作成
    triangle_coords = np.array([
        [0.0, 0.0, 0.0],    # 頂点1
        [1.0, 0.0, 0.0],    # 頂点2
        [0.5, 1.0, 0.0],    # 頂点3
        [0.0, 0.0, 0.0]     # 閉じる
    ], dtype=np.float32)
    
    offsets = np.array([0, 4], dtype=np.int32)  # 1つの線分
    
    geometry_data = GeometryData(triangle_coords, offsets)
    geometry_api = GeometryAPI(geometry_data)
    
    print(f"  作成されたジオメトリ: {geometry_api}")
    print(f"  頂点数: {geometry_api.num_points()}")
    print(f"  線分数: {geometry_api.num_lines()}")
    print(f"  バウンディングボックス: {geometry_api.bounds()}")
    
    return geometry_api

def test_basic_effect_chain():
    """基本的なエフェクトチェーンのテスト"""
    print_separator("基本的なエフェクトチェーンテスト")
    
    # テストジオメトリを作成
    test_geom = create_test_geometry()
    
    print("\n1. ノイズエフェクトの適用テスト")
    try:
        # ノイズエフェクトを適用
        result = E.add(test_geom).noise(intensity=0.1, frequency=1.0).result()
        
        print(f"  ✓ ノイズエフェクト適用成功")
        print(f"  結果の型: {type(result)}")
        print(f"  結果: {result}")
        print(f"  GeometryAPIインスタンスか: {isinstance(result, GeometryAPI)}")
        
        # 座標が変更されたかチェック
        original_coords = test_geom.coords
        modified_coords = result.coords
        coords_changed = not np.allclose(original_coords, modified_coords)
        print(f"  座標が変更されたか: {coords_changed}")
        
        return result
        
    except Exception as e:
        print(f"  ✗ ノイズエフェクト適用失敗: {e}")
        return None

def test_multiple_effects():
    """複数エフェクトの連鎖テスト"""
    print_separator("複数エフェクト連鎖テスト")
    
    # G.polygonを使って適当な形状を作成
    try:
        polygon = G.polygon(n_sides=6, scale=(50, 50, 1))
        print(f"  ベース形状: {polygon}")
        
        # 複数のエフェクトを連鎖
        result = (E.add(polygon)
                   .subdivision(n_divisions=0.3)
                   .noise(intensity=0.2)
                   .scaling(scale=(1.2, 1.2, 1.0))
                   .result())
        
        print(f"  ✓ 複数エフェクト連鎖成功")
        print(f"  最終結果: {result}")
        print(f"  元の頂点数: {polygon.num_points()}")
        print(f"  最終頂点数: {result.num_points()}")
        
        return result
        
    except Exception as e:
        print(f"  ✗ 複数エフェクト連鎖失敗: {e}")
        return None

def test_custom_effect():
    """カスタムエフェクトのテスト"""
    print_separator("カスタムエフェクトテスト")
    
    # カスタムエフェクトを定義
    @E.register("double_scale")
    def double_scale_effect(geometry_api: GeometryAPI, factor: float = 2.0) -> GeometryAPI:
        """座標を指定倍数でスケールするカスタムエフェクト"""
        return geometry_api.size(factor, factor, factor)
    
    try:
        # シンプルな形状を作成
        circle_like = G.polygon(n_sides=8, scale=(30, 30, 1))
        print(f"  ベース形状: {circle_like}")
        
        # カスタムエフェクトを適用
        result = E.add(circle_like).double_scale(factor=1.5).result()
        
        print(f"  ✓ カスタムエフェクト適用成功")
        print(f"  結果: {result}")
        
        # スケール効果を確認
        original_bounds = circle_like.bounds()
        result_bounds = result.bounds()
        print(f"  元のバウンディングボックス: {original_bounds}")
        print(f"  変換後バウンディングボックス: {result_bounds}")
        
        return result
        
    except Exception as e:
        print(f"  ✗ カスタムエフェクト失敗: {e}")
        return None

def test_apply_function():
    """apply関数によるワンショットエフェクトのテスト"""
    print_separator("apply関数テスト")
    
    try:
        # ベース形状
        base_shape = G.polygon(n_sides=4, scale=(40, 40, 1))
        print(f"  ベース形状: {base_shape}")
        
        # ワンショット関数を定義
        def rotate_and_move(geom: GeometryAPI) -> GeometryAPI:
            return geom.spin(45).move(10, 10)
        
        # apply関数を使って適用
        result = E.add(base_shape).apply(rotate_and_move).result()
        
        print(f"  ✓ apply関数適用成功")
        print(f"  結果: {result}")
        
        # 中心点の変化を確認
        original_center = base_shape.center()
        result_center = result.center()
        print(f"  元の中心点: {original_center}")
        print(f"  変換後中心点: {result_center}")
        
        return result
        
    except Exception as e:
        print(f"  ✗ apply関数失敗: {e}")
        return None

def test_effect_chain_properties():
    """エフェクトチェーンのプロパティとメソッドテスト"""
    print_separator("エフェクトチェーンプロパティテスト")
    
    try:
        # 形状作成
        shape = G.sphere(subdivisions=0.3, sphere_type=0.1)
        
        # エフェクトチェーン作成
        chain = (E.add(shape)
                  .noise(intensity=0.1)
                  .subdivision(n_divisions=0.2)
                  .scaling(scale=(0.8, 0.8, 0.8)))
        
        # チェーンプロパティの確認
        print(f"  チェーン表現: {chain}")
        print(f"  適用ステップ: {chain.steps()}")
        
        # 結果取得の複数方法をテスト
        result1 = chain.result()
        result2 = chain()
        result3 = chain.geometry
        
        print(f"  ✓ result()メソッド: {result1}")
        print(f"  ✓ ()呼び出し: {result2}")  
        print(f"  ✓ geometryプロパティ: {result3}")
        
        # 同じ結果かチェック（GUIDは違うが構造は同じはず）
        print(f"  結果の頂点数一致: {result1.num_points() == result2.num_points() == result3.num_points()}")
        
        return result1
        
    except Exception as e:
        print(f"  ✗ エフェクトチェーンプロパティテスト失敗: {e}")
        return None

def test_available_effects():
    """利用可能エフェクトのリスト表示"""
    print_separator("利用可能エフェクトリスト")
    
    try:
        effects = E.list_effects()
        
        print("  標準エフェクト:")
        for effect in effects["standard"]:
            print(f"    - {effect}")
            
        print("  カスタムエフェクト:")
        for effect in effects["custom"]:
            print(f"    - {effect}")
            
        print(f"  ✓ 合計 {len(effects['standard']) + len(effects['custom'])} 個のエフェクトが利用可能")
        
    except Exception as e:
        print(f"  ✗ エフェクトリスト取得失敗: {e}")

def main():
    """メインテスト実行"""
    print("EffectChain実装動作確認テスト開始")
    print("=" * 60)
    
    # 各テストを実行
    test_results = []
    
    # 1. 基本的なエフェクトチェーンテスト
    result1 = test_basic_effect_chain()
    test_results.append(("基本エフェクト", result1 is not None))
    
    # 2. 複数エフェクト連鎖テスト
    result2 = test_multiple_effects()
    test_results.append(("複数エフェクト連鎖", result2 is not None))
    
    # 3. カスタムエフェクトテスト
    result3 = test_custom_effect()
    test_results.append(("カスタムエフェクト", result3 is not None))
    
    # 4. apply関数テスト
    result4 = test_apply_function()
    test_results.append(("apply関数", result4 is not None))
    
    # 5. エフェクトチェーンプロパティテスト
    result5 = test_effect_chain_properties()
    test_results.append(("チェーンプロパティ", result5 is not None))
    
    # 6. 利用可能エフェクトリスト
    test_available_effects()
    
    # 結果サマリー
    print_separator("テスト結果サマリー")
    
    passed = 0
    total = len(test_results)
    
    for test_name, success in test_results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"  {test_name}: {status}")
        if success:
            passed += 1
    
    print(f"\n合計: {passed}/{total} テストが成功")
    
    if passed == total:
        print("\n🎉 すべてのテストが成功しました！")
        print("EffectChain実装は正常に動作しています。")
    else:
        print(f"\n⚠️  {total - passed} 個のテストが失敗しました。")
        print("実装に問題がある可能性があります。")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)