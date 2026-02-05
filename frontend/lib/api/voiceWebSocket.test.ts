/**
 * VoiceWebSocketClient テスト
 */

import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import type { ADKEvent } from "./types"
import { VoiceWebSocketClient } from "./voiceWebSocket"

// WebSocketモック
class MockWebSocket {
	static CONNECTING = 0
	static OPEN = 1
	static CLOSING = 2
	static CLOSED = 3

	readyState = MockWebSocket.CONNECTING
	url: string
	onopen: (() => void) | null = null
	onmessage: ((event: { data: string | ArrayBuffer }) => void) | null = null
	onerror: ((event: Event) => void) | null = null
	onclose: (() => void) | null = null
	send = vi.fn()
	close = vi.fn()

	constructor(url: string) {
		this.url = url
	}

	// テストヘルパー: 接続を開く
	simulateOpen() {
		this.readyState = MockWebSocket.OPEN
		this.onopen?.()
	}

	// テストヘルパー: メッセージを受信
	simulateMessage(data: string | ArrayBuffer) {
		this.onmessage?.({ data })
	}

	// テストヘルパー: エラーを発生
	simulateError() {
		this.onerror?.(new Event("error"))
	}

	// テストヘルパー: 接続を閉じる
	simulateClose() {
		this.readyState = MockWebSocket.CLOSED
		this.onclose?.()
	}
}

// グローバルWebSocketをモック
const originalWebSocket = globalThis.WebSocket
let mockWebSocketInstance: MockWebSocket | null = null

// WebSocketモックコンストラクタ
class MockWebSocketConstructor extends MockWebSocket {
	constructor(url: string) {
		super(url)
		mockWebSocketInstance = this
	}
}

beforeEach(() => {
	mockWebSocketInstance = null
	// クラスとして代入することでnewで呼び出し可能にする
	globalThis.WebSocket = MockWebSocketConstructor as unknown as typeof WebSocket
})

afterEach(() => {
	globalThis.WebSocket = originalWebSocket
	vi.restoreAllMocks()
})

describe("VoiceWebSocketClient", () => {
	// 各テストで新しいモック関数を作成するためのファクトリ
	const createDefaultOptions = () => ({
		baseUrl: "ws://localhost:8000",
		userId: "test-user",
		sessionId: "test-session",
		onAudioData: vi.fn(),
		onTranscription: vi.fn(),
		onTurnComplete: vi.fn(),
		onInterrupted: vi.fn(),
		onError: vi.fn(),
		onConnectionChange: vi.fn(),
	})

	let defaultOptions: ReturnType<typeof createDefaultOptions>

	beforeEach(() => {
		defaultOptions = createDefaultOptions()
	})

	describe("接続", () => {
		it("正しいURLでWebSocket接続を開始する", () => {
			const client = new VoiceWebSocketClient(defaultOptions)
			client.connect()

			expect(mockWebSocketInstance?.url).toBe("ws://localhost:8000/ws/test-user/test-session")
		})

		it("HTTPS環境ではwss://を使用する", () => {
			const client = new VoiceWebSocketClient({
				...defaultOptions,
				baseUrl: "wss://example.com",
			})
			client.connect()

			expect(mockWebSocketInstance?.url).toBe("wss://example.com/ws/test-user/test-session")
		})

		it("接続中にconnecting状態を通知する", () => {
			const client = new VoiceWebSocketClient(defaultOptions)
			client.connect()

			expect(defaultOptions.onConnectionChange).toHaveBeenCalledWith("connecting")
		})

		it("接続成功時にconnected状態を通知する", () => {
			const client = new VoiceWebSocketClient(defaultOptions)
			client.connect()

			mockWebSocketInstance?.simulateOpen()

			expect(defaultOptions.onConnectionChange).toHaveBeenCalledWith("connected")
		})

		it("接続が開いた後、isConnectedがtrueになる", () => {
			const client = new VoiceWebSocketClient(defaultOptions)
			client.connect()

			expect(client.isConnected).toBe(false)

			mockWebSocketInstance?.simulateOpen()

			expect(client.isConnected).toBe(true)
		})
	})

	describe("切断", () => {
		it("disconnect()でWebSocketを閉じる", () => {
			const client = new VoiceWebSocketClient(defaultOptions)
			client.connect()
			mockWebSocketInstance?.simulateOpen()

			client.disconnect()

			expect(mockWebSocketInstance?.close).toHaveBeenCalled()
		})

		it("切断後にdisconnected状態を通知する", () => {
			const client = new VoiceWebSocketClient(defaultOptions)
			client.connect()
			mockWebSocketInstance?.simulateOpen()

			client.disconnect()
			mockWebSocketInstance?.simulateClose()

			expect(defaultOptions.onConnectionChange).toHaveBeenCalledWith("disconnected")
		})
	})

	describe("音声データ送信", () => {
		it("ArrayBufferをバイナリで送信する", () => {
			const client = new VoiceWebSocketClient(defaultOptions)
			client.connect()
			mockWebSocketInstance?.simulateOpen()

			const audioData = new ArrayBuffer(256)
			client.sendAudio(audioData)

			expect(mockWebSocketInstance?.send).toHaveBeenCalledWith(audioData)
		})

		it("接続前に送信しようとしてもエラーにならない", () => {
			const client = new VoiceWebSocketClient(defaultOptions)

			const audioData = new ArrayBuffer(256)
			expect(() => client.sendAudio(audioData)).not.toThrow()
		})
	})

	describe("テキストメッセージ送信", () => {
		it("テキストメッセージをJSON形式で送信する", () => {
			const client = new VoiceWebSocketClient(defaultOptions)
			client.connect()
			mockWebSocketInstance?.simulateOpen()

			client.sendText("こんにちは")

			expect(mockWebSocketInstance?.send).toHaveBeenCalledWith(
				JSON.stringify({ type: "text", text: "こんにちは" }),
			)
		})
	})

	describe("メッセージ受信", () => {
		it("音声データを受信してコールバックを呼ぶ", () => {
			const client = new VoiceWebSocketClient(defaultOptions)
			client.connect()
			mockWebSocketInstance?.simulateOpen()

			// ADKイベント: 音声データ
			const event: ADKEvent = {
				content: {
					parts: [
						{
							inlineData: {
								mimeType: "audio/pcm",
								data: "AAAA", // Base64エンコードされた音声データ
							},
						},
					],
				},
			}
			mockWebSocketInstance?.simulateMessage(JSON.stringify(event))

			expect(defaultOptions.onAudioData).toHaveBeenCalled()
		})

		it("入力トランスクリプションを受信してコールバックを呼ぶ", () => {
			const client = new VoiceWebSocketClient(defaultOptions)
			client.connect()
			mockWebSocketInstance?.simulateOpen()

			const event: ADKEvent = {
				inputTranscription: {
					text: "テスト入力",
					finished: true,
				},
			}
			mockWebSocketInstance?.simulateMessage(JSON.stringify(event))

			expect(defaultOptions.onTranscription).toHaveBeenCalledWith("テスト入力", true, true)
		})

		it("出力トランスクリプションを受信してコールバックを呼ぶ", () => {
			const client = new VoiceWebSocketClient(defaultOptions)
			client.connect()
			mockWebSocketInstance?.simulateOpen()

			const event: ADKEvent = {
				outputTranscription: {
					text: "AIの回答",
					finished: false,
				},
			}
			mockWebSocketInstance?.simulateMessage(JSON.stringify(event))

			expect(defaultOptions.onTranscription).toHaveBeenCalledWith("AIの回答", false, false)
		})

		it("ターン完了イベントを受信してコールバックを呼ぶ", () => {
			const client = new VoiceWebSocketClient(defaultOptions)
			client.connect()
			mockWebSocketInstance?.simulateOpen()

			const event: ADKEvent = {
				turnComplete: true,
			}
			mockWebSocketInstance?.simulateMessage(JSON.stringify(event))

			expect(defaultOptions.onTurnComplete).toHaveBeenCalled()
		})

		it("中断イベントを受信してコールバックを呼ぶ", () => {
			const client = new VoiceWebSocketClient(defaultOptions)
			client.connect()
			mockWebSocketInstance?.simulateOpen()

			const event: ADKEvent = {
				interrupted: true,
			}
			mockWebSocketInstance?.simulateMessage(JSON.stringify(event))

			expect(defaultOptions.onInterrupted).toHaveBeenCalled()
		})
	})

	describe("エラーハンドリング", () => {
		it("WebSocketエラー時にerror状態を通知する", () => {
			const client = new VoiceWebSocketClient(defaultOptions)
			client.connect()

			mockWebSocketInstance?.simulateError()

			expect(defaultOptions.onConnectionChange).toHaveBeenCalledWith("error")
			expect(defaultOptions.onError).toHaveBeenCalled()
		})

		it("無効なJSONを受信してもクラッシュしない", () => {
			const client = new VoiceWebSocketClient(defaultOptions)
			client.connect()
			mockWebSocketInstance?.simulateOpen()

			expect(() => {
				mockWebSocketInstance?.simulateMessage("invalid json {")
			}).not.toThrow()

			expect(defaultOptions.onError).toHaveBeenCalled()
		})
	})
})
