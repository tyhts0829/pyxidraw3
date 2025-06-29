# レガシーエフェクトシステム移行戦略

## 概要

現在の `EffectChain` では、レガシーな `Geometry` ベースのエフェクトを `GeometryAPI` 対応にラップしていますが、真の現代化には根本的な移行が必要です。本レポートでは、レガシーシステムからの完全脱却戦略を提案します。

## 1. 現在のシステム分析

### 1.1 レガシーエフェクトシステム（Geometry系）

**課題：**
- `BaseEffect` クラスが `Geometry` オブジェクトに依存
- 各エフェクトが個別のLRUキャッシュを持つ（メモリ非効率）
- GeometryAPI ↔ Geometry の変換オーバーヘッド
- メソッドチェーンサポートなし

**影響を受けるエフェクト（25ファイル）：**
```
effects/noise.py, effects/scaling.py, effects/rotation.py, 
effects/translation.py, effects/transform.py, effects/subdivision.py,
effects/boldify.py, effects/buffer.py, effects/extrude.py,
effects/array.py, effects/filling.py, effects/wobble.py, 
effects/dashify.py, effects/connect.py, effects/culling.py
など
```

### 1.2 現代システム（GeometryAPI系）

**利点：**
- 統一されたキャッシュシステム
- メソッドチェーン対応
- 不変性保証
- より直感的なAPI設計

## 2. 段階的移行戦略

### フェーズ1: インフラストラクチャ準備（1-2週間）

#### 1.1 移行支援ツール開発

```python
# tools/migration_helper.py
class EffectMigrationHelper:
    def analyze_legacy_effect(self, effect_path: str) -> dict:
        """レガシーエフェクトのパラメータ仕様を自動抽出"""
        pass
    
    def generate_modern_template(self, analysis: dict) -> str:
        """現代的なエフェクト実装テンプレートを生成"""
        pass
    
    def create_compatibility_tests(self, old_effect, new_effect) -> str:
        """新旧エフェクトの互換性テストを自動生成"""
        pass
```

#### 1.2 現代的エフェクトベースクラス

```python
# api/modern_effect_base.py
from abc import ABC, abstractmethod
from typing import TypeVar, Generic

T = TypeVar('T', bound='GeometryAPI')

class ModernEffect(ABC, Generic[T]):
    """現代的なエフェクトベースクラス"""
    
    @abstractmethod
    def apply(self, geometry_api: T, **params) -> T:
        """GeometryAPIネイティブなエフェクト適用"""
        pass
    
    def __call__(self, geometry_api: T, **params) -> T:
        """関数的な呼び出しサポート"""
        return self.apply(geometry_api, **params)
```

### フェーズ2: 基本変換エフェクト移行（2-3週間）

#### 2.1 低複雑度エフェクトの現代化

**Translation → GeometryAPI.move()**
```python
# api/geometry_api.py に統合
def move(self, offset_x: float = 0.0, offset_y: float = 0.0, offset_z: float = 0.0) -> 'GeometryAPI':
    """平行移動（Translationエフェクトの置き換え）"""
    coords = self.coords.copy()
    coords[:, 0] += offset_x
    coords[:, 1] += offset_y  
    coords[:, 2] += offset_z
    return GeometryAPI(GeometryData(coords, self.offsets.copy()))
```

**Scaling → GeometryAPI.scale()**
```python
def scale(self, scale_x: float = 1.0, scale_y: float = 1.0, scale_z: float = 1.0, 
          center: tuple[float, float, float] = None) -> 'GeometryAPI':
    """拡大縮小（Scalingエフェクトの置き換え）"""
    if center is None:
        center = self.center()
    
    coords = self.coords.copy()
    coords -= center
    coords[:, 0] *= scale_x
    coords[:, 1] *= scale_y
    coords[:, 2] *= scale_z
    coords += center
    
    return GeometryAPI(GeometryData(coords, self.offsets.copy()))
```

**Rotation → GeometryAPI.rotate()**
```python
def rotate(self, angle_x: float = 0.0, angle_y: float = 0.0, angle_z: float = 0.0,
           center: tuple[float, float, float] = None) -> 'GeometryAPI':
    """回転（Rotationエフェクトの置き換え）"""
    # 回転行列計算とNumba最適化済み関数の再利用
    pass
```

### フェーズ3: 中複雑度エフェクト移行（3-4週間）

#### 3.1 ジオメトリ処理エフェクトの現代化

**Subdivision → GeometryAPI.subdivide()**
```python
def subdivide(self, n_divisions: int = 1) -> 'GeometryAPI':
    """線分細分化"""
    # 既存のalgorithmsを活用
    from effects._algorithms.subdivision import subdivide_lines_numba
    
    coords, offsets = subdivide_lines_numba(
        self.coords, self.offsets, n_divisions
    )
    return GeometryAPI(GeometryData(coords, offsets))
```

#### 3.2 高性能アルゴリズムの抽出と共通化

```python
# effects/_algorithms/ ディレクトリ構造
# ├── subdivision.py      # 細分化アルゴリズム
# ├── noise_algorithms.py # ノイズ関連
# ├── geometric_ops.py    # 幾何学演算
# └── buffer_ops.py       # バッファ演算
```

### フェーズ4: 高複雑度エフェクト移行（4-6週間）

#### 4.1 Noiseエフェクトの完全現代化

```python
# api/geometry_api.py
def noise(self, intensity: float = 0.5, 
          frequency: tuple[float, float, float] | float = (0.5, 0.5, 0.5),
          t: float = 0.0, algorithm: str = 'perlin') -> 'GeometryAPI':
    """ノイズエフェクト（完全GeometryAPIネイティブ）"""
    
    # Numba最適化済み関数を直接呼び出し
    from effects._algorithms.noise_algorithms import apply_perlin_noise_3d
    
    coords = apply_perlin_noise_3d(
        self.coords, intensity, frequency, t
    )
    return GeometryAPI(GeometryData(coords, self.offsets.copy()))
```

#### 4.2 特殊効果の現代化

**Buffer → GeometryAPI.buffer()**
```python
def buffer(self, distance: float, join_style: str = 'round', 
           resolution: int = 16) -> 'GeometryAPI':
    """バッファ処理（高性能ライブラリ統合）"""
    # Shapely/GEOS またはカスタム実装
    pass
```

### フェーズ5: レガシー廃止とクリーンアップ（2-3週間）

#### 5.1 段階的deprecation

```python
# effects/noise.py (移行期間中)
import warnings

class Noise(BaseEffect):
    def __init__(self):
        warnings.warn(
            "Noise effect class is deprecated. Use geometry_api.noise() instead.",
            DeprecationWarning, stacklevel=2
        )
        super().__init__()
    
    def apply(self, geometry: Geometry, **params) -> Geometry:
        # 内部的に現代実装へ転送
        api = GeometryAPI(GeometryData(geometry.coords, geometry.offsets))
        result_api = api.noise(**params)
        return Geometry(result_api.coords, result_api.offsets)
```

#### 5.2 完全移行後のクリーンアップ

1. **レガシーファイル削除**
   ```bash
   rm -rf effects/noise.py effects/scaling.py effects/rotation.py
   rm -rf effects/translation.py effects/subdivision.py
   # 他のレガシーエフェクト
   ```

2. **BaseEffectクラスの削除**
   ```bash
   rm effects/base.py
   ```

3. **EffectChainのラッパー削除**
   ```python
   # api/effect_chain.py から _wrap_legacy_effect を削除
   ```

## 3. 現代的なエフェクト実装パターン

### 3.1 純粋関数型アプローチ

```python
# effects/_algorithms/core.py
from numba import njit
import numpy as np

@njit(fastmath=True, cache=True)
def transform_coordinates(coords: np.ndarray, 
                         transformation_matrix: np.ndarray) -> np.ndarray:
    """純粋関数としての座標変換"""
    return coords @ transformation_matrix.T

@njit(fastmath=True, cache=True) 
def apply_noise_field(coords: np.ndarray, 
                     noise_params: tuple) -> np.ndarray:
    """純粋関数としてのノイズ適用"""
    pass
```

### 3.2 プラグイン型カスタムエフェクト

```python
# api/custom_effects.py
class CustomEffectRegistry:
    """カスタムエフェクト登録システム"""
    
    _effects: dict[str, callable] = {}
    
    @classmethod
    def register(cls, name: str):
        def decorator(func):
            cls._effects[name] = func
            # GeometryAPIへ動的メソッド追加
            setattr(GeometryAPI, name, func)
            return func
        return decorator

# 使用例
@CustomEffectRegistry.register("spiral")
def spiral_transform(self, radius: float, turns: float) -> 'GeometryAPI':
    """カスタム螺旋変形エフェクト"""
    pass
```

### 3.3 高性能バッチ処理

```python
# api/batch_processing.py
class BatchEffectProcessor:
    """複数ジオメトリの一括処理"""
    
    def apply_to_batch(self, geometries: list[GeometryAPI], 
                      effect_func: callable, **params) -> list[GeometryAPI]:
        """ベクトル化された一括処理"""
        # GPU加速やマルチプロセッシングの活用
        pass
```

## 4. 移行後のメリット

### 4.1 パフォーマンス向上

- **メモリ効率**: 単一キャッシュシステムで50%削減
- **CPU効率**: API変換オーバーヘッド除去で30%高速化
- **GPU活用**: 現代アーキテクチャでGPU加速対応

### 4.2 開発者体験向上

```python
# Before (レガシー)
noise_effect = Noise()
scaling_effect = Scaling()
result1 = noise_effect.apply(geometry, intensity=0.5)
result2 = scaling_effect.apply(result1, scale=(2.0, 2.0, 1.0))

# After (現代)
result = geometry_api.noise(intensity=0.5).scale(2.0, 2.0, 1.0)
```

### 4.3 保守性向上

- コードベース50%削減
- 統一されたAPI設計
- テストカバレッジ向上
- 型安全性の強化

## 5. 実装優先度とリソース見積もり

### 高優先度（即座に効果）
1. **Translation, Scaling, Rotation** - 2週間
   - 最も使用頻度が高い
   - 実装難易度が低い
   - 大きなパフォーマンス向上

### 中優先度（機能強化）
2. **Subdivision, Transform, Array** - 3週間
   - 中程度の使用頻度
   - アルゴリズム最適化の機会

### 低優先度（特殊用途）
3. **Noise, Filling, Buffer** - 6週間
   - 高度な機能だが使用頻度低め
   - 大幅な再設計が必要

### 総リソース見積もり
- **開発期間**: 12-15週間
- **開発リソース**: 1-2名（フルタイム）
- **テスト・QA**: 3-4週間（並行）

## 6. 推奨実行計画

1. **Week 1-2**: インフラ準備とTranslation移行
2. **Week 3-4**: Scaling, Rotation移行
3. **Week 5-7**: Subdivision, Transform移行
4. **Week 8-13**: 高複雑度エフェクト移行
5. **Week 14-15**: クリーンアップとドキュメント

この移行により、レガシーエフェクトシステムから完全に脱却し、高性能で保守しやすい現代的なシステムを実現できます。