/**
 * ゲーミフィケーション要素の型定義
 * Phase 1: フロントエンドのみ実装（モックデータ）
 * Phase 2: バックエンドAPI連携予定
 */

/**
 * ポイント獲得理由
 */
export type PointReason =
	| "self_discovery" // 自分で気づいた (3pt)
	| "hint_discovery" // ヒントで気づいた (2pt)
	| "collaborative" // 一緒に解いた (1pt)
	| "bonus_streak" // 連続正解ボーナス
	| "bonus_first_clear" // 初回クリアボーナス

/**
 * ポイント獲得イベント
 */
export interface PointEvent {
	/** 獲得ポイント数 */
	points: number
	/** ポイント獲得理由 */
	reason: PointReason
	/** 獲得タイムスタンプ（Unix時間） */
	timestamp: number
	/** 対象問題ID（任意） */
	problemId?: string
}

/**
 * バッジカテゴリ
 */
export type BadgeCategory = "achievement" | "streak" | "mastery"

/**
 * バッジ定義
 */
export interface Badge {
	/** バッジID */
	id: string
	/** バッジ名 */
	name: string
	/** バッジ説明 */
	description: string
	/** Lucide Reactアイコン名 */
	iconName: string
	/** バッジカテゴリ */
	category: BadgeCategory
	/** 獲得タイムスタンプ（未獲得の場合はundefined） */
	unlockedAt?: number
}

/**
 * ストーリーチャプター
 */
export interface StoryChapter {
	/** チャプターID */
	id: string
	/** チャプタータイトル */
	title: string
	/** チャプター説明 */
	description: string
	/** クリアに必要なポイント数 */
	requiredPoints: number
	/** 完了フラグ */
	completed: boolean
}

/**
 * ゲーミフィケーション状態
 */
export interface GamificationState {
	/** 累計獲得ポイント */
	totalPoints: number
	/** 現在のセッションで獲得したポイント */
	sessionPoints: number
	/** 現在のレベル */
	level: number
	/** 獲得済みバッジリスト */
	badges: Badge[]
	/** 現在のストーリーチャプター */
	currentChapter: StoryChapter
	/** ポイント獲得履歴 */
	pointHistory: PointEvent[]
}
