/**
 * エラーコード定数
 * フロントエンド・バックエンド間で共有
 */

export const ErrorCodes = {
	// 認証エラー (1xxx)
	AUTH_REQUIRED: "E1001",
	AUTH_INVALID_TOKEN: "E1002",
	AUTH_TOKEN_EXPIRED: "E1003",

	// セッションエラー (2xxx)
	SESSION_NOT_FOUND: "E2001",
	SESSION_EXPIRED: "E2002",
	SESSION_ALREADY_ACTIVE: "E2003",

	// バリデーションエラー (3xxx)
	VALIDATION_FAILED: "E3001",
	INVALID_INPUT: "E3002",

	// リソースエラー (4xxx)
	RESOURCE_NOT_FOUND: "E4001",
	RESOURCE_ALREADY_EXISTS: "E4002",

	// 外部サービスエラー (5xxx)
	GEMINI_API_ERROR: "E5001",
	FIRESTORE_ERROR: "E5002",
	REDIS_ERROR: "E5003",

	// サーバーエラー (9xxx)
	INTERNAL_ERROR: "E9001",
	SERVICE_UNAVAILABLE: "E9002",
} as const

export type ErrorCode = (typeof ErrorCodes)[keyof typeof ErrorCodes]
