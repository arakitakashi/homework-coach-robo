/**
 * カメラ・画像認識関連の型定義
 *
 * CameraInterfaceコンポーネントで使用するカメラ状態、エラー、
 * 画像認識リクエスト/レスポンスの型を定義。
 */

/** カメラの状態遷移 */
export type CameraStatus = "initial" | "active" | "preview" | "processing" | "recognized" | "error"

/**
 * カメラエラーの種別
 * - permission_denied: カメラ権限が拒否された
 * - not_available: カメラデバイスが利用不可
 * - capture_failed: 画像キャプチャに失敗
 * - recognition_failed: 画像認識に失敗
 * - unknown: その他のエラー
 */
export type CameraErrorType =
	| "permission_denied"
	| "not_available"
	| "capture_failed"
	| "recognition_failed"
	| "unknown"

/** カメラエラー情報 */
export interface CameraError {
	/** エラー種別 */
	type: CameraErrorType
	/** ユーザー向けエラーメッセージ（子供向けやさしい日本語） */
	message: string
}

/**
 * 画像認識リクエスト
 * バックエンド POST /api/v1/vision/recognize に送信
 */
export interface ImageRecognitionRequest {
	/** Base64エンコードされた画像データ */
	image: string
	/** 認識タイプ */
	recognition_type?: "homework_problem" | "handwriting" | "diagram"
	/** 予想される教科 */
	expected_subject?: string
}

/**
 * 認識された問題の詳細
 */
export interface ProblemDetail {
	/** 問題文のテキスト */
	text: string
	/** 問題タイプ（arithmetic, word_problem, kanji, reading, other） */
	type: string
	/** 難易度 */
	difficulty: number
	/** 計算式（算数の場合のみ） */
	expression?: string
}

/**
 * 画像認識レスポンス
 * バックエンドから返される認識結果
 */
export interface ImageRecognitionResponse {
	/** 認識成功フラグ */
	success: boolean
	/** 認識された問題リスト */
	problems: ProblemDetail[]
	/** 認識の確信度（0〜1） */
	confidence: number
	/** 子供に確認が必要かどうか */
	needs_confirmation: boolean
}
