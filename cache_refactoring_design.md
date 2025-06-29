# キャッシュ設計改善案

## 現状の問題点

1. **二重キャッシュ管理**
   - `EffectChain`: `WeakValueDictionary`でチェーン全体の結果をキャッシュ
   - `BaseEffect`: `@lru_cache`で個別エフェクトの結果をキャッシュ
   - 現在は`disable_cache()`で回避しているが非効率的

2. **責任の不明確さ**
   - どのレベルでキャッシュすべきかが不明確
   - エフェクトインスタンスの生成時にキャッシュ無効化を忘れる可能性

## 設計案

### 案1: EffectChainレベルでの統一キャッシュ（推奨）

**概要**: キャッシュ管理をEffectChainに一元化し、個別エフェクトはピュアな変換処理のみを担当

```python
# api/effect_chain.py
class EffectChain:
    # グローバルキャッシュ（チェーン全体と個別ステップの両方を管理）
    _chain_cache: WeakValueDictionary[tuple, GeometryAPI] = WeakValueDictionary()
    _step_cache: LRUCache[tuple, GeometryAPI] = LRUCache(maxsize=1024)
    
    def _apply_single_effect(self, geometry_api: GeometryAPI, step: EffectStep) -> GeometryAPI:
        # ステップレベルのキャッシュキー
        step_key = (geometry_api.guid, step.effect_name, step.params_hash)
        
        # ステップキャッシュをチェック
        if step_key in self._step_cache:
            return self._step_cache[step_key]
        
        # エフェクト適用（キャッシュなし）
        result = self._apply_effect_pure(geometry_api, step)
        self._step_cache[step_key] = result
        return result

# effects/base.py
class BaseEffect(ABC):
    # LRUキャッシュを完全に削除
    @abstractmethod
    def apply(self, coords: np.ndarray, offsets: np.ndarray, **params) -> tuple[np.ndarray, np.ndarray]:
        """ピュアな変換処理のみ"""
        pass
```

**メリット**:
- キャッシュ管理が一元化され、理解しやすい
- エフェクトクラスがシンプルになる
- キャッシュ戦略の変更が容易

**デメリット**:
- EffectChain外でエフェクトを使用する場合、キャッシュの恩恵を受けられない

### 案2: 階層的キャッシュ with キャッシュポリシー

**概要**: 各レベルで異なるキャッシュ戦略を採用し、明示的なポリシーで管理

```python
# cache/policies.py
class CachePolicy(Enum):
    NONE = "none"
    EFFECT_LEVEL = "effect"
    CHAIN_LEVEL = "chain"
    BOTH = "both"

# api/effect_chain.py
class EffectChain:
    def __init__(self, base_geometry: GeometryAPI, cache_policy: CachePolicy = CachePolicy.CHAIN_LEVEL):
        self._cache_policy = cache_policy
        # ...
    
    def _create_effect_instance(self, effect_class):
        instance = effect_class()
        if self._cache_policy in (CachePolicy.NONE, CachePolicy.CHAIN_LEVEL):
            instance.disable_cache()
        return instance

# effects/base.py
class BaseEffect(ABC):
    def __init__(self, cache_enabled: bool = True):
        self._cache_enabled = cache_enabled
        self._cache_stats = CacheStats()  # キャッシュ統計情報
```

**メリット**:
- 柔軟なキャッシュ戦略
- パフォーマンスチューニングが可能
- デバッグ時の統計情報収集

**デメリット**:
- 複雑性が増加
- 設定ミスのリスク

### 案3: キャッシュ完全分離

**概要**: エフェクトとキャッシュを完全に分離し、デコレーターパターンで実装

```python
# cache/effect_cache.py
class CachedEffect:
    """エフェクトのキャッシュラッパー"""
    def __init__(self, effect: BaseEffect, cache_size: int = 128):
        self._effect = effect
        self._cache = LRUCache(maxsize=cache_size)
    
    def apply(self, coords: np.ndarray, offsets: np.ndarray, **params):
        cache_key = self._compute_key(coords, offsets, params)
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        result = self._effect.apply(coords, offsets, **params)
        self._cache[cache_key] = result
        return result

# 使用例
noise_effect = CachedEffect(Noise(), cache_size=256)
```

**メリット**:
- 完全な分離により、テストが容易
- エフェクトの実装がクリーン
- キャッシュの有無を選択可能

**デメリット**:
- ラッパーの追加により、若干のオーバーヘッド

## 推奨実装案

**案1（EffectChainレベルでの統一キャッシュ）** を推奨します。

### 理由：

1. **シンプルさ**: キャッシュ管理が一箇所に集約
2. **パフォーマンス**: チェーン全体と個別ステップの両方を効率的にキャッシュ
3. **保守性**: エフェクトクラスの実装がピュアになり、テストしやすい
4. **実用性**: 現在の使用パターン（EffectChain経由）に最適

### 実装手順：

1. BaseEffectから`@lru_cache`関連のコードを削除
2. EffectChainに統合キャッシュシステムを実装
3. キャッシュ統計機能を追加（オプション）
4. 既存のエフェクトクラスを簡素化

### カスタムエフェクトのキャッシュ

案1では、カスタムエフェクトも自動的にキャッシュされます：

```python
def _apply_single_effect(self, geometry_api: GeometryAPI, step: EffectStep) -> GeometryAPI:
    # ステップレベルのキャッシュキー（カスタムエフェクトも同様）
    step_key = (geometry_api.guid, step.effect_name, step.params_hash)
    
    # キャッシュチェック（標準・カスタム問わず）
    if step_key in self._step_cache:
        return self._step_cache[step_key]
    
    # エフェクト適用
    if step.effect_name in self._effect_registry:
        # 標準エフェクト
        result = self._apply_standard_effect(geometry_api, step)
    elif step.effect_name in self._custom_effects:
        # カスタムエフェクト（@E.registerで登録）
        result = self._custom_effects[step.effect_name](geometry_api, **step.params)
    else:
        raise ValueError(f"Unknown effect: {step.effect_name}")
    
    # 結果をキャッシュ
    self._step_cache[step_key] = result
    return result
```

**カスタムエフェクトのキャッシュの利点**：
- 標準エフェクトと同じキャッシュ機構を利用
- パラメータのハッシュ化により、同じ引数での呼び出しを最適化
- ユーザーは特別な処理なしでパフォーマンス向上を享受

### パフォーマンス考慮事項：

- ステップキャッシュのサイズは調整可能にする
- 頻繁に使用されるエフェクトを優先的にキャッシュ
- メモリ使用量の監視機能を追加
- カスタムエフェクトの計算コストに応じてキャッシュ優先度を調整

### 移行計画：

1. 新しいキャッシュシステムをfeatureフラグで制御
2. 段階的に既存のキャッシュを無効化
3. パフォーマンステストで検証
4. 完全移行