#!/usr/bin/env python3
"""
チュートリアル 01: 基本的な形状の生成

PyxiDrawの基本的な使い方を学びます。
シンプルな形状を生成して表示します。
"""
from api import G
from api.runner import run_sketch
from util.constants import CANVAS_SIZES


def draw(t, cc):
    """
    基本的な形状を生成する関数

    Args:
        t: 時間（フレーム番号）
        cc: MIDIコントローラーの値（辞書形式）

    Returns:
        GeometryAPI: 描画する形状
    """
    # 1. 球体を生成
    # subdivisions: 細分化レベル（0-1の範囲）
    sphere = G.sphere(subdivisions=0.3)

    # 2. サイズを設定（x, y, z）
    sphere = sphere.size(100, 100, 100)

    # 3. 位置を設定（x, y, z）
    sphere = sphere.at(200, 200, 0)

    return sphere


def main():
    run_sketch(draw, canvas_size=CANVAS_SIZES["SQUARE_400"])


if __name__ == "__main__":
    main()
