/**
 * VoiceWebSocketClient
 *
 * WebSocket client for bidirectional audio streaming with ADK backend.
 * Handles:
 * - Audio data transmission (16kHz 16-bit PCM)
 * - Text message transmission
 * - ADK event parsing (transcriptions, turn completion, audio data)
 */

import type { ADKEvent, VoiceConnectionState, VoiceWebSocketOptions } from "./types"

export class VoiceWebSocketClient {
	private ws: WebSocket | null = null
	private options: VoiceWebSocketOptions
	private _isConnected = false

	constructor(options: VoiceWebSocketOptions) {
		this.options = options
	}

	/**
	 * 接続状態を取得
	 */
	get isConnected(): boolean {
		return this._isConnected
	}

	/**
	 * WebSocket接続を開始
	 */
	connect(): void {
		const url = this.buildWebSocketUrl()
		this.updateConnectionState("connecting")

		this.ws = new WebSocket(url)
		this.setupEventHandlers()
	}

	/**
	 * WebSocket接続を切断
	 */
	disconnect(): void {
		if (this.ws) {
			this.ws.close()
		}
	}

	/**
	 * 音声データを送信（バイナリ）
	 * @param pcmData - 16kHz 16-bit PCM音声データ
	 */
	sendAudio(pcmData: ArrayBuffer): void {
		if (this.ws && this.ws.readyState === WebSocket.OPEN) {
			this.ws.send(pcmData)
		}
	}

	/**
	 * テキストメッセージを送信
	 * @param text - 送信するテキスト
	 */
	sendText(text: string): void {
		if (this.ws && this.ws.readyState === WebSocket.OPEN) {
			const message = JSON.stringify({ type: "text", text })
			this.ws.send(message)
		}
	}

	/**
	 * WebSocket URLを構築
	 */
	private buildWebSocketUrl(): string {
		const { baseUrl, userId, sessionId } = this.options
		// baseUrlの末尾スラッシュを除去
		const cleanBaseUrl = baseUrl.replace(/\/$/, "")
		return `${cleanBaseUrl}/ws/${userId}/${sessionId}`
	}

	/**
	 * WebSocketイベントハンドラを設定
	 */
	private setupEventHandlers(): void {
		if (!this.ws) return

		this.ws.onopen = () => {
			this._isConnected = true
			this.updateConnectionState("connected")
		}

		this.ws.onclose = () => {
			this._isConnected = false
			this.updateConnectionState("disconnected")
		}

		this.ws.onerror = () => {
			this._isConnected = false
			this.updateConnectionState("error")
			this.options.onError("WebSocket接続エラー")
		}

		this.ws.onmessage = (event) => {
			this.handleMessage(event.data)
		}
	}

	/**
	 * 受信メッセージを処理
	 */
	private handleMessage(data: string | ArrayBuffer): void {
		// バイナリデータの場合は直接音声データとして処理
		if (data instanceof ArrayBuffer) {
			this.options.onAudioData(data)
			return
		}

		// JSONメッセージをパース
		let event: ADKEvent
		try {
			event = JSON.parse(data)
		} catch {
			this.options.onError("無効なメッセージ形式")
			return
		}

		this.processADKEvent(event)
	}

	/**
	 * ADKイベントを処理
	 */
	private processADKEvent(event: ADKEvent): void {
		// ターン完了
		if (event.turnComplete) {
			this.options.onTurnComplete()
			return
		}

		// 中断
		if (event.interrupted) {
			this.options.onInterrupted()
			return
		}

		// 入力トランスクリプション（ユーザーの音声）
		if (event.inputTranscription?.text) {
			this.options.onTranscription(
				event.inputTranscription.text,
				true, // isUser
				event.inputTranscription.finished,
			)
		}

		// 出力トランスクリプション（AIの音声）
		if (event.outputTranscription?.text) {
			this.options.onTranscription(
				event.outputTranscription.text,
				false, // isUser
				event.outputTranscription.finished,
			)
		}

		// Phase 2a: ツール実行イベント
		if (event.toolExecution) {
			this.options.onToolExecution?.(
				event.toolExecution.toolName,
				event.toolExecution.status,
				event.toolExecution.result,
			)
		}

		// Phase 2b: エージェント遷移イベント
		if (event.agentTransition) {
			this.options.onAgentTransition?.(
				event.agentTransition.fromAgent,
				event.agentTransition.toAgent,
				event.agentTransition.reason,
			)
		}

		// Phase 2d: 感情更新イベント
		if (event.emotionUpdate) {
			this.options.onEmotionUpdate?.(
				event.emotionUpdate.emotion,
				event.emotionUpdate.frustrationLevel,
				event.emotionUpdate.engagementLevel,
			)
		}

		// コンテンツ（音声データまたはテキスト）
		if (event.content?.parts) {
			for (const part of event.content.parts) {
				// 音声データ
				if (part.inlineData?.mimeType?.startsWith("audio/")) {
					const audioData = this.base64ToArrayBuffer(part.inlineData.data)
					this.options.onAudioData(audioData)
				}
			}
		}
	}

	/**
	 * 接続状態を更新
	 */
	private updateConnectionState(state: VoiceConnectionState): void {
		this.options.onConnectionChange(state)
	}

	/**
	 * Base64文字列をArrayBufferに変換
	 */
	private base64ToArrayBuffer(base64: string): ArrayBuffer {
		// Base64URL形式を標準Base64に変換
		let standardBase64 = base64.replace(/-/g, "+").replace(/_/g, "/")

		// パディングを追加
		while (standardBase64.length % 4) {
			standardBase64 += "="
		}

		const binaryString = atob(standardBase64)
		const bytes = new Uint8Array(binaryString.length)
		for (let i = 0; i < binaryString.length; i++) {
			bytes[i] = binaryString.charCodeAt(i)
		}
		return bytes.buffer
	}
}
