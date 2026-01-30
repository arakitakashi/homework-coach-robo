# Steering Directory

このディレクトリは、体系的な開発ワークフローを実現するためのステアリング（方向づけ）ドキュメントを管理します。

## ディレクトリ構造

```
.steering/
├── .templates/           # テンプレートファイル
│   ├── requirements.md   # 要求仕様テンプレート
│   ├── design.md         # 実装設計テンプレート
│   ├── tasklist.md       # タスクリストテンプレート
│   └── COMPLETED.md      # 完了サマリーテンプレート
├── [YYYYMMDD]-[work-description]/  # 作業ごとのディレクトリ
│   ├── requirements.md   # 要求仕様
│   ├── design.md         # 実装設計
│   ├── tasklist.md       # タスクリスト
│   └── COMPLETED.md      # 完了サマリー（作業完了時）
└── README.md            # このファイル
```

## 使い方

### 1. 新規作業の開始

```bash
# 日付と作業内容でディレクトリを作成
mkdir -p .steering/$(date +%Y%m%d)-your-work-description

# テンプレートをコピー
cp .steering/.templates/requirements.md .steering/$(date +%Y%m%d)-your-work-description/
cp .steering/.templates/design.md .steering/$(date +%Y%m%d)-your-work-description/
cp .steering/.templates/tasklist.md .steering/$(date +%Y%m%d)-your-work-description/
```

### 2. ドキュメント作成順序

1. **requirements.md**: 何を作るか、なぜ作るかを明確化
2. **design.md**: どのように作るかを設計
3. **tasklist.md**: 実装を小さなタスクに分解

### 3. 実装の進行

`tasklist.md` に従って、TDD原則で実装を進めます。各タスク完了時にチェックマークを更新してください。

### 4. 作業完了

すべてのタスクが完了したら、`COMPLETED.md` を作成し、実装内容のサマリー、学んだこと、今後の改善点を記録します。

## ルールファイル

詳細なワークフローは `.claude/rules/steering-workflow.md` を参照してください。

Claude Code がこのワークフローを自動的に適用します。

## 例

### 初回実装の場合

```bash
.steering/20260131-initial-implementation/
├── requirements.md
├── design.md
├── tasklist.md
└── COMPLETED.md  # 完了時に作成
```

### 新機能追加の場合

```bash
.steering/20260215-add-socratic-dialogue/
├── requirements.md
├── design.md
├── tasklist.md
└── COMPLETED.md  # 完了時に作成
```

## Claude Code との連携

Claude Code は以下のタイミングで自動的にこのワークフローを適用します：

- ユーザーが新機能の実装を依頼した時
- 大規模なリファクタリングを依頼した時
- アーキテクチャ変更を伴う開発を依頼した時

手動で適用したい場合は、「ステアリングワークフローに従って実装してください」と指示してください。
