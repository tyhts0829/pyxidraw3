import arc

from api import E, G
from api.runner import run_sketch
from util.constants import CANVAS_SIZES


def draw(t, cc):
    """PyxiDraw次期API仕様の全機能デモ"""
    # デフォルト値を設定
    subdivision_val = cc.get(1, 0.5)
    noise_intensity = cc.get(2, 0.3)
    rotation_val = cc.get(3, 0.1)
    sphere_subdivisions = cc.get(6, 0.5)

    pl = (
        E.pipeline.subdivision(n_divisions=subdivision_val)
        .noise(intensity=noise_intensity)
        .rotation(center=(100, 100, 0), rotate=(rotation_val, rotation_val, rotation_val))
    )
    sphere = G.sphere(subdivisions=sphere_subdivisions, sphere_type=noise_intensity).size(80, 80, 80)
    sphere = sphere.at(50, 50, 0)
    sphere = pl(sphere)

    poly = G.polyhedron().size(80, 80, 80).at(150, 50, 0).rotate(0, 0, 0, center=(150, 50, 0))
    poly = pl(poly)
    return poly + sphere


if __name__ == "__main__":
    arc.start(midi=False)  # MIDIを無効化してテスト
    run_sketch(draw, canvas_size=CANVAS_SIZES["SQUARE_200"], render_scale=8, background=(1, 1, 1, 1))
    arc.stop()
