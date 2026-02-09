---
name: update-docs
description: Delegates documentation updates (CLAUDE.md, docs/implementation-status.md) to a sub-agent after completing implementation work. Use when finishing a feature, fix, or other implementation task before creating a PR.
allowed-tools: Task, Bash(git:*)
---

# Update Documentation

## Overview

このスキルは、実装完了後のドキュメント更新をサブエージェントに委譲し、メインエージェントのコンテキスト消費を最小化します。

## When to Use

- 実装作業（Phase 5 品質チェック）の完了後
- PR作成前

## Instructions

### Step 1: 作業サマリーを準備

以下の情報を整理してください：

- **何を実装/変更したか**（1〜2文）
- **ステアリングディレクトリのパス**（例: `.steering/20260210-xxx/`）
- **テスト数やカバレッジの変化**（あれば）

### Step 2: サブエージェントを起動

Task ツールで `general-purpose` サブエージェントを起動し、以下のプロンプトテンプレートを使用してください。`[PLACEHOLDERS]` を実際の値に置き換えてください。

```
プロジェクトのドキュメントを更新してください。

## 作業サマリー
[作業内容の1〜2文の説明]

## ステアリングディレクトリ
[.steering/YYYYMMDD-xxx/]

## テスト数/カバレッジ
[変化があれば記載。なければ「変更なし」]

## 更新手順

### 1. CLAUDE.md の更新
- ファイルを読み込み、Development Context セクション（「このプロジェクトは現在、」で始まる行）を探す
- プロジェクトステータスの説明に今回の作業内容を追加
- 変更が大きい場合（新Phase完了、アーキテクチャ変更等）のみ更新。軽微な修正は不要

### 2. docs/implementation-status.md の更新
- ファイルを読み込み、以下の3箇所を更新:
  a. 冒頭の「プロジェクトステータス」行（CLAUDE.md と同じ内容）
  b. 「完了済み機能一覧」セクションの末尾に今回の作業を追加
  c. ステアリングディレクトリ一覧テーブルの末尾に今回の .steering/ を追加
- テスト数/カバレッジに変化があれば該当箇所も更新

### 3. その他のドキュメント確認
- 作業内容に応じて以下も確認:
  - docs/agent-architecture.md（エージェント/ツール変更時）
  - docs/functional-design.md（API仕様変更時）
  - docs/architecture.md（技術スタック変更時）

### 4. コミット
- 変更をコミット: `docs: update documentation for [作業内容の簡潔な説明]`
```

### Step 3: 結果確認

サブエージェントの完了後、更新内容が正しいことを簡単に確認してください。

## Notes

- サブエージェントがドキュメントを読み込むため、メインエージェントのコンテキストに700行以上の `implementation-status.md` が載ることを避けられます
- 軽微な変更（タイポ修正等）ではこのスキルを使う必要はありません
