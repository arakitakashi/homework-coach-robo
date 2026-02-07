/**
 * Phase 2 状態管理の Jotai atoms
 * Phase 2a: ツール状態
 * Phase 2b: マルチエージェント状態
 * Phase 2c: RAG状態
 * Phase 2d: 感情適応状態
 */

import { atom } from "jotai"
import type {
	ActiveAgent,
	AgentTransition,
	ChildLearningProfile,
	EmotionAdaptation,
	EmotionAnalysis,
	RetrievedMemory,
	ToolExecution,
} from "@/types"

// ============================================
// Phase 2a: ツール状態
// ============================================

/** 現在実行中のツール */
export const activeToolExecutionsAtom = atom<ToolExecution[]>([])

/** ツール実行履歴 */
export const toolExecutionHistoryAtom = atom<ToolExecution[]>([])

/** ツール実行中フラグ（派生atom） */
export const isToolRunningAtom = atom((get) => {
	const executions = get(activeToolExecutionsAtom)
	return executions.some((e) => e.status === "running" || e.status === "pending")
})

// ============================================
// Phase 2b: マルチエージェント状態
// ============================================

/** アクティブエージェント */
export const activeAgentAtom = atom<ActiveAgent | null>(null)

/** エージェント遷移履歴 */
export const agentTransitionHistoryAtom = atom<AgentTransition[]>([])

// ============================================
// Phase 2c: RAG状態
// ============================================

/** 取得された記憶 */
export const retrievedMemoriesAtom = atom<RetrievedMemory[]>([])

// ============================================
// Phase 2d: 感情適応状態
// ============================================

/** 最新の感情分析結果 */
export const emotionAnalysisAtom = atom<EmotionAnalysis | null>(null)

/** 感情適応設定 */
export const emotionAdaptationAtom = atom<EmotionAdaptation | null>(null)

/** 感情履歴 */
export const emotionHistoryAtom = atom<EmotionAnalysis[]>([])

// ============================================
// 学習プロファイル
// ============================================

/** 子供の学習プロファイル */
export const learningProfileAtom = atom<ChildLearningProfile | null>(null)
