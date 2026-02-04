/**
 * 対話関連の型定義
 */

/** 発話者 */
export type Speaker = "child" | "robot"

/** 対話ターン */
export interface DialogueTurn {
	id: string
	speaker: Speaker
	text: string
	timestamp: Date
}

/** ヒントレベル（0 = 未使用、1-3 = レベル） */
export type HintLevel = 0 | 1 | 2 | 3

/** キャラクター状態 */
export type CharacterState = "idle" | "listening" | "thinking" | "speaking" | "happy"
