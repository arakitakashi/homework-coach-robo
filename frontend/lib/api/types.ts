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
