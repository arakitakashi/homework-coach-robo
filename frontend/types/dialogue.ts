/**
 * 対話関連の型定義
 */

import type {
	AgentType,
	EmotionType,
	QuestionType,
	ResponseAnalysis,
	ToolExecution,
} from "./phase2"

/** 発話者 */
export type Speaker = "child" | "robot"

/** 対話ターン */
export interface DialogueTurn {
	id: string
	speaker: Speaker
	text: string
	timestamp: Date
	/** Phase 2a: 質問タイプ */
	questionType?: QuestionType
	/** Phase 2a: 回答分析結果 */
	responseAnalysis?: ResponseAnalysis
	/** Phase 2d: 検出された感情 */
	emotion?: EmotionType
	/** Phase 2b: 対応したエージェント */
	activeAgent?: AgentType
	/** Phase 2a: ツール実行結果 */
	toolExecutions?: ToolExecution[]
}

/** ヒントレベル（0 = 未使用、1-3 = レベル） */
export type HintLevel = 0 | 1 | 2 | 3

/** キャラクター状態 */
export type CharacterState = "idle" | "listening" | "thinking" | "speaking" | "happy"
