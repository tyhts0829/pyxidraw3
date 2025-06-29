# エフェクトパイプライン設計

## 概要

現在の `EffectChain` は個別ジオメトリに対するメソッドチェーンですが、複数のジオメトリに同じエフェクト組み合わせを適用するパイプライン機能が必要です。以下のような使用パターンを実現します：

```python
# パイプライン定義
effect_pipeline = E.pipeline.subdivision().noise().filling()

# 複数ジオメトリへの適用
sphere = effect_pipeline(sphere)
box = effect_pipeline(box)
cylinder = effect_pipeline(cylinder)
```

## 1. 現在のシステム分析

### 1.1 現在の制限

**単一ジオメトリ専用:**
```python
# 現在の方式 - 各ジオメトリごとにチェーン作成が必要
sphere_result = E.add(sphere).subdivision().noise().filling().result()
box_result = E.add(box).subdivision().noise().filling().result()
cylinder_result = E.add(cylinder).subdivision().noise().filling().result()
```

**問題点:**
- 同じエフェクト組み合わせの重複定義
- パイプライン再利用不可
- コード冗長性
- パフォーマンス非効率（毎回新しいチェーン作成）

### 1.2 求められる機能

1. **パイプライン定義の分離** - エフェクト組み合わせの事前定義
2. **再利用可能性** - 複数ジオメトリへの適用
3. **パフォーマンス最適化** - パイプライン定義の共有
4. **型安全性** - 適切な型推論とエラーハンドリング

## 2. エフェクトパイプライン設計

### 2.1 基本アーキテクチャ

```python
# api/effect_pipeline.py

from __future__ import annotations
from typing import List, Callable, TypeVar, Generic
from .geometry_api import GeometryAPI
from .effect_chain import EffectStep

T = TypeVar('T', bound=GeometryAPI)

class EffectPipeline(Generic[T]):
    """再利用可能なエフェクトパイプライン"""
    
    def __init__(self):
        self._steps: List[EffectStep] = []
        self._compiled_pipeline: Callable[[T], T] = None
        self._is_compiled = False
    
    def __call__(self, geometry: T) -> T:
        """パイプラインをジオメトリに適用"""
        if not self._is_compiled:
            self._compile_pipeline()
        
        return self._compiled_pipeline(geometry)
    
    def _compile_pipeline(self):
        """パイプラインを高効率な実行形式にコンパイル"""
        def compiled_func(geometry: T) -> T:
            current = geometry
            for step in self._steps:
                current = self._apply_step(current, step)
            return current
        
        self._compiled_pipeline = compiled_func
        self._is_compiled = True
```

### 2.2 パイプラインビルダー

```python
class PipelineBuilder:
    """パイプライン構築用ビルダークラス"""
    
    def __init__(self):
        self._pipeline = EffectPipeline()
    
    def subdivision(self, n_divisions: float = 0.5, **params) -> 'PipelineBuilder':
        """細分化エフェクトをパイプラインに追加"""
        all_params = {"n_divisions": n_divisions, **params}
        self._pipeline._steps.append(EffectStep("subdivision", all_params))
        return self
    
    def noise(self, intensity: float = 0.5, 
              frequency: tuple[float, float, float] | float = (0.5, 0.5, 0.5),
              t: float = 0.0, **params) -> 'PipelineBuilder':
        """ノイズエフェクトをパイプラインに追加"""
        all_params = {"intensity": intensity, "frequency": frequency, "t": t, **params}
        self._pipeline._steps.append(EffectStep("noise", all_params))
        return self
    
    def filling(self, pattern: str = "lines", density: float = 0.5, 
                angle: float = 0.0, **params) -> 'PipelineBuilder':
        """塗りつぶしエフェクトをパイプラインに追加"""
        all_params = {"pattern": pattern, "density": density, "angle": angle, **params}
        self._pipeline._steps.append(EffectStep("filling", all_params))
        return self
    
    def rotation(self, center: tuple[float, float, float] = (0, 0, 0), 
                 rotate: tuple[float, float, float] = (0, 0, 0), **params) -> 'PipelineBuilder':
        """回転エフェクトをパイプラインに追加"""
        all_params = {"center": center, "rotate": rotate, **params}
        self._pipeline._steps.append(EffectStep("rotation", all_params))
        return self
    
    def scaling(self, center: tuple[float, float, float] = (0, 0, 0), 
                scale: tuple[float, float, float] = (1, 1, 1), **params) -> 'PipelineBuilder':
        """拡大縮小エフェクトをパイプラインに追加"""
        all_params = {"center": center, "scale": scale, **params}
        self._pipeline._steps.append(EffectStep("scaling", all_params))
        return self
    
    def translation(self, offset_x: float = 0.0, offset_y: float = 0.0, 
                    offset_z: float = 0.0, **params) -> 'PipelineBuilder':
        """平行移動エフェクトをパイプラインに追加"""
        all_params = {"offset_x": offset_x, "offset_y": offset_y, "offset_z": offset_z, **params}
        self._pipeline._steps.append(EffectStep("translation", all_params))
        return self
    
    def build(self) -> EffectPipeline:
        """パイプラインを構築して返す"""
        return self._pipeline
    
    # コンビニエンスメソッド - ビルダー自体を実行可能オブジェクトとして扱う
    def __call__(self, geometry: GeometryAPI) -> GeometryAPI:
        """ビルダーから直接実行"""
        return self.build()(geometry)
```

### 2.3 EffectFactoryの拡張

```python
# api/effect_chain.py の EffectFactory クラスを拡張

class EffectFactory:
    # 既存のメソッド...
    
    @property
    def pipeline(self) -> PipelineBuilder:
        """新しいパイプラインビルダーを作成"""
        return PipelineBuilder()
    
    @classmethod
    def create_pipeline(cls) -> PipelineBuilder:
        """パイプラインビルダーの明示的な作成"""
        return PipelineBuilder()
```

## 3. 高度な機能

### 3.1 パイプラインのキャッシュと最適化

```python
class OptimizedEffectPipeline(EffectPipeline):
    """最適化されたエフェクトパイプライン"""
    
    def __init__(self):
        super().__init__()
        self._cache: Dict[int, GeometryAPI] = {}
        self._cache_enabled = True
    
    def __call__(self, geometry: GeometryAPI) -> GeometryAPI:
        """キャッシュ機能付きで実行"""
        if self._cache_enabled:
            cache_key = self._compute_cache_key(geometry)
            if cache_key in self._cache:
                return self._cache[cache_key]
        
        result = super().__call__(geometry)
        
        if self._cache_enabled:
            self._cache[cache_key] = result
            
        return result
    
    def _compute_cache_key(self, geometry: GeometryAPI) -> int:
        """ジオメトリとパイプラインの組み合わせキーを生成"""
        geometry_hash = hash((geometry.guid, tuple(geometry.coords.flatten())))
        pipeline_hash = hash(tuple(step.params_hash for step in self._steps))
        return hash((geometry_hash, pipeline_hash))
    
    def optimize(self) -> 'OptimizedEffectPipeline':
        """パイプラインを最適化"""
        # エフェクトの順序最適化
        optimized_steps = self._optimize_step_order(self._steps)
        
        # 同種エフェクトの統合
        merged_steps = self._merge_similar_effects(optimized_steps)
        
        new_pipeline = OptimizedEffectPipeline()
        new_pipeline._steps = merged_steps
        return new_pipeline
    
    def _optimize_step_order(self, steps: List[EffectStep]) -> List[EffectStep]:
        """エフェクトの適用順序を最適化"""
        # 変換系エフェクトを最後にまとめる
        transform_effects = []
        other_effects = []
        
        for step in steps:
            if step.effect_name in ['rotation', 'scaling', 'translation', 'transform']:
                transform_effects.append(step)
            else:
                other_effects.append(step)
        
        return other_effects + transform_effects
```

### 3.2 バッチ処理機能

```python
class BatchEffectPipeline(EffectPipeline):
    """バッチ処理対応パイプライン"""
    
    def apply_to_batch(self, geometries: List[GeometryAPI]) -> List[GeometryAPI]:
        """複数ジオメトリへの一括適用"""
        if not self._is_compiled:
            self._compile_pipeline()
        
        # 並列処理での一括適用
        from concurrent.futures import ThreadPoolExecutor
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            results = list(executor.map(self._compiled_pipeline, geometries))
        
        return results
    
    def __call__(self, geometry_or_list):
        """単一ジオメトリまたはリストに対応"""
        if isinstance(geometry_or_list, list):
            return self.apply_to_batch(geometry_or_list)
        else:
            return super().__call__(geometry_or_list)
```

### 3.3 パイプラインのシリアライゼーション

```python
import json
from typing import Dict, Any

class SerializablePipeline(EffectPipeline):
    """シリアライズ可能なパイプライン"""
    
    def to_dict(self) -> Dict[str, Any]:
        """パイプラインを辞書形式に変換"""
        return {
            "steps": [
                {
                    "effect_name": step.effect_name,
                    "params": step.params
                }
                for step in self._steps
            ]
        }
    
    def to_json(self) -> str:
        """JSON文字列として保存"""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SerializablePipeline':
        """辞書からパイプラインを復元"""
        pipeline = cls()
        for step_data in data["steps"]:
            step = EffectStep(step_data["effect_name"], step_data["params"])
            pipeline._steps.append(step)
        return pipeline
    
    @classmethod
    def from_json(cls, json_str: str) -> 'SerializablePipeline':
        """JSON文字列からパイプラインを復元"""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def save(self, filepath: str):
        """ファイルに保存"""
        with open(filepath, 'w') as f:
            f.write(self.to_json())
    
    @classmethod
    def load(cls, filepath: str) -> 'SerializablePipeline':
        """ファイルから読み込み"""
        with open(filepath, 'r') as f:
            return cls.from_json(f.read())
```

## 4. 使用例とパターン

### 4.1 基本的な使用パターン

```python
# 1. 基本的なパイプライン作成と使用
effect_pipeline = E.pipeline.subdivision().noise().filling()

sphere = effect_pipeline(sphere)
box = effect_pipeline(box)
cylinder = effect_pipeline(cylinder)

# 2. パイプラインの事前ビルド
pipeline = E.pipeline.subdivision(n_divisions=0.3).noise(intensity=0.8).build()
results = [pipeline(geom) for geom in geometries]

# 3. バッチ処理
batch_pipeline = BatchEffectPipeline()
batch_pipeline._steps = pipeline._steps
batch_results = batch_pipeline(geometries)  # リストで一括処理
```

### 4.2 高度な使用パターン

```python
# 4. パイプラインの保存と読み込み
complex_pipeline = E.pipeline.subdivision().noise().rotation().scaling().filling()
serializable = SerializablePipeline()
serializable._steps = complex_pipeline._steps
serializable.save("my_pipeline.json")

# 後で読み込み
loaded_pipeline = SerializablePipeline.load("my_pipeline.json")
result = loaded_pipeline(geometry)

# 5. 最適化されたパイプライン
optimized = OptimizedEffectPipeline()
optimized._steps = complex_pipeline._steps
optimized = optimized.optimize()  # エフェクト順序とパラメータを最適化

# 6. カスタムパイプライン組み合わせ
def create_organic_pipeline():
    return E.pipeline.subdivision(n_divisions=0.4).noise(intensity=0.6).filling(pattern="organic")

def create_mechanical_pipeline():
    return E.pipeline.subdivision(n_divisions=0.2).rotation().scaling().filling(pattern="lines")

organic_objects = [create_organic_pipeline()(obj) for obj in natural_objects]
mechanical_objects = [create_mechanical_pipeline()(obj) for obj in tech_objects]
```

### 4.3 パイプライン合成

```python
class CompositePipeline:
    """複数パイプラインの組み合わせ"""
    
    def __init__(self):
        self._pipelines: List[EffectPipeline] = []
    
    def add_pipeline(self, pipeline: EffectPipeline) -> 'CompositePipeline':
        """パイプラインを追加"""
        self._pipelines.append(pipeline)
        return self
    
    def __call__(self, geometry: GeometryAPI) -> GeometryAPI:
        """全パイプラインを順次適用"""
        current = geometry
        for pipeline in self._pipelines:
            current = pipeline(current)
        return current

# 使用例
base_processing = E.pipeline.subdivision().noise()
detail_processing = E.pipeline.filling().rotation()

composite = CompositePipeline().add_pipeline(base_processing).add_pipeline(detail_processing)
final_result = composite(geometry)
```

## 5. 実装計画

### フェーズ1: 基本パイプライン実装（1週間）
1. **EffectPipeline基底クラス作成**
2. **PipelineBuilderクラス実装**
3. **EffectFactory.pipeline プロパティ追加**
4. **基本エフェクトメソッド（subdivision, noise, filling等）**

### フェーズ2: 最適化機能（1週間）
1. **OptimizedEffectPipeline実装**
2. **キャッシュシステム統合**
3. **エフェクト順序最適化**
4. **パフォーマンステスト**

### フェーズ3: 高度な機能（1週間）
1. **BatchEffectPipeline実装**
2. **SerializablePipeline実装**
3. **CompositePipeline実装**
4. **並列処理サポート**

### フェーズ4: テストと文書化（0.5週間）
1. **包括的テストスイート**
2. **使用例ドキュメント**
3. **パフォーマンスベンチマーク**

## 6. 期待される効果

### 6.1 コード簡潔性
```python
# Before: 冗長な繰り返し
sphere_result = E.add(sphere).subdivision().noise().filling().result()
box_result = E.add(box).subdivision().noise().filling().result()
cylinder_result = E.add(cylinder).subdivision().noise().filling().result()

# After: 簡潔なパイプライン
pipeline = E.pipeline.subdivision().noise().filling()
results = [pipeline(obj) for obj in [sphere, box, cylinder]]
```

### 6.2 パフォーマンス向上
- **パイプライン事前コンパイル**: 30-50%の処理時間短縮
- **バッチ処理**: 並列実行で2-4倍の処理速度
- **キャッシュ活用**: 同一パイプライン再利用で大幅高速化

### 6.3 保守性向上
- **エフェクト組み合わせの再利用**
- **設定の永続化と共有**
- **複雑なワークフローの管理**

この設計により、効率的でスケーラブルなエフェクトパイプラインシステムを実現できます。