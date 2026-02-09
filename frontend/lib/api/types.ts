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

// ============================================
// Voice WebSocket API 型定義
// ============================================

/** WebSocket接続状態 */
export type VoiceConnectionState = "disconnected" | "connecting" | "connected" | "error"

/** トランスクリプションイベント */
export interface TranscriptionEvent {
	/** トランスクリプションテキスト */
	text: string
	/** 完了フラグ */
	finished: boolean
}

/** ADKツール実行イベント */
export interface ADKToolExecutionEvent {
	/** ツール名 */
	toolName: string
	/** 実行ステータス */
	status: string
	/** 実行結果（完了時） */
	result?: Record<string, unknown>
}

/** ADKエージェント遷移イベント */
export interface ADKAgentTransitionEvent {
	/** 遷移元エージェント */
	fromAgent: string
	/** 遷移先エージェント */
	toAgent: string
	/** 遷移理由 */
	reason: string
}

/** ADK感情更新イベント */
export interface ADKEmotionUpdateEvent {
	/** 検出された感情 */
	emotion: string
	/** フラストレーションレベル（0-1） */
	frustrationLevel: number
	/** エンゲージメントレベル（0-1） */
	engagementLevel: number
}

/** ADKイベント - サーバーからのWebSocketメッセージ */
export interface ADKEvent {
	/** イベント発行者 */
	author?: string
	/** ターン完了フラグ */
	turnComplete?: boolean
	/** 中断フラグ */
	interrupted?: boolean
	/** 入力トランスクリプション（ユーザーの音声） */
	inputTranscription?: TranscriptionEvent
	/** 出力トランスクリプション（AIの音声） */
	outputTranscription?: TranscriptionEvent
	/** コンテンツ */
	content?: {
		parts: ADKContentPart[]
	}
	/** Phase 2a: ツール実行イベント */
	toolExecution?: ADKToolExecutionEvent
	/** Phase 2b: エージェント遷移イベント */
	agentTransition?: ADKAgentTransitionEvent
	/** Phase 2d: 感情更新イベント */
	emotionUpdate?: ADKEmotionUpdateEvent
}

/** ADKコンテンツパート */
export interface ADKContentPart {
	/** テキスト */
	text?: string
	/** インラインデータ（音声など） */
	inlineData?: {
		mimeType: string
		data: string
	}
}

/** クライアントからサーバーへのテキストメッセージ */
export interface VoiceTextMessage {
	type: "text"
	text: string
}

/** VoiceWebSocketClientのオプション */
export interface VoiceWebSocketOptions {
	/** ベースURL（ws:// または wss://） */
	baseUrl: string
	/** ユーザーID */
	userId: string
	/** セッションID */
	sessionId: string
	/** 音声データ受信コールバック */
	onAudioData: (data: ArrayBuffer) => void
	/** トランスクリプション受信コールバック */
	onTranscription: (text: string, isUser: boolean, finished: boolean) => void
	/** ターン完了コールバック */
	onTurnComplete: () => void
	/** 中断コールバック */
	onInterrupted: () => void
	/** エラーコールバック */
	onError: (error: string) => void
	/** 接続状態変更コールバック */
	onConnectionChange: (state: VoiceConnectionState) => void
	/** Phase 2a: ツール実行コールバック */
	onToolExecution?: (toolName: string, status: string, result?: Record<string, unknown>) => void
	/** Phase 2b: エージェント遷移コールバック */
	onAgentTransition?: (fromAgent: string, toAgent: string, reason: string) => void
	/** Phase 2d: 感情更新コールバック */
	onEmotionUpdate?: (emotion: string, frustrationLevel: number, engagementLevel: number) => void
}
