# 変数名の揺れ - コードレビュー指摘事項

## 概要
コードベースにおいて同一概念を表す変数名に揺れが散見されます。以下に該当箇所をリストアップし、改善計画を示します。

## 1. divisions vs n_divisions vs subdivisions

### 問題のある箇所
- `shapes/grid.py:53` - `n_divisions` パラメータ使用
- `shapes/grid.py:86` - `n_divisions` パラメータ使用  
- `shapes/sphere.py:14,55,96,110,128,169,246,266` - `subdivisions` パラメータ使用
- `effects/extrude.py:25,46` - `subdivisions` パラメータ使用

### 推奨統一名
`subdivisions` に統一（3D形状の分割概念により適している）

## 2. offset_x/offset_y vs dx/dy

### 問題のある箇所
- `effects/translation.py:23-25` - `offset_x`, `offset_y`, `offset_z` 使用
- `effects/boldify.py:22-23` - `dx`, `dy` を内部計算で使用

### 推奨統一名
`offset_x`, `offset_y`, `offset_z` に統一（オフセットの意味がより明確）

## 3. points vs n_points

### 問題のある箇所
- `shapes/sphere.py:137` - `n_points` 使用
- `shapes/attractor.py:16,31,32,36,39,42` - `points` パラメータ使用

### 推奨統一名
`n_points` に統一（点の数を表すことがより明確）

## 4. radius系の統一性確認

### 現状確認済み箇所
- `shapes/capsule.py:221,226` - `radius` 使用（適切）
- `shapes/cylinder.py:11,15,71,76` - `radius` 使用（適切）
- `shapes/torus.py:57,68,111,121` - `major_radius`, `minor_radius` 使用（適切）

### 統一性
トーラスは性質上major/minor radiusが必要だが、他の形状では`radius`で統一されており問題なし。

## 改善計画

### Phase 1: 高優先度修正
1. **grid.py**: `n_divisions` → `subdivisions` に変更
   - Line 53: 関数パラメータ変更
   - Line 86: 関数パラメータ変更

2. **sphere.py**: `n_points` → `points` または逆に統一検討
   - Line 137: 変数名変更

### Phase 2: 中優先度修正
3. **boldify.py**: 内部計算変数を `dx`, `dy` → `offset_x`, `offset_y` に変更
   - Line 22-23: 内部変数名変更

### Phase 3: テストとドキュメント更新
4. 変更に伴うテストケースの更新
5. APIドキュメントの更新
6. 既存コードの動作確認

## 影響範囲評価

### 破壊的変更
- 公開API（関数パラメータ）の変更は破壊的変更となる
- 特に`grid.py`の関数パラメータ変更は使用者に影響する可能性

### 非破壊的変更
- 内部変数名の変更（`boldify.py`の`dx`/`dy`など）は影響なし

## 実装順序
1. 内部変数の変更から開始（非破壊的）
2. パラメータ名変更（破壊的変更）は慎重に実施
3. 各変更後にテストスイート実行で動作確認
4. 変更履歴とマイグレーションガイドの作成

## 実装結果（2025-06-29）

### 完了した修正
1. ✅ **boldify.py**: 内部コメント `dx`/`dy` → `offset_x`/`offset_y` (Line 22-23)
2. ✅ **grid.py**: `n_divisions` → `subdivisions` (Line 53, 86)
3. ✅ **sphere.py**: `n_points` → `points` (Line 137)
4. ✅ **subdivision.py**: `n_divisions` → `subdivisions` (全パラメータ)
5. ✅ **collapse.py**: `n_divisions` → `subdivisions` (Line 137, 148, 159, 163)

### 検出された追加の修正箇所
- **テストファイル**: `test_subdivision.py` で `n_divisions` → `subdivisions` 
- **API層**: `effect_chain.py`, `effect_pipeline.py`, `shape_factory.py`で統一が必要
- **サンプル・ベンチマーク**: 低優先度の修正箇所

### 動作確認結果
- Grid生成: ✅ 正常動作
- Subdivision: ✅ 正常動作  
- Collapse: ⚠️ Numbaの既存問題（変数名変更とは無関係）
- Boldify: ⚠️ Numbaの既存問題（変数名変更とは無関係）

## 期待効果
- ✅ コード可読性の向上
- ✅ 開発者の理解しやすさ向上
- ✅ 保守性の向上
- ✅ 新規開発者のオンボーディング改善

## 今後の作業
1. テストファイルでの`n_divisions` → `subdivisions`修正
2. API層での統一（中優先度）
3. 既存Numba問題の別途対応