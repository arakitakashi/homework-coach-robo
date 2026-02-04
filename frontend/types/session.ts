/**
 * セッション関連の型定義
 */

/** キャラクタータイプ */
export type CharacterType = "robot" | "wizard" | "astronaut" | "animal"

/** セッションステータス */
export type SessionStatus = "idle" | "connecting" | "active" | "error"

/** セッション情報 */
export interface Session {
	id: string
	userId: string
	character: CharacterType
	status: SessionStatus
	startTime: Date
	endTime?: Date
}

/** セッション作成時の入力 */
export type SessionCreation = Omit<Session, "id" | "startTime" | "endTime">

/** 学習進捗 */
export interface LearningProgress {
	selfDiscoveryCount: number
	hintDiscoveryCount: number
	togetherCount: number
}
