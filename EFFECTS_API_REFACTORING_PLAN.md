# エフェクトAPI二重化問題 解決計画書

## 🔍 問題の特定

### 現状の重複構造

1. **api/effects.py**：関数形式の古いエフェクトAPI
   - `rotation()`, `scaling()`, `translation()`, `subdivision()` など
   - 個別関数として実装
   - キャッシュ機能なし
   - 古い`Geometry`型を使用

2. **api/effect_chain.py**：新しいEffectChain（E）API  
   - `E.add().rotation().scaling().result()` のメソッドチェーン形式
   - 高性能LRUキャッシュ機能
   - 新しい`GeometryAPI`型対応
   - モダンなエフェクトパイプライン

### 問題点

- **機能重複**: 同じエフェクトを2つの方法で提供
- **APIの混乱**: 開発者がどちらを使うべきか不明
- **保守負担**: 2つのAPIを並行してメンテナンス
- **パフォーマンス差**: 新APIにのみキャッシュ機能
- **型不統一**: Geometry vs GeometryAPI

## 📊 現状分析

### api/effects.py の関数一覧

**アクティブな関数**（7個）:
- `rotation()`
- `scaling()` 
- `translation()`
- `subdivision()`
- `extrude()`
- `filling()`
- `transform()`
- `noise()`
- `buffer()`
- `array()`

**コメントアウトされた関数**（多数）:
- `boldify()`, `connect()`, `dashify()`, `culling()`, `wobble()` など

### api/effect_chain.py（E）の実装状況

- メソッドチェーンAPI: `E.add(geometry).effect().result()`
- LRUキャッシュ: `EffectStep`でパラメータをキャッシュ
- 高性能: WeakValueDictionary使用
- 型安全: GeometryAPI統一

### 使用状況調査

```bash
grep結果:
- README.md: api.effects の使用例あり
- benchmarks/plugins/serializable_targets.py: api.effects 使用
- その他：主にドキュメントでの言及
```

## 🎯 解決方針

**api/effect_chain.py（E）を正式APIとし、api/effects.pyを段階的に廃止する**

### 利点

1. **統一されたメソッドチェーンAPI**
2. **高性能キャッシュシステム**  
3. **GeometryAPIとの型統一**
4. **拡張可能なパイプライン設計**

## 📋 実装手順

### Phase 1: 互換性レイヤーの構築

#### 1-1. api/effects.py を薄いラッパーに変更

```python
"""
DEPRECATED: This module is deprecated. Use E from api.effect_chain instead.

Legacy effect functions that wrap the new EffectChain (E).
All functions in this module are deprecated and will be removed in a future version.
"""

import warnings
from api.effect_chain import E
from engine.core.geometry import Geometry
from api.geometry_api import GeometryAPI

def rotation(geometry, **kwargs):
    warnings.warn(
        "api.effects.rotation() is deprecated. Use E.add(geometry).rotation().result() instead.",
        DeprecationWarning,
        stacklevel=2
    )
    # Geometry → GeometryAPI 変換
    if isinstance(geometry, Geometry):
        geo_api = GeometryAPI(geometry.to_geometry_data())
    else:
        geo_api = geometry
    
    return E.add(geo_api).rotation(**kwargs).result()
```

#### 1-2. 非推奨警告の追加

- 全アクティブ関数に`DeprecationWarning`を追加
- 新しいE.*への移行方法を明示

#### 1-3. パラメータ互換性の確保

- 既存の関数シグネチャを維持
- 内部でE.*への変換処理を実装

### Phase 2: 使用箇所の移行

#### 2-1. 使用箇所の特定と更新

```bash
# 検索対象
- benchmarks/plugins/serializable_targets.py
- README.md の使用例
- その他のサンプルコード
```

#### 2-2. 移行パターン

```python
# 旧API
from api.effects import rotation, scaling, noise
result = noise(scaling(rotation(geometry, center=(0,0,0), rotate=(0,0,0.5)), scale=(2,2,2)), intensity=0.3)

# 新API 
from api import E
result = (E.add(geometry)
           .rotation(center=(0,0,0), rotate=(0,0,0.5))
           .scaling(scale=(2,2,2))
           .noise(intensity=0.3)
           .result())
```

#### 2-3. README.md の更新

- 全エフェクト使用例をE.*に変更
- メソッドチェーンの利点を説明
- パフォーマンス向上を明記

### Phase 3: 最終クリーンアップ

#### 3-1. api/effects.py の完全削除

- 非推奨期間後に完全削除
- または空ファイルとして保持（ImportError対応）

#### 3-2. effects/ モジュールの整理

- 個別エフェクトクラスは内部実装として保持
- E経由でのみアクセス可能に統一

#### 3-3. ドキュメント最終更新

- APIリファレンスの統一
- 移行ガイドの提供

## 🔧 技術的詳細

### 型変換処理

```python
def _convert_to_geometry_api(geometry) -> GeometryAPI:
    """古いGeometry型を新しいGeometryAPIに変換"""
    if isinstance(geometry, Geometry):
        return GeometryAPI(geometry.to_geometry_data())
    elif isinstance(geometry, GeometryAPI):
        return geometry
    else:
        raise TypeError(f"Unsupported geometry type: {type(geometry)}")
```

### パラメータマッピング

大部分は1:1マッピングが可能:
- `rotation(center, rotate)` → `E.add().rotation(center, rotate)`
- `scaling(center, scale)` → `E.add().scaling(center, scale)` 
- `noise(intensity, frequency)` → `E.add().noise(intensity, frequency)`

### キャッシュ効果の検証

```python
# 性能比較テスト
old_time = measure_time(lambda: old_rotation(geometry, rotate=(0,0,0.5)))
new_time = measure_time(lambda: E.add(geometry).rotation(rotate=(0,0,0.5)).result())
```

## 📈 期待効果

### パフォーマンス向上

- **LRUキャッシュ**: 同一パラメータでの高速化
- **メソッドチェーン**: 中間結果の最適化
- **型統一**: 変換オーバーヘッド削減

### 開発者体験向上

- **統一API**: E.*での一貫したインターフェース
- **可読性**: メソッドチェーンによる明確な処理フロー
- **発見しやすさ**: IDE補完での全エフェクト表示

### 保守性向上

- **単一責任**: エフェクトチェーンに集約
- **拡張性**: 新エフェクトの追加が容易
- **テスト**: 統一されたテストフレームワーク

## ⚠️ 注意点

### 移行時の互換性

- Geometry ↔ GeometryAPI の変換処理が必要
- パラメータ名の微細な差異をマッピング
- エラーハンドリングの統一

### 段階的移行

- 大規模なコードベースでは段階的移行を推奨
- 非推奨警告を経て最終削除
- 十分なテスト期間を確保

## 📅 実装スケジュール

### Phase 1: 互換性レイヤー（1-2日）
- api/effects.py のラッパー化
- 非推奨警告の実装
- 基本動作テスト

### Phase 2: 使用箇所移行（1-2日）  
- benchmarks/ の移行
- README.md の更新
- サンプルコードの移行

### Phase 3: 最終化（1日）
- 完全削除または空ファイル化
- 最終テストと品質確認
- 完了ドキュメント作成

## 🎯 成功指標

- ✅ 全実用コードでE.*への移行完了
- ✅ パフォーマンステストでキャッシュ効果確認  
- ✅ 旧APIの完全削除または無効化
- ✅ 統合テスト全項目合格
- ✅ ドキュメント完全更新

---

**この計画により、エフェクトAPIの重複問題を解決し、統一された高性能なE.*インターフェースを実現します。**