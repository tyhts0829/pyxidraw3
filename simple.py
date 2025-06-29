import arc

from api import E, G
from api.runner import run_sketch
from util.constants import CANVAS_SIZES


def draw(t, cc):
    """PyxiDraw次期API仕様の全機能デモ"""
    pl = (
        E.pipeline.subdivision(n_divisions=cc[1])
        .noise(intensity=cc[2])
        .rotation(center=(100, 100, 0), rotate=(cc[3], cc[3], cc[3]))
    )
    sphere = G.sphere(subdivisions=cc[6], sphere_type=cc[2]).size(80, 80, 80).at(50, 50, 0)
    sphere = pl(sphere)

    poly = G.polyhedron().size(80, 80, 80).at(150, 50, 0).rotate(0, 0, 0, center=(150, 50, 0))
    poly = pl(poly)
    return poly + sphere


if __name__ == "__main__":
    arc.start(midi=False)  # MIDIを無効化してテスト
    run_sketch(draw, canvas_size=CANVAS_SIZES["SQUARE_200"], render_scale=8, background=(1, 1, 1, 1))
    arc.stop()
