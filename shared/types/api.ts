/**
 * API共通型定義
 * フロントエンド・バックエンド間で共有される型
 */

/** APIレスポンスの基本型 */
export interface ApiResponse<T> {
	success: boolean
	data?: T
	error?: ApiError
}

/** APIエラー型 */
export interface ApiError {
	code: string
	message: string
	details?: Record<string, unknown>
}

/** ページネーション */
export interface Pagination {
	page: number
	limit: number
	total: number
	hasMore: boolean
}

/** セッション情報 */
export interface Session {
	id: string
	userId: string
	startedAt: string
	status: SessionStatus
}

export type SessionStatus = "active" | "paused" | "completed"

/** ヒントレベル */
export type HintLevel = 1 | 2 | 3

/** キャラクタータイプ */
export type CharacterType = "robot" | "wizard" | "astronaut"
