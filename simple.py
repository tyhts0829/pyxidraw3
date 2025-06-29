import arc

from api import E, G
from api.runner import run_sketch
from util.constants import CANVAS_SIZES


def draw(t, cc):
    """PyxiDraw次期API仕様の全機能デモ"""
    sphere = G.sphere(subdivisions=cc[1], sphere_type=cc[2]).size(80, 80, 80).at(50, 50, 0).rotate(cc[3], cc[3], cc[3])
    sphere = (
        E.add(sphere).subdivision(n_divisions=cc[4]).noise(intensity=cc[5] * 0.5).filling(density=cc[6] * 0.8).result()
    )

    poly = G.polyhedron().size(80, 80, 80).at(150, 50, 0).rotate(0, 0, 0, center=(150, 50, 0))
    poly = E.add(poly).buffer(distance=cc[7]).result()
    return poly + sphere


if __name__ == "__main__":
    arc.start(midi=False)  # MIDIを無効化してテスト
    run_sketch(draw, canvas_size=CANVAS_SIZES["SQUARE_200"], render_scale=8, background=(1, 1, 1, 1))
    arc.stop()
