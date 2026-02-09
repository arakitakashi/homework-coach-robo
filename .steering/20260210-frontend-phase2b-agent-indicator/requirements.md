# Requirements - Phase 2b エージェント切り替えUIコンポーネント

## 背景・目的

Phase 2bでバックエンドにマルチエージェント構成（Router Agent → Math Coach / Japanese Coach / Encouragement / Review Agent）が導入され、フロントエンドでも `AgentTransitionMessage` WebSocketメッセージのハンドリングと状態管理（`activeAgentAtom`, `agentTransitionHistoryAtom`）が完了しました（PR #77）。

本タスクでは、ユーザーに対して現在のアクティブエージェントを視覚的に表示し、エージェント切り替え時のスムーズなトランジションアニメーションを提供することで、マルチエージェント構成の学習体験を向上させます。

## 要求事項

### 機能要件

#### FR-1: 現在のアクティブエージェント表示

- **FR-1.1**: 現在のアクティブエージェント名を表示する（例: 「算数コーチ」「国語コーチ」「励まし」「振り返り」）
- **FR-1.2**: エージェントに対応する教科アイコンを表示する
- **FR-1.3**: `activeAgentAtom` の状態を購読し、リアルタイムに更新する

#### FR-2: エージェント切り替えトランジションアニメーション

- **FR-2.1**: エージェント切り替え時にフェードイン/フェードアウトアニメーションを表示する
- **FR-2.2**: 切り替え理由（`reason`）がある場合、簡潔なメッセージを表示する
- **FR-2.3**: アニメーション時間は500ms以内とし、ユーザーの学習を妨げない

#### FR-3: エージェント切り替え履歴の記録

- **FR-3.1**: `agentTransitionHistoryAtom` に切り替え履歴を記録する
- **FR-3.2**: 開発者モード（デバッグ用）で履歴を確認できる（将来の拡張）

### 非機能要件

#### NFR-1: パフォーマンス

- **NFR-1.1**: エージェント切り替え時のUI更新は60fpsを維持する
- **NFR-1.2**: 不要な再レンダリングを避けるため、`React.memo` やアトムの細粒度化を活用する

#### NFR-2: アクセシビリティ

- **NFR-2.1**: エージェント名は `aria-label` で読み上げ可能にする
- **NFR-2.2**: アイコンには `aria-hidden="true"` を付与し、テキストで情報を伝える

#### NFR-3: デザイン一貫性

- **NFR-3.1**: Tailwind CSSを使用し、既存のデザインシステムに準拠する
- **NFR-3.2**: `/frontend-design` スキルのガイドラインに従う

### 制約条件

- **C-1**: WebSocketハンドラ（`handleAgentTransition`）は既に実装済み
- **C-2**: 状態管理（`activeAgentAtom`, `agentTransitionHistoryAtom`）は既に実装済み
- **C-3**: `SessionContent.tsx` にコンポーネントを統合する必要がある

## 対象範囲

### In Scope

- ✅ `AgentIndicator` コンポーネントの新規作成
- ✅ エージェント切り替えアニメーションの実装
- ✅ `SessionContent.tsx` への統合
- ✅ ユニットテストの作成（Vitest + Testing Library）

### Out of Scope

- ❌ エージェント切り替えの手動操作（Router Agentが自動で切り替え）
- ❌ エージェント切り替え履歴の詳細ビュー（将来の拡張）
- ❌ バックエンドのマルチエージェント実装（既に完了）

## 成功基準

- ✅ `AgentIndicator` コンポーネントが実装され、テストが通る
- ✅ エージェント切り替え時にスムーズなアニメーションが表示される
- ✅ `activeAgentAtom` の変更が即座にUIに反映される
- ✅ `bun lint && bun typecheck && bun test` が全てパスする
- ✅ アクセシビリティチェック（Biome a11y）をパスする
