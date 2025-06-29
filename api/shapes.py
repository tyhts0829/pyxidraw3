from __future__ import annotations

from typing import Any

from api.geometry_api import GeometryAPI
from shapes import ShapeFactory

# グローバル形状ファクトリインスタンス
_factory = ShapeFactory()

# ==================================================================================
# GeometryAPIラッピング設計メモ
# ==================================================================================
#
# このモジュールでは、ShapeFactoryから返されるGeometryDataを即座にGeometryAPIで
# ラップしています。このタイミングでのラッピングを選択した理由：
#
# 【検討した代替案】
# 1. 形状生成レベル (shapes/base.py):
#    - メリット: より一貫したAPIフロー
#    - デメリット: 形状層がAPI層に依存（アーキテクチャ違反）
#
# 2. ShapeFactoryレベル (shapes/factory.py):
#    - メリット: キャッシュの粒度が適切
#    - デメリット: キャッシュサイズ増加、管理複雑化
#
# 3. エフェクトチェーン内統一 (api/effect_chain.py):
#    - メリット: 変換オーバーヘッド減少
#    - デメリット: 既存エフェクトの大幅変更が必要
#
# 4. レイジーラッピング（遅延ラッピング）:
#    - メリット: パフォーマンス最適化
#    - デメリット: 実装・デバッグの複雑化
#
# 【現在のアプローチ（api/shapes.py）が最適な理由】
# 1. 明確な責任分離: GeometryData(データ) → GeometryAPI(ユーザーAPI)
# 2. 適切なキャッシュ戦略: 軽量なGeometryDataをキャッシュ
# 3. 拡張性: 各層の変更が他層に影響しない
# 4. 実用的パフォーマンス: ラッピングオーバーヘッドは問題なし
#
# このアーキテクチャにより、ユーザーは形状生成後に即座に
# .size(), .at(), .spin() などのメソッドチェーンを使用可能。
# ==================================================================================


def polygon(
    n_sides: int | float = 3,
    center: tuple[float, float, float] = (0, 0, 0),
    scale: tuple[float, float, float] = (1, 1, 1),
    rotate: tuple[float, float, float] = (0, 0, 0),
    **params: Any,
) -> GeometryAPI:
    """正多角形を生成します。

    Args:
        n_sides: 辺の数。浮動小数点の場合0-100から指数的にマップ。
        center: 位置オフセット (x, y, z)
        scale: スケール係数 (x, y, z)
        rotate: 回転角度（ラジアン） (x, y, z)
        **params: 追加パラメータ

    Returns:
        正多角形の頂点を含むGeometryAPI
    """
    shape = _factory.create("polygon")
    geometry_data = shape(n_sides=n_sides, center=center, scale=scale, rotate=rotate, **params)
    return GeometryAPI(geometry_data)


def sphere(
    subdivisions: float = 0.5,
    sphere_type: float = 0.5,
    center: tuple[float, float, float] = (0, 0, 0),
    scale: tuple[float, float, float] = (1, 1, 1),
    rotate: tuple[float, float, float] = (0, 0, 0),
    **params: Any,
) -> GeometryAPI:
    """球体を生成します。

    Args:
        subdivisions: 細分化レベル (0.0-1.0、0-5にマップ)
        sphere_type: 描画スタイル (0.0-1.0):
                    0.0-0.2: 経緯線（デフォルト）
                    0.2-0.4: ワイヤーフレーム
                    0.4-0.6: ジグザグ
                    0.6-0.8: 正二十面体
                    0.8-1.0: リング
        center: 位置オフセット (x, y, z)
        scale: スケール係数 (x, y, z)
        rotate: 回転角度（ラジアン） (x, y, z)
        **params: 追加パラメータ

    Returns:
        球体の頂点を含むGeometryAPI
    """
    shape = _factory.create("sphere")
    geometry_data = shape(
        subdivisions=subdivisions, sphere_type=sphere_type, center=center, scale=scale, rotate=rotate, **params
    )
    return GeometryAPI(geometry_data)


def grid(
    n_divisions: tuple[float, float] = (0.1, 0.1),
    center: tuple[float, float, float] = (0, 0, 0),
    scale: tuple[float, float, float] = (1, 1, 1),
    rotate: tuple[float, float, float] = (0, 0, 0),
    **params: Any,
) -> GeometryAPI:
    """グリッドを生成します。

    Args:
        n_divisions: (x_divisions, y_divisions) 0.0-1.0の浮動小数点
        center: 位置オフセット (x, y, z)
        scale: スケール係数 (x, y, z)
        rotate: 回転角度（ラジアン） (x, y, z)
        **params: 追加パラメータ

    Returns:
        グリッド線の頂点を含むGeometryAPI
    """
    shape = _factory.create("grid")
    geometry_data = shape(n_divisions=n_divisions, center=center, scale=scale, rotate=rotate, **params)
    return GeometryAPI(geometry_data)


def polyhedron(
    polygon_type: str | int = "tetrahedron",
    center: tuple[float, float, float] = (0, 0, 0),
    scale: tuple[float, float, float] = (1, 1, 1),
    rotate: tuple[float, float, float] = (0, 0, 0),
    **params: Any,
) -> GeometryAPI:
    """正多面体を生成します。

    Args:
        polygon_type: 多面体のタイプ（名前または面の数）
        center: 位置オフセット (x, y, z)
        scale: スケール係数 (x, y, z)
        rotate: 回転角度（ラジアン） (x, y, z)
        **params: 追加パラメータ

    Returns:
        多面体の端の頂点を含むGeometryAPI
    """
    shape = _factory.create("polyhedron")
    geometry_data = shape(polygon_type=polygon_type, center=center, scale=scale, rotate=rotate, **params)
    return GeometryAPI(geometry_data)


def lissajous(
    freq_x: float = 3.0,
    freq_y: float = 2.0,
    phase: float = 0.0,
    points: int = 1000,
    center: tuple[float, float, float] = (0, 0, 0),
    scale: tuple[float, float, float] = (1, 1, 1),
    rotate: tuple[float, float, float] = (0, 0, 0),
    **params: Any,
) -> GeometryAPI:
    """リサージュ曲線を生成します。

    Args:
        freq_x: X軸の周波数
        freq_y: Y軸の周波数
        phase: 位相オフセット（ラジアン）
        points: 生成する点の数
        center: 位置オフセット (x, y, z)
        scale: スケール係数 (x, y, z)
        rotate: 回転角度（ラジアン） (x, y, z)
        **params: 追加パラメータ

    Returns:
        頂点を含むGeometryAPI
    """
    shape = _factory.create("lissajous")
    geometry_data = shape(
        freq_x=freq_x, freq_y=freq_y, phase=phase, points=points, center=center, scale=scale, rotate=rotate, **params
    )
    return GeometryAPI(geometry_data)


def torus(
    major_radius: float = 0.3,
    minor_radius: float = 0.1,
    major_segments: int = 32,
    minor_segments: int = 16,
    center: tuple[float, float, float] = (0, 0, 0),
    scale: tuple[float, float, float] = (1, 1, 1),
    rotate: tuple[float, float, float] = (0, 0, 0),
    **params: Any,
) -> GeometryAPI:
    """トーラスを生成します。

    Args:
        major_radius: 主半径（中心からチューブ中心まで）
        minor_radius: 副半径（チューブ半径）
        major_segments: 主円の周りのセグメント数
        minor_segments: 副円の周りのセグメント数
        center: 位置オフセット (x, y, z)
        scale: スケール係数 (x, y, z)
        rotate: 回転角度（ラジアン） (x, y, z)
        **params: 追加パラメータ

    Returns:
        トーラス線の頂点を含むGeometryAPI
    """
    shape = _factory.create("torus")
    geometry_data = shape(
        major_radius=major_radius,
        minor_radius=minor_radius,
        major_segments=major_segments,
        minor_segments=minor_segments,
        center=center,
        scale=scale,
        rotate=rotate,
        **params,
    )
    return GeometryAPI(geometry_data)


def cylinder(
    radius: float = 0.3,
    height: float = 0.6,
    segments: int = 32,
    center: tuple[float, float, float] = (0, 0, 0),
    scale: tuple[float, float, float] = (1, 1, 1),
    rotate: tuple[float, float, float] = (0, 0, 0),
    **params: Any,
) -> GeometryAPI:
    """円柱を生成します。

    Args:
        radius: 円柱の半径
        height: 円柱の高さ
        segments: 周囲のセグメント数
        center: 位置オフセット (x, y, z)
        scale: スケール係数 (x, y, z)
        rotate: 回転角度（ラジアン） (x, y, z)
        **params: 追加パラメータ

    Returns:
        円柱線の頂点を含むGeometryAPI
    """
    shape = _factory.create("cylinder")
    geometry_data = shape(
        radius=radius, height=height, segments=segments, center=center, scale=scale, rotate=rotate, **params
    )
    return GeometryAPI(geometry_data)


def cone(
    radius: float = 0.3,
    height: float = 0.6,
    segments: int = 32,
    center: tuple[float, float, float] = (0, 0, 0),
    scale: tuple[float, float, float] = (1, 1, 1),
    rotate: tuple[float, float, float] = (0, 0, 0),
    **params: Any,
) -> GeometryAPI:
    """円錐を生成します。

    Args:
        radius: 底面半径
        height: 円錐の高さ
        segments: 周囲のセグメント数
        center: 位置オフセット (x, y, z)
        scale: スケール係数 (x, y, z)
        rotate: 回転角度（ラジアン） (x, y, z)
        **params: 追加パラメータ

    Returns:
        円錐線の頂点を含むGeometryAPI
    """
    shape = _factory.create("cone")
    geometry_data = shape(
        radius=radius, height=height, segments=segments, center=center, scale=scale, rotate=rotate, **params
    )
    return GeometryAPI(geometry_data)


def capsule(
    radius: float = 0.2,
    height: float = 0.4,
    segments: int = 32,
    latitude_segments: int = 16,
    center: tuple[float, float, float] = (0, 0, 0),
    scale: tuple[float, float, float] = (1, 1, 1),
    rotate: tuple[float, float, float] = (0, 0, 0),
    **params: Any,
) -> GeometryAPI:
    """カプセル形状を生成します。

    Args:
        radius: 半球の半径
        height: 円柱部分の高さ
        segments: 曲線のセグメント数
        latitude_segments: 半球の緯度方向のセグメント数
        center: 位置オフセット (x, y, z)
        scale: スケール係数 (x, y, z)
        rotate: 回転角度（ラジアン） (x, y, z)
        **params: 追加パラメータ

    Returns:
        カプセル線の頂点を含むGeometryAPI
    """
    shape = _factory.create("capsule")
    geometry_data = shape(
        radius=radius,
        height=height,
        segments=segments,
        latitude_segments=latitude_segments,
        center=center,
        scale=scale,
        rotate=rotate,
        **params,
    )
    return GeometryAPI(geometry_data)


def attractor(
    attractor_type: str = "lorenz",
    points: int = 10000,
    dt: float = 0.01,
    center: tuple[float, float, float] = (0, 0, 0),
    scale: tuple[float, float, float] = (1, 1, 1),
    rotate: tuple[float, float, float] = (0, 0, 0),
    **params: Any,
) -> GeometryAPI:
    """ストレンジアトラクターを生成します。

    Args:
        attractor_type: アトラクターのタイプ ("lorenz"、"rossler"、"chua")
        points: 生成する点の数
        dt: 積分の時間ステップ
        center: 位置オフセット (x, y, z)
        scale: スケール係数 (x, y, z)
        rotate: 回転角度（ラジアン） (x, y, z)
        **params: 追加パラメータ

    Returns:
        頂点を含むGeometryAPI
    """
    shape = _factory.create("attractor")
    geometry_data = shape(
        attractor_type=attractor_type, points=points, dt=dt, center=center, scale=scale, rotate=rotate, **params
    )
    return GeometryAPI(geometry_data)


def text(
    text: str = "HELLO",
    size: float = 0.1,
    center: tuple[float, float, float] = (0, 0, 0),
    scale: tuple[float, float, float] = (1, 1, 1),
    rotate: tuple[float, float, float] = (0, 0, 0),
    **params: Any,
) -> GeometryAPI:
    """テキストを線分として生成します。

    Args:
        text: レンダリングするテキスト文字列
        size: テキストサイズ
        center: 位置オフセット (x, y, z)
        scale: スケール係数 (x, y, z)
        rotate: 回転角度（ラジアン） (x, y, z)
        **params: 追加パラメータ

    Returns:
        テキストアウトラインの頂点を含むGeometryAPI
    """
    shape = _factory.create("text")
    geometry_data = shape(text=text, size=size, center=center, scale=scale, rotate=rotate, **params)
    return GeometryAPI(geometry_data)


def asemic_glyph(
    complexity: int = 5,
    seed: int | None = None,
    center: tuple[float, float, float] = (0, 0, 0),
    scale: tuple[float, float, float] = (1, 1, 1),
    rotate: tuple[float, float, float] = (0, 0, 0),
    **params: Any,
) -> GeometryAPI:
    """抽象的なグリフ状の形状を生成します。

    Args:
        complexity: ストローク数 (1-10)
        seed: 再現性のためのランダムシード
        center: 位置オフセット (x, y, z)
        scale: スケール係数 (x, y, z)
        rotate: 回転角度（ラジアン） (x, y, z)
        **params: 追加パラメータ

    Returns:
        グリフストロークの頂点を含むGeometryAPI
    """
    shape = _factory.create("asemic_glyph")
    geometry_data = shape(complexity=complexity, seed=seed, center=center, scale=scale, rotate=rotate, **params)
    return GeometryAPI(geometry_data)
