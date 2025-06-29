import arc

from api.effects import filling, noise, rotation, subdivision
from api.runner import run_sketch
from api.shapes import sphere
from engine.core.geometry import Geometry
from util.constants import CANVAS_SIZES


def draw(t, cc) -> Geometry:
    # 新アーキテクチャ：API層で形状生成
    sph = sphere(subdivisions=cc[1], sphere_type=cc[2], center=(100, 100, 0), scale=(100, 100, 100))

    # API層のエフェクトを使用
    sph = rotation(sph, center=(100, 100, 0), rotate=(cc[3], cc[3], cc[3]))
    sph = filling(sph, density=cc[4])
    sph = subdivision(sph, n_divisions=cc[5])
    sph = noise(sph, intensity=cc[6])

    return sph


if __name__ == "__main__":
    arc.start(midi=False)  # MIDIを無効化してテスト
    run_sketch(draw, canvas_size=CANVAS_SIZES["SQUARE_200"], render_scale=8, background=(1, 1, 1, 1))
    arc.stop()
