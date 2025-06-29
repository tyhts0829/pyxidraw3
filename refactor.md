2.2 問題点・結合箇所
EffectChain の「二重変換」コスト
GeometryAPI → ndarray → 旧 Geometry → GeometryAPI という往復変換が各エフェクト適用ごとに発生しオーバーヘッド大。
キャッシュの重複
EffectChain 側の WeakValueDictionary と、各旧エフェクトクラスの個別 LRU キャッシュが二重管理で非効率。
旧エフェクト API 依存
新しいチェーン API の内部で旧 Geometry ベースの実装を呼び出し続けており、拡張時に複雑化。
シェイプ API の二重化
api/shapes.py の関数群と ShapeFactory (G) がほぼ同機能を重複。
命名の不統一
divisions vs n_divisions、offset_x vs dx など同一概念で名称が揺れるケースが散見。
一文字ファクトリ (G, E) の可読性
コード閲覧時に文脈がないと意味が分かりづらい。
