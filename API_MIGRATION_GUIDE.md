# シェイプAPI移行ガイド

## 概要

PyxiDrawのシェイプAPIが統一され、高性能化されました。新しい `G` インターフェースをご利用ください。

## 旧APIから新APIへの移行

### 基本的な変更

```python
# 旧API（非推奨）
from api.shapes import polygon, sphere, grid
poly = polygon(n_sides=6)
sph = sphere(subdivisions=0.5)

# 新API（推奨）
from api import G
poly = G.polygon(n_sides=6)  
sph = G.sphere(subdivisions=0.5)
```

### インポート文の変更

| 旧API | 新API |
|-------|-------|
| `from api.shapes import polygon` | `from api import G` |
| `from api.shapes import *` | `from api import G` |
| `import api.shapes` | `from api import G` |

### 関数呼び出しの変更

| 旧API | 新API |
|-------|-------|
| `polygon(n_sides=6)` | `G.polygon(n_sides=6)` |
| `sphere(subdivisions=0.5)` | `G.sphere(subdivisions=0.5)` |
| `grid(n_divisions=(0.2, 0.2))` | `G.grid(divisions=0.2)` * |
| `text(text="Hello")` | `G.text(text_content="Hello")` * |

*パラメータ名が変更された関数があります。詳細は下記参照。

## パラメータ変更の詳細

### 1. grid関数
```python
# 旧API
grid(n_divisions=(0.2, 0.2))

# 新API  
G.grid(divisions=0.2)  # 単一値の場合
# または
G.grid(divisions=(0.2, 0.3))  # 異なるx,y分割の場合（内部で変換）
```

### 2. text関数
```python
# 旧API
text(text="Hello", size=0.1)

# 新API
G.text(text_content="Hello", size=0.1)
```

### 3. polyhedron関数
```python
# 旧API
polyhedron(polygon_type="tetrahedron")

# 新API
G.polyhedron(polyhedron_type=0.0)  # 数値指定に変更
```

## 新APIの利点

### 1. 高性能キャッシュ
```python
from api import G

# 同じパラメータでの呼び出しはキャッシュされます
sphere1 = G.sphere(subdivisions=0.5)  # 初回計算
sphere2 = G.sphere(subdivisions=0.5)  # キャッシュヒット（高速）

# キャッシュ情報の確認
print(G.cache_info())  # CacheInfo(hits=1, misses=1, maxsize=128, currsize=1)
```

### 2. 統一されたインターフェース
```python
# すべての形状が G.* で統一
shapes = [
    G.polygon(n_sides=6),
    G.sphere(subdivisions=0.5),
    G.grid(divisions=0.3),
    G.cylinder(radius=0.5),
    G.torus(major_radius=0.4),
    G.text(text_content="PyxiDraw"),
]
```

### 3. メソッドチェーン対応
```python
# 形状生成とメソッドチェーンが連携
result = (G.sphere(subdivisions=0.5)
          .size(100, 100, 100) 
          .at(200, 200, 0)
          .rotate(0.5, 0, 0))
```

## 移行チェックリスト

- [ ] `from api.shapes import` を `from api import G` に変更
- [ ] 関数呼び出しを `function()` から `G.function()` に変更  
- [ ] `grid` の `n_divisions` → `divisions` に変更
- [ ] `text` の `text` → `text_content` に変更
- [ ] `polyhedron` のパラメータを数値に変更（必要に応じて）
- [ ] 動作テストを実行
- [ ] 非推奨警告が出ていないことを確認

## 移行期間中の対応

### 非推奨警告への対応
移行期間中は旧APIも動作しますが、警告が表示されます：

```python
# 旧APIを使用すると警告が表示される
import warnings
warnings.simplefilter('always', DeprecationWarning)

from api.shapes import polygon
poly = polygon(n_sides=6)
# DeprecationWarning: api.shapes.polygon() is deprecated. Use G.polygon() instead.
```

### 段階的移行
大きなコードベースでは段階的に移行できます：

```python
# 一時的な混在も可能
from api import G
from api.shapes import polygon  # 旧API（警告付き）

# 新しいコードはG.*を使用
new_sphere = G.sphere(subdivisions=0.5)

# 既存コードは徐々に移行
old_polygon = polygon(n_sides=6)  # 警告が出るが動作する
```

## トラブルシューティング

### よくある問題

1. **ImportError: G が見つからない**
   ```python
   # 解決策: 正しいインポート
   from api import G
   ```

2. **TypeError: 予期しないパラメータ**
   ```python
   # 問題: パラメータ名の変更
   G.grid(n_divisions=0.2)  # ❌
   
   # 解決策: 新しいパラメータ名を使用
   G.grid(divisions=0.2)    # ✅
   ```

3. **AttributeError: G にメソッドがない**
   ```python
   # 確認: 利用可能な形状一覧
   print(dir(G))
   # または
   help(G)
   ```

## 参考リンク

- [PyxiDraw API リファレンス](./pyxidraw_api_spec.md)
- [移行完了報告書](./shape_api_migration_report.md)
- [リファクタリング計画書](./shape_api_refactoring_plan.md)

## サポート

移行に関する質問や問題がある場合は、GitHubのIssueでお知らせください。