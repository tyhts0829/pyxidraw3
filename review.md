課題
現在、engine/core/geometry.py の Geometry クラスは描画データ（頂点や線分オフセット）の管理のみならず、図形生成（正多角形、球、文字など）や**各種変形エフェクト（回転、拡大縮小、ノイズ付加など）**まで一手に担っています（例：Geometry.polygon() で API 側の api.shapes.polygon を呼び出し
GitHub
GitHub
、Geometry.scale() で api.effects.scaling を呼び出す
GitHub
）。つまり、エンジン層（engine/core）にありながら、API 層（api/）や形状／エフェクト層（/shapes、/effects）に依存しており、本来の層構造を侵害しています。
例えばリポジトリの設計ガイドにも「4 層アーキテクチャ（API 層、エンジン層、形状・エフェクト層、ユーティリティ層）を採用する」ことが明示されており
GitHub
GitHub
、API 層はあくまで高レベル呼び出しを束ねる役割とされています。しかし現状では Geometry クラスが API に直接依存しており、エンジン（中核データ構造）と API（ユーザー向けラッパー）の境界が曖昧になっています。これはコードの可読性・保守性・テスト性を低下させる原因です。

以下では、破壊的変更を許容して Geometry の責務過多・密結合を解消するために、実際のコードベースを段階的に変更していく具体的な手順とサンプル実装を提示します。
（diff は gist ではなく概要的な抜粋です。行番号は便宜上。）

フェーズ 1 : コアデータ構造の抽出

1-1. GeometryData クラス新設
engine/core/geometry_data.py を追加します。

# engine/core/geometry_data.py

from **future** import annotations
import numpy as np
from typing import Any, Tuple

class GeometryData:
"""頂点列とオフセット列だけを保持する純粋データコンテナ。"""

    __slots__ = ("coords", "offsets")

    def __init__(self, coords: np.ndarray, offsets: np.ndarray):
        # shape: (N, 3), dtype=float32   /   (M,), int32
        self.coords = coords.astype(np.float32, copy=False)
        self.offsets = offsets.astype(np.int32, copy=False)

    # --- データ操作（副作用なし） ------------------
    def copy(self) -> "GeometryData":
        return GeometryData(self.coords.copy(), self.offsets.copy())

    def concat(self, other: "GeometryData") -> "GeometryData":
        """別ジオメトリと連結した新インスタンスを返す。"""
        off_shift = self.coords.shape[0]
        new_coords = np.vstack([self.coords, other.coords])
        new_offsets = np.hstack([self.offsets, other.offsets + off_shift])
        return GeometryData(new_coords, new_offsets)

    # 以降、データフォーマット変換ユーティリティなど……

ポイント
API/エフェクト/形状を一切 import しない。
元の Geometry.coords, Geometry.offsets のみを残し、変形処理は呼び出さない。

1-2. 既存 Geometry からデータ部を切り離す
engine/core/geometry.py からデータ保持ロジックを削除し、代わりに GeometryData を内部委譲する薄いラッパーとします（後方互換用）。

-class Geometry:

- def **init**(self, coords, offsets):
-        self.coords = np.asarray(coords, dtype=np.float32)
-        self.offsets = np.asarray(offsets, dtype=np.int32)
  +from engine.core.geometry_data import GeometryData

* +class Geometry:
* """旧 API との互換レイヤ。内部では GeometryData を保持。"""
*
* def **init**(self, coords, offsets):
*        self._data = GeometryData(coords, offsets)
*
* # プロパティとして提供
* @property
* def coords(self): return self.\_data.coords
* @property
* def offsets(self): return self.\_data.offsets
  可動確認：既存テストやサンプルを実行し、描画結果が変わらないことを確かめてフェーズ 1 を完了。

フェーズ 2 : 変換ユーティリティとエフェクト層の分離

2-1. transform_utils.py 追加
engine/core/transform_utils.py:
import numpy as np
from .geometry_data import GeometryData

def translate(g: GeometryData, dx: float, dy: float, dz: float = 0) -> GeometryData:
vec = np.array([dx, dy, dz], dtype=np.float32)
return GeometryData(g.coords + vec, g.offsets)

def scale_uniform(g: GeometryData, factor: float) -> GeometryData:
return GeometryData(g.coords \* factor, g.offsets)

def rotate_z(g: GeometryData, angle_rad: float, center=(0, 0)) -> GeometryData:
c, s = np.cos(angle_rad), np.sin(angle_rad)
cx, cy = center
pts = g.coords.copy()
pts[:, :2] -= (cx, cy)
pts[:, :2] = pts[:, :2] @ np.array([[c, -s], [s, c]], dtype=np.float32)
pts[:, :2] += (cx, cy)
return GeometryData(pts, g.offsets)
後工程で Numba などによる JIT 高速化がしやすい分離とする。

2-2. 旧 Geometry.translate() などの内部実装を書き換え
-from api.effects import translation
-def translate(self, x, y, z=0):

- return translation(self, x, y, z)
  +from engine.core import transform_utils as \_tf
  +def translate(self, x, y, z=0):

* new_data = \_tf.translate(self.\_data, x, y, z)
* return Geometry.from_data(new_data)
  ここで Geometry.from_data は薄いファクトリメソッド:
  @classmethod
  def from_data(cls, data: GeometryData) -> "Geometry":
  obj = cls.**new**(cls)
  obj.\_data = data
  return obj
  同様に rotate, scale 系をすべて transform_utils 呼び出しに差し替え。

フェーズ 3 : 形状生成ロジックの独立

3-1. /shapes/ モジュールへ移動
例：shapes/polygon.py
import numpy as np
from engine.core.geometry_data import GeometryData

def polygon(n_sides: int, radius: float = 1.0, center=(0, 0)) -> GeometryData:
angles = np.linspace(0, 2 _ np.pi, n_sides, endpoint=False, dtype=np.float32)
pts = np.stack([np.cos(angles), np.sin(angles), np.zeros_like(angles)], axis=1)
pts[:, :2] = pts[:, :2] _ radius + np.asarray(center, dtype=np.float32)
offsets = np.array([0], dtype=np.int32)
return GeometryData(pts, offsets)
3-2. api/shapes.py でユーザー向け関数を再エクスポート

from shapes.polygon import polygon as \_polygon
from engine.core.geometry import Geometry

def polygon(n, radius=1.0, center=(0,0)):
return Geometry.from_data(\_polygon(n, radius, center))
レイヤー準拠：api は shapes と engine には依存するが、その逆依存はない。

フェーズ 4 : キャッシュ機構の切り出し

変形キャッシュは エフェクト層に付与。
effects/base.py へ簡易 LRU デコレータを配置し、各エフェクト関数 (scale_uniform, translate, rotate_z など) を修飾。
GeometryData 側からキャッシュ辞書・ハッシュ計算を削除して軽量化。
フェーズ 5 : 後方互換 API の整理と段階的削除

Geometry.at = Geometry.translate、Geometry.size = Geometry.scale_uniform といった エイリアスを残す。
warnings.warn で「今後 vX.Y で非推奨予定」と明示。
ドキュメント・サンプルコードを新 API に更新。古い呼び出しを検索して直しやすいようチェッカー（flake8 プラグイン等）を提供。

フェーズ 6 : テスト・CI 強化

snapshot-test：旧ビルドとの比較用に、代表的スケッチを描画 → 頂点バッファを NumPy 保存 → リファクタ後に数値差分が 1e-5 以内か比較。
ユニットテスト：
GeometryData.concat など純粋関数をパラメトリックに網羅。
transform_utils 各関数で行列変換の真値と比較。
CI（GitHub Actions）で Python 3.11/3.12 環境＋ macOS/Linux で走らせる。

まとめ：メリットと見積もり

項目 効果
依存方向が一方通行 engine ← shapes / effects ← api ← ユーザーコード となり、テスト単位でモック化容易。
クラス肥大の解消 旧 Geometry 2,000 行 → 約 200 行の薄いラッパー。変換ロジックは transform_utils へ分散。
高速化余地 変換関数だけを Numba/JAX で JIT すると、エンジン層全体に波及せず最適化可能。
学習コスト低減 ユーザーは API レイヤだけを覚えればよく、エンジン内部を気にせずに済む。

これらを順守することで、Geometry クラスの責務集中問題を解消し、長期運用に耐えうるクリーンアーキテクチャ へ移行できます。
