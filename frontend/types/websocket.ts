/**
 * WebSocket通信関連の型定義
 */

import type { HintLevel, Speaker } from "./dialogue"

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

/** WebSocketメッセージ（受信） */
export type WebSocketIncomingMessage =
	| AudioMessage
	| TranscriptMessage
	| HintLevelMessage
	| SessionStartMessage
	| SessionEndMessage
	| ErrorMessage

/** WebSocketメッセージ（送信） */
export type WebSocketOutgoingMessage = AudioMessage | SessionEndMessage

/** WebSocket接続状態 */
export type WebSocketConnectionState = "disconnected" | "connecting" | "connected" | "error"
