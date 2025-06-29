# シェイプ API の二重化問題　解決実装手順

## 問題の確認結果

**指摘は正しい**：以下の通り、同じ機能を持つ2つのAPIが存在し、重複している。

### 現状の問題点

1. **api/shapes.py**：ラッパー関数形式の古いAPI
   - `polygon()`, `sphere()`, `grid()` などの関数
   - 内部で `shapes.ShapeFactory` を使用
   - 各関数が `GeometryAPI` でラップして返却

2. **api/shape_factory.py**：新しいShapeFactoryクラス（G）
   - `G.polygon()`, `G.sphere()`, `G.grid()` などのクラスメソッド
   - 高性能なLRUキャッシュ機能付き
   - 同じく `GeometryAPI` でラップして返却

3. **shapes/factory.py**：元のShapeFactoryクラス
   - インスタンス作成型のファクトリー
   - キャッシュ機能なし

## 解決方針

**api/shape_factory.py（G）を正式APIとし、api/shapes.pyを段階的に廃止する**

## 実装手順

### Phase 1: 互換性レイヤーの作成

1. **api/shapes.py を薄いラッパーに変更**
   ```python
   # 各関数を G.* への単純な転送に変更
   def polygon(**kwargs):
       return G.polygon(**kwargs)
   ```

2. **非推奨警告の追加**
   ```python
   import warnings
   
   def polygon(**kwargs):
       warnings.warn(
           "api.shapes.polygon() is deprecated. Use G.polygon() instead.",
           DeprecationWarning,
           stacklevel=2
       )
       return G.polygon(**kwargs)
   ```

### Phase 2: 使用箇所の移行

1. **全体検索で api/shapes.py の使用箇所を特定**
   ```bash
   grep -r "from api.shapes import" .
   grep -r "import api.shapes" .
   ```

2. **各使用箇所を G.* に変更**
   - `from api.shapes import polygon` → `from api.shape_factory import G`
   - `polygon(...)` → `G.polygon(...)`

3. **テストケースの更新**
   - 既存テストを G.* に移行
   - 非推奨警告のテストも追加

### Phase 3: 完全移行

1. **shapes/factory.py の整理**
   - 不要になったクラスは削除検討
   - または内部実装専用として保持

2. **api/shapes.py の完全削除**
   - 非推奨期間（2-3マイナーバージョン）後に削除
   - CHANGELOG でbreaking changeとして告知

## 移行の利点

1. **パフォーマンス向上**：LRUキャッシュによる高速化
2. **API統一**：`G.shape_name()` の一貫した命名
3. **保守性向上**：重複コードの削除
4. **拡張性**：キャッシュ管理機能（`clear_cache()`, `cache_info()`）

## 実装時の注意点

1. **パラメータ互換性の確認**
   - 既存APIとの引数名・型の違いを調査
   - 必要に応じて互換性レイヤーで調整

2. **デフォルト値の統一**
   - 両APIでデフォルト値が異なる場合は統一

3. **テストカバレッジの維持**
   - 移行前後で同じテスト結果を保証

## 実装優先度

**高**：Phase 1（互換性レイヤー）→ 即座に実装可能
**中**：Phase 2（使用箇所移行）→ 計画的に実施
**低**：Phase 3（完全削除）→ 将来のメジャーバージョンアップ時