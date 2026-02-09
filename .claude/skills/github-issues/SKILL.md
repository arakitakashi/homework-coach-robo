---
name: github-issues
description: Delegates GitHub issue operations (list, view, create, update, close, comment) to a sub-agent. Use when checking related issues before starting work, updating issue status after implementation, or managing project issues.
allowed-tools: Task
---

# GitHub Issues

## Overview

このスキルは、GitHub Issue の確認・作成・更新をサブエージェントに委譲します。Issue一覧や詳細の読み込みがメインのコンテキストに載ることを防ぎます。

## When to Use

- 実装開始前に関連 Issue を確認するとき
- 実装完了後に Issue をクローズ / コメントするとき
- 新しい Issue を作成するとき
- Milestone やラベルの確認が必要なとき

## Instructions

### 操作ごとにサブエージェントを起動

Task ツールで `general-purpose` サブエージェントを起動し、操作に応じたプロンプトを使用してください。

---

#### 関連 Issue の確認（実装開始前）

```
GitHub Issue を確認し、関連する Issue を報告してください。

リポジトリ: [owner/repo]
作業ディレクトリ: [ディレクトリの絶対パス]

## 手順

### 1. オープンな Issue を一覧取得
コマンド: gh issue list --state open --limit 30

### 2. 関連 Issue の特定
以下のキーワードに関連する Issue をフィルタ:
- キーワード: [今回の作業に関連するキーワード]

関連する Issue が見つかった場合、各 Issue について:
コマンド: gh issue view [ISSUE_NUMBER]

### 3. Milestone の確認
コマンド: gh api repos/[owner/repo]/milestones --jq '.[].title'

## 報告フォーマット

### 関連 Issue
各 Issue について:
- #番号: タイトル
- ラベル: [ラベル一覧]
- Milestone: [Milestone名]
- 概要: [1文の要約]

### 関連なしの場合
「関連する Issue は見つかりませんでした」と報告
```

---

#### Issue のクローズ / コメント（実装完了後）

```
GitHub Issue を更新してください。

リポジトリ: [owner/repo]
作業ディレクトリ: [ディレクトリの絶対パス]

## 操作内容

### Issue にコメントを追加
Issue番号: #[NUMBER]
コメント内容:
[作業内容の要約。例: "PR #XX で対応しました。以下の変更を含みます: ..."]

コマンド: gh issue comment [NUMBER] --body "[コメント内容]"

### Issue をクローズ（該当する場合）
コマンド: gh issue close [NUMBER] --comment "Resolved in PR #[PR_NUMBER]"

## 報告
更新した Issue の番号と操作内容を報告してください。
```

---

#### 新しい Issue の作成

```
GitHub Issue を作成してください。

リポジトリ: [owner/repo]
作業ディレクトリ: [ディレクトリの絶対パス]

## Issue 内容
タイトル: [タイトル]
ラベル: [ラベル（カンマ区切り）]
Milestone: [Milestone名（該当する場合）]

本文:
[Issue の本文。以下の構成を推奨]
## 概要
[問題や要望の説明]

## 期待動作
[あるべき姿]

## 現状
[現在の状態]

## 対応案
[もしあれば]

コマンド: gh issue create --title "[タイトル]" --body "[本文]" --label "[ラベル]"

## 報告
作成した Issue の URL を報告してください。
```

---

#### Issue 一覧の確認（プロジェクト状況把握）

```
GitHub Issue の状況を確認し、サマリーを報告してください。

リポジトリ: [owner/repo]
作業ディレクトリ: [ディレクトリの絶対パス]

## 手順

### 1. オープンな Issue を取得
コマンド: gh issue list --state open --limit 50

### 2. Milestone 別の集計
コマンド: gh issue list --state open --limit 50 --json number,title,labels,milestone

### 3. ラベル別の集計

## 報告フォーマット

### サマリー
- オープン: X 件
- Milestone別:
  - [Milestone名]: X 件
- ラベル別:
  - [ラベル名]: X 件

### 優先度の高い Issue（あれば）
- #番号: タイトル（理由: ...）
```

---

### 結果確認

サブエージェントの結果を確認し、必要に応じて追加操作を行ってください。

## Notes

- `gh issue list` の出力が長い場合（数十件）、サブエージェントが要約してくれるためコンテキスト節約に効果的
- Issue のコメント追加や作成は `dangerouslyDisableSandbox: true` が必要な場合があります
- PR 作成時に `closes #XX` を含めることで、マージ時に自動クローズされます（`/create-pr` スキルと併用推奨）
