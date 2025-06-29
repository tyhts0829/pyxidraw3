import arc

from api import E, G
from api.runner import run_sketch
from util.constants import CANVAS_SIZES


def draw(t, cc):
    """複数のエフェクトをテストするスケッチ"""

    array = G.polyhedron().size(50, 50, 50)
    return array

    # テストするエフェクトをリストで指定
    target_effects = ["array", "noise", "filling"]

    shapes = []
    spacing = 200 / len(target_effects)  # エフェクトの数に応じて等間隔に配置

    for i, effect_name in enumerate(target_effects):
        x_pos = spacing * (i + 0.5)  # 等間隔に配置

        # 基本の形状を作成（多面体）
        shape = G.polyhedron(polyhedron_type=0.0).size(30, 30, 30).at(x_pos, 100, 0)

        # エフェクトを適用
        if effect_name == "array":
            # arrayエフェクト: 形状を複製して配列化
            shape = (
                E.add(shape)
                .array(
                    n_duplicates=0.3,  # 複製数の係数（3個程度）
                    offset=(15, 15, 0),  # 各複製間のオフセット
                    rotate=(0.5, 0.5, 0.5),  # 回転は中立
                    scale=(1.0, 1.0, 1.0),  # スケールは変更なし
                )
                .result()
            )

        elif effect_name == "noise":
            # noiseエフェクト: ノイズを追加
            shape = (
                E.add(shape)
                .noise(intensity=0.3, frequency=2.0, t=0.0)  # 固定値に変更  # ノイズの周波数  # 時間パラメータ
                .result()
            )

        elif effect_name == "filling":
            # fillingエフェクト: 塗りつぶしパターンを追加
            shape = (
                E.add(shape)
                .filling(
                    pattern="lines", density=0.8, angle=0.785  # ラインパターン  # 塗りつぶし密度  # 45度（ラジアン）
                )
                .result()
            )

        shapes.append(shape)

    # すべての形状を結合して返す
    result = shapes[0]
    for shape in shapes[1:]:
        result = result + shape

    return result


if __name__ == "__main__":
    arc.start(midi=False)  # MIDIを無効化してテスト
    run_sketch(draw, canvas_size=CANVAS_SIZES["SQUARE_200"], render_scale=8, background=(1, 1, 1, 1))
    arc.stop()
