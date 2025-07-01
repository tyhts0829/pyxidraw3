#!/usr/bin/env python3
"""
チュートリアル 03: 基本的なエフェクトの適用

形状にエフェクトを適用して、変形や装飾を行います。
エフェクトチェーンの基本的な使い方を学びます。
"""

import arc
from api import E, G
from api.runner import run_sketch
from util.constants import CANVAS_SIZES


def draw(t, cc):
    """
    エフェクトを適用した形状を生成
    
    Args:
        t: 時間（フレーム番号）
        cc: MIDIコントローラーの値
    
    Returns:
        GeometryAPI: エフェクトを適用した形状
    """
    # 時間による動的な値を計算
    time_factor = t * 0.01
    
    # 基本となる立方体を生成
    base_shape = G.polyhedron(name="cube").size(100, 100, 100).at(200, 200, 0)
    
    # エフェクトチェーンを適用
    result = E.add(base_shape)
    
    # 1. ノイズエフェクト（形状に揺らぎを追加）
    # intensity: ノイズの強度（0-1）
    result = result.noise(intensity=0.2)
    
    # 2. 回転エフェクト（時間とともに回転）
    # x, y, z: 各軸の回転角度（度）
    result = result.rotate(
        x=time_factor * 30,  # X軸回りに回転
        y=time_factor * 45,  # Y軸回りに回転
        z=0
    )
    
    # 3. スケールエフェクト（脈動するような効果）
    # 三角関数を使って滑らかに変化
    import math
    scale_factor = 1.0 + 0.2 * math.sin(time_factor)
    result = result.scale(
        x=scale_factor,
        y=scale_factor,
        z=scale_factor
    )
    
    # 4. 細分化エフェクト（滑らかな表面に）
    # algorithm: 細分化アルゴリズム（catmull-clark, loop, butterfly）
    # iterations: 細分化の回数
    result = result.subdivide(
        algorithm="catmull-clark",
        iterations=1
    )
    
    # 5. 結果を取得
    return result.result()


def draw_comparison(t, cc):
    """
    エフェクト適用前後の比較表示
    """
    # 左側：エフェクトなし
    original = G.polyhedron(name="cube").size(80, 80, 80).at(150, 200, 0)
    
    # 右側：エフェクトあり
    effected = G.polyhedron(name="cube").size(80, 80, 80).at(250, 200, 0)
    effected = E.add(effected)\
        .noise(intensity=0.3)\
        .rotate(x=45, y=45)\
        .subdivide(iterations=1)\
        .result()
    
    # 両方を組み合わせて返す
    return G.empty().add(original).add(effected)


def main():
    """メイン実行関数"""
    print("=== チュートリアル 03: 基本的なエフェクトの適用 ===")
    print("立方体に様々なエフェクトを適用します：")
    print("- ノイズ：形状に揺らぎを追加")
    print("- 回転：時間とともに回転")
    print("- スケール：脈動するような拡大縮小")
    print("- 細分化：滑らかな表面に変換")
    print("\n終了するには Ctrl+C を押してください")
    
    arc.start(midi=False)
    
    # 動的なエフェクトを表示
    run_sketch(draw, canvas_size=CANVAS_SIZES["SQUARE_400"])
    
    # 比較表示も可能（コメントを外して実行）
    # run_sketch(draw_comparison, canvas_size=CANVAS_SIZES["SQUARE_400"])
    
    arc.stop()


if __name__ == "__main__":
    main()