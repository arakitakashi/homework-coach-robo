/**
 * WebSocket通信関連の型定義
 */

import type { HintLevel, Speaker } from "./dialogue"
import type { AgentType, EmotionType, ToolExecutionStatus, ToolName } from "./phase2"

/** 音声データメッセージ */
export interface AudioMessage {
	type: "audio"
	data: ArrayBuffer
}

/** 文字起こしメッセージ */
export interface TranscriptMessage {
	type: "transcript"
	text: string
	speaker: Speaker
}

/** ヒントレベルメッセージ */
export interface HintLevelMessage {
	type: "hint_level"
	level: HintLevel
}

/** セッション開始メッセージ */
export interface SessionStartMessage {
	type: "session_start"
	sessionId: string
}

/** セッション終了メッセージ */
export interface SessionEndMessage {
	type: "session_end"
}

/** エラーメッセージ */
export interface ErrorMessage {
	type: "error"
	message: string
}

/** Phase 2a: ツール実行メッセージ */
export interface ToolExecutionMessage {
	type: "tool_execution"
	toolName: ToolName
	status: ToolExecutionStatus
	result?: Record<string, unknown>
}

/** Phase 2b: エージェント切り替えメッセージ */
export interface AgentTransitionMessage {
	type: "agent_transition"
	fromAgent: AgentType
	toAgent: AgentType
	reason: string
}

/** Phase 2d: 感情更新メッセージ */
export interface EmotionUpdateMessage {
	type: "emotion_update"
	emotion: EmotionType
	frustrationLevel: number
	engagementLevel: number
}

/** 画像問題開始メッセージ（クライアント → サーバー） */
export interface StartWithImageMessage {
	type: "start_with_image"
	payload: {
		problem_text: string
		problem_type?: string
		image_url: string
		metadata?: Record<string, unknown>
	}
}

/** 画像問題確認メッセージ（サーバー → クライアント） */
export interface ImageProblemConfirmedMessage {
	type: "image_problem_confirmed"
	payload: {
		problem_id: string
		coach_response: string
	}
}

/** 画像認識エラーメッセージ（サーバー → クライアント） */
export interface ImageRecognitionErrorMessage {
	type: "image_recognition_error"
	payload: {
		error: string
		code: string
	}
}

/** WebSocketメッセージ（受信） */
export type WebSocketIncomingMessage =
	| AudioMessage
	| TranscriptMessage
	| HintLevelMessage
	| SessionStartMessage
	| SessionEndMessage
	| ErrorMessage
	| ToolExecutionMessage
	| AgentTransitionMessage
	| EmotionUpdateMessage
	| ImageProblemConfirmedMessage
	| ImageRecognitionErrorMessage

/** WebSocketメッセージ（送信） */
export type WebSocketOutgoingMessage = AudioMessage | SessionEndMessage | StartWithImageMessage

/** WebSocket接続状態 */
export type WebSocketConnectionState = "disconnected" | "connecting" | "connected" | "error"
