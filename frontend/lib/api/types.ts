/**
 * SSE API関連の型定義
 */

/** SSEイベントタイプ */
export type SSEEventType = "text" | "done" | "error"

/** テキストイベント */
export interface TextEvent {
	text: string
}

/** 完了イベント */
export interface DoneEvent {
	session_id: string
}

/** エラーイベント */
export interface ErrorEvent {
	error: string
	code: string
}

/** 対話実行リクエスト */
export interface RunDialogueRequest {
	user_id: string
	session_id: string
	message: string
}

// ============================================
// Session API 型定義
// ============================================

/** セッション作成リクエスト */
export interface CreateSessionRequest {
	/** 問題文 */
	problem: string
	/** 学年（1-3） */
	child_grade: number
	/** キャラクタータイプ */
	character_type?: string
}

/** セッションAPIレスポンス */
export interface SessionApiResponse {
	/** セッションID */
	session_id: string
	/** 問題文 */
	problem: string
	/** 現在のヒントレベル（1-3） */
	current_hint_level: number
	/** 対話トーン */
	tone: string
	/** ターン数 */
	turns_count: number
	/** 作成日時（ISO 8601形式） */
	created_at: string
}
