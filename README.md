# PyxiDraw - MIDI制御リアルタイム3Dベクターグラフィックスシステム

PyxiDrawは、MIDIコントローラーと連携したリアルタイム3Dベクトルグラフィックス生成システムです。直感的なメソッドチェーンAPI、高性能キャッシュシステム、豊富な形状・エフェクトライブラリを特徴とし、AxiDrawなどのペンプロッターデバイスへの出力にも対応しています。

## 🚀 クイックスタート

### 基本セットアップ

```bash
# 基本デモの実行
python test_effects_geometry.py

# 全形状の展示
python all_shapes.py

# メソッドチェーンAPIデモ
python test_fluent_api.py
```

### 最初のスケッチ

```python
import arc
from api.runner import run_sketch
from api import G

def draw(t, cc):
    # 時間と共に回転する六角形
    return G.polygon(n_sides=6).size(50).at(100, 100).rotate_z(t * 0.1)

if __name__ == "__main__":
    arc.start(midi=True)  # MIDI制御を有効化
    run_sketch(draw, canvas_size="SQUARE_200", render_scale=4)
    arc.stop()
```

### 🎯 フル機能デモ: simple.py

simple.pyは、PyxiDrawの全機能を実演する包括的なデモアプリケーションです：

```python
# 実行方法
python simple.py
```

**主な特徴:**
- **球体 + 多面体**の複合図形生成
- **エフェクトパイプライン**（subdivision → noise → rotation）
- **リアルタイムMIDI制御**（5つのパラメータ同時制御）
- **高性能キャッシュ**による最適化

## 🏗️ システム構成

PyxiDrawは明確な4層アーキテクチャで構成されています：

```
pyxidraw3/
├── api/          # 🎯 高レベルユーザーAPI
│   ├── geometry_api.py    # メソッドチェーン基盤
│   ├── shape_factory.py   # G (図形ファクトリ)
│   ├── effect_chain.py    # E (エフェクトチェーン)
│   ├── effect_pipeline.py # パイプライン機能
│   └── runner.py          # run_sketch 統合システム
├── engine/       # ⚙️ コアシステム（レンダリング、MIDI、並列処理）
│   ├── core/     # ModernGL レンダリングエンジン
│   ├── io/       # MIDI/OSC制御システム
│   ├── pipeline/ # 並列処理パイプライン
│   └── render/   # 描画・投影処理
├── shapes/       # 📐 形状生成ライブラリ
│   ├── sphere.py         # 球体（5種類の描画スタイル）
│   ├── polyhedron.py     # 正多面体群
│   └── grid.py           # グリッド系形状
├── effects/      # ✨ エフェクト処理ライブラリ
│   ├── subdivision.py    # Numba最適化 線分細分化
│   ├── noise.py          # 3D Perlinノイズ
│   └── rotation.py       # 高速回転行列
├── util/         # 🔧 ユーティリティ・定数
└── simple.py     # 📊 フル機能デモアプリケーション
```

## 🏛️ アーキテクチャ設計

### レイヤード・アーキテクチャ

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   simple.py     │───▶│   API Layer      │───▶│  Engine Layer   │
│  (Demo App)     │    │  - G (Geometry)  │    │  - Core Render  │
│                 │    │  - E (Effects)   │    │  - MIDI/IO      │
│                 │    │  - run_sketch    │    │  - Pipeline     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   arc Module    │    │ Effects/Shapes   │    │  ModernGL       │
│  (External)     │    │  - subdivision   │    │  (OpenGL)       │
│                 │    │  - noise         │    │                 │
│                 │    │  - rotation      │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

**設計原則:**
- **Facade パターン**: G, E による統一API
- **Builder パターン**: メソッドチェーンによる直感的構築
- **キャッシュ戦略**: LRU + WeakValue による多層最適化
- **並列処理**: SwapBuffer + WorkerPool による高速レンダリング

## 🎨 形状ライブラリ

### 基本図形
```python
from api import G

# 正多角形（三角形〜多角形）
hex_shape = G.polygon(n_sides=6).size(50).at(100, 100)

# 球体（細分化レベル制御可能）
sphere_obj = G.sphere(subdivisions=0.5).scale(100, 100, 100)

# 正多面体（四面体、立方体、八面体、十二面体、二十面体）
tetrahedron = G.polyhedron(polyhedron_type=0.0).scale(80, 80, 80)
```

### 高度な形状
```python
from api import G

# リサージュ曲線
lissa = G.lissajous(freq_x=3.0, freq_y=2.0).scale(50, 50, 50)

# カオスアトラクター（Lorenz、Rossler、Chua）
lorenz = G.attractor(attractor_type="lorenz").scale(5, 5, 5).at(150, 150)

# トーラス
donut = G.torus(major_radius=0.8, minor_radius=0.3).scale(100, 100, 100)

# テキスト
message = G.text(text_content="HELLO").size(30).at(100, 100)
```

## ✨ エフェクトシステム

### 基本変換
```python
from api import E

# メソッドチェーンによる統一されたエフェクト処理
result = (E.add(geometry)
          .rotation(center=(0,0,0), rotate=(0,0,0.5))
          .scaling(center=(0,0,0), scale=(2,2,2))
          .translation(offset_x=10, offset_y=20)
          .result())

# 複合変換
transformed = (E.add(geometry)
               .transform(center=(100, 100, 0), 
                         scale=(2, 2, 2), 
                         rotate=(0.5, 0.3, 0))
               .result())
```

### 形状操作エフェクト
```python
from api import E

# 高性能なメソッドチェーンエフェクト
result = (E.add(geometry)
          .subdivision(n_divisions=0.8)    # 線の細分化
          .filling(pattern="lines", density=0.6)  # ハッチング塗りつぶし
          .noise(intensity=0.3, time=t)    # Perlinノイズ
          .buffer(distance=0.08)           # バッファ（太線効果）
          .result())

# 個別エフェクトも可能
smooth = E.add(geometry).subdivision(n_divisions=0.8).result()
filled = E.add(geometry).filling(pattern="lines", density=0.6).result()
```

## 🎹 MIDI制御システム

### 基本的なMIDI制御
```python
def draw(t, cc):
    # t: 経過時間（秒）
    # cc: MIDI CC値辞書 {CC番号: 値(0.0-1.0)}
    
    size = cc.get(1, 0.5) * 100      # CC#1でサイズ制御
    rotation_speed = cc.get(2, 0.5)   # CC#2で回転速度制御
    noise_level = cc.get(3, 0.2)      # CC#3でノイズ強度制御
    
    base = G.polygon(n_sides=6).size(size).at(100, 100)
    
    # エフェクトチェーンで統一されたAPI
    final = (E.add(base)
             .rotation(rotate=(0, 0, t * rotation_speed))
             .noise(intensity=noise_level, time=t)
             .result())
    
    return final
```

### 複雑なMIDI制御例
```python
def advanced_midi_control(t, cc):
    # 形状の種類をMIDI制御
    n_sides = int(cc.get(1, 0.5) * 10 + 3)  # 3〜13角形
    
    # 複数パラメータの組み合わせ
    base = G.polygon(n_sides=n_sides)
    
    # エフェクトチェーン（MIDIで各段階を制御）
    final = (E.add(base)
             .transform(center=(100, 100, 0),
                       scale=(cc.get(2, 0.5) * 100, cc.get(2, 0.5) * 100, 50),
                       rotate=(cc.get(3, 0) * 6.28, cc.get(4, 0) * 6.28, t * 0.1))
             .subdivision(n_divisions=cc.get(5, 0.5))
             .noise(intensity=cc.get(6, 0.2), time=t)
             .result())
    
    return final
```

## 🚀 高性能メソッドチェーンAPI

PyxiDrawの最大の特徴は、直感的で高性能なメソッドチェーンAPIです：

### 新記法：エレガントなメソッドチェーン
```python
def draw(t, cc):
    # 読みやすく、書きやすい
    return (sphere(subdivisions=0.5)
            .scale(100, 100, 100)
            .translate(100, 100, 0)
            .rotate(t * 0.1, t * 0.2, 0))

def complex_scene(t, cc):
    # 複数オブジェクトの組み合わせ
    sphere_obj = (sphere(subdivisions=cc.get(1, 0.5))
                  .scale(80, 80, 80)
                  .at(100, 150)
                  .rotate(t * 0.2, t * 0.3, 0))
    
    polygon_obj = (polygon(n_sides=8)
                   .size(cc.get(2, 0.5) * 60)
                   .at(200, 150)
                   .spin(t * 0.5))
    
    return sphere_obj + polygon_obj
```

### ショートカットメソッド
```python
# 便利なエイリアス
geometry.size(50)        # scale_uniform(50) のエイリアス
geometry.at(100, 100)    # center_at(100, 100) のエイリアス
geometry.spin(0.5)       # rotate_z(0.5) のエイリアス
```

## ⚡ 高性能キャッシュシステム

PyxiDrawは**最大440倍の高速化**を実現するインテリジェントキャッシュを内蔵：

```python
# 同じ操作は自動的にキャッシュされ、即座に結果を返却
sphere1 = G.sphere(subdivisions=0.5).size(100, 100, 100)  # 初回計算
sphere2 = G.sphere(subdivisions=0.5).size(100, 100, 100)  # キャッシュヒット（440倍高速）

# パラメータが異なれば新たに計算
sphere3 = G.sphere(subdivisions=0.6).size(100, 100, 100)  # 新規計算
```

### パフォーマンス最適化の実装

- **Numba JIT**: `@njit(fastmath=True, cache=True)` による数値計算高速化
- **マルチレベルキャッシュ**: 
  - 形状生成: `@lru_cache(maxsize=128)`
  - エフェクトチェーン: 統合キャッシュ + ステップレベルキャッシュ
  - パイプライン: `WeakValueDictionary` による効率的メモリ管理
- **並列処理**: 6ワーカーによる並列レンダリング

## 🎛️ 対応MIDIデバイス

- **Teenage Engineering**: OP-Z, TX-6
- **monome**: Grid, Arc
- **一般的なMIDIコントローラー**: すべてのCC対応デバイス

### MIDI設定
```python
# MIDIデバイス確認
arc.list_midi_devices()

# MIDI有効化
arc.start(midi=True)

# MIDI無効モード
arc.start(midi=False)
```

### simple.py でのMIDI制御例
```python
def draw(t, cc):
    # MIDIコントローラー値を取得（0.0-1.0範囲）
    subdivision_val = cc.get(1, 0.5)      # CC#1: subdivision レベル
    noise_intensity = cc.get(2, 0.3)      # CC#2: noise 強度  
    rotation_val = cc.get(3, 0.1)         # CC#3: rotation 速度
    sphere_subdivisions = cc.get(6, 0.5)  # CC#6: sphere 細分化
    
    # エフェクトパイプライン構築
    pipeline = (
        E.pipeline.subdivision(n_divisions=subdivision_val)
        .noise(intensity=noise_intensity)
        .rotation(rotate=(rotation_val, rotation_val, rotation_val))
    )
    
    # 図形生成 + エフェクト適用
    sphere = G.sphere(subdivisions=sphere_subdivisions).size(80, 80, 80)
    poly = G.polyhedron().size(80, 80, 80)
    
    return pipeline(sphere) + pipeline(poly)
```

## 📊 実行環境設定

### run_sketch関数の詳細設定
```python
run_sketch(
    user_draw_function,
    canvas_size="A4",                    # "A4", "A5", "SQUARE_200" or (width, height)
    render_scale=4,                      # 表示倍率（1-10）
    fps=60,                             # フレームレート
    background=(1, 1, 1, 1),            # 背景色 (R, G, B, A)
    workers=6                           # 並列処理ワーカー数
)
```

### キャンバスサイズプリセット
```python
from util.constants import CANVAS_SIZES

# 利用可能なサイズ
"A4"          # 210×297mm
"A5"          # 148×210mm  
"SQUARE_200"  # 200×200mm
"SQUARE_150"  # 150×150mm

# カスタムサイズ
run_sketch(draw, canvas_size=(120, 180))
```

## 🛠️ 開発者向け情報

### テストとベンチマーク
```bash
# パフォーマンステスト
python demo_cached_scene.py

# ベンチマーク実行
python -m pytest benchmarks/

# 全エフェクトテスト
python all_effects.py
```

### デバッグとモニタリング
```python
# パフォーマンス監視
from engine.monitor import performance_monitor

# デバッグ出力
import logging
logging.basicConfig(level=logging.DEBUG)
```

### プロジェクト拡張
```python
# カスタム形状の追加
from shapes.base import BaseShape
from engine.core.geometry import Geometry

class MyCustomShape(BaseShape):
    def create_geometry(self) -> Geometry:
        # カスタム形状ロジック
        pass

# カスタムエフェクトの追加
from effects.base import BaseEffect

class MyCustomEffect(BaseEffect):
    def apply(self, geometry: Geometry) -> Geometry:
        # カスタムエフェクトロジック
        pass
```

## 📈 システム評価

### コード品質スコア (10点満点)

| 項目 | スコア | 評価 |
|------|--------|------|
| **アーキテクチャ** | 8/10 | レイヤード設計、Facadeパターンの効果的使用 |
| **パフォーマンス** | 9/10 | Numba JIT、多層キャッシュによる高速化 |
| **コード品質** | 7/10 | 型ヒント完備、一部改善の余地 |
| **保守性** | 6/10 | ハードコーディング問題、設定分散 |
| **テスタビリティ** | 5/10 | 外部依存強、モック必要 |
| **セキュリティ** | 6/10 | 基本対策済、入力検証要改善 |

**総合評価: 7.0/10** (良好、改善により8.5+を目指せる)

### 実装ロードマップ

#### 🔴 Phase 1: 即座改善 (1-2週間)
1. **simple.py 設定定数化** - ハードコーディング解消
2. **パラメータ流用問題解決** - sphere_type 専用化
3. **エラーハンドリング追加** - 基本的な例外処理
4. **座標値動的化** - キャンバスサイズ依存解消

#### 🟡 Phase 2: 中期改善 (1ヶ月)
1. **設定管理システム** - YAML/JSON 設定ファイル
2. **入力検証体系化** - パラメータ範囲チェック
3. **カスタム例外クラス** - エラー種別の明確化
4. **ログシステム統合** - デバッグ・監視強化

#### 🟢 Phase 3: 長期改善 (3ヶ月)
1. **テストスイート構築** - 単体・統合テスト
2. **プロファイリング統合** - パフォーマンス監視
3. **セキュリティ監査** - 脆弱性対策
4. **ドキュメント完全化** - API仕様書

## 🔗 関連リソース

- **コードレビュー詳細**: `simple_py_code_review.md`
- **アーキテクチャ詳細**: `/CLAUDE.md`
- **サンプルコード**: `/examples/`
- **変数命名改善**: `variable_naming_issues.md`
- **ベンチマーク結果**: `/benchmark_results/`

## 🎯 学習ロードマップ

### 初心者
1. `test_effects_geometry.py` を実行して基本動作を確認
2. 簡単な形状生成から始める (`polygon`, `sphere`)
3. 基本的なMIDI制御を試す

### 中級者
1. メソッドチェーンAPIをマスター
2. 複数エフェクトの組み合わせを実験
3. 複雑なMIDI制御パターンを構築

### 上級者
1. カスタム形状・エフェクトの開発
2. 並列処理システムの活用
3. パフォーマンス最適化とベンチマーク

## ⚠️ 重要な注意事項

- **座標系**: 3D座標系のみ対応（Z=0で2D描画）
- **キャンバス**: A4サイズ（297mm×210mm）基準の設計
- **エフェクト引数**: 0.0-1.0の正規化レンジを使用
- **スレッドセーフティ**: MIDI入力は別スレッドで処理される

---

PyxiDrawで**美しいベクターアート**と**インタラクティブな表現**を作り上げましょう！ 🎨✨