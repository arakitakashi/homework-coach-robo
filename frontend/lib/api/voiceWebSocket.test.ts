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

	describe("ツール実行イベント", () => {
		it("ツール実行イベントを受信してonToolExecutionコールバックを呼ぶ", () => {
			const options = {
				...createDefaultOptions(),
				onToolExecution: vi.fn(),
			}
			const client = new VoiceWebSocketClient(options)
			client.connect()
			mockWebSocketInstance?.simulateOpen()

			const event: ADKEvent = {
				toolExecution: {
					toolName: "calculate_tool",
					status: "running",
				},
			}
			mockWebSocketInstance?.simulateMessage(JSON.stringify(event))

			expect(options.onToolExecution).toHaveBeenCalledWith("calculate_tool", "running", undefined)
		})

		it("ツール実行完了時に結果も渡す", () => {
			const options = {
				...createDefaultOptions(),
				onToolExecution: vi.fn(),
			}
			const client = new VoiceWebSocketClient(options)
			client.connect()
			mockWebSocketInstance?.simulateOpen()

			const event: ADKEvent = {
				toolExecution: {
					toolName: "calculate_tool",
					status: "completed",
					result: { expression: "2+3", result: 5, isCorrect: true },
				},
			}
			mockWebSocketInstance?.simulateMessage(JSON.stringify(event))

			expect(options.onToolExecution).toHaveBeenCalledWith("calculate_tool", "completed", {
				expression: "2+3",
				result: 5,
				isCorrect: true,
			})
		})

		it("onToolExecutionが未設定でもエラーにならない", () => {
			const client = new VoiceWebSocketClient(defaultOptions)
			client.connect()
			mockWebSocketInstance?.simulateOpen()

			const event: ADKEvent = {
				toolExecution: {
					toolName: "calculate_tool",
					status: "running",
				},
			}

			expect(() => {
				mockWebSocketInstance?.simulateMessage(JSON.stringify(event))
			}).not.toThrow()
		})
	})

	describe("エージェント遷移イベント", () => {
		it("エージェント遷移イベントを受信してonAgentTransitionコールバックを呼ぶ", () => {
			const options = {
				...createDefaultOptions(),
				onAgentTransition: vi.fn(),
			}
			const client = new VoiceWebSocketClient(options)
			client.connect()
			mockWebSocketInstance?.simulateOpen()

			const event: ADKEvent = {
				agentTransition: {
					fromAgent: "router",
					toAgent: "math_coach",
					reason: "算数の問題を検出",
				},
			}
			mockWebSocketInstance?.simulateMessage(JSON.stringify(event))

			expect(options.onAgentTransition).toHaveBeenCalledWith(
				"router",
				"math_coach",
				"算数の問題を検出",
			)
		})

		it("エージェント遷移でresult付きイベントを処理できる", () => {
			const options = {
				...createDefaultOptions(),
				onAgentTransition: vi.fn(),
			}
			const client = new VoiceWebSocketClient(options)
			client.connect()
			mockWebSocketInstance?.simulateOpen()

			const event: ADKEvent = {
				agentTransition: {
					fromAgent: "math_coach",
					toAgent: "encouragement",
					reason: "フラストレーション検出",
				},
			}
			mockWebSocketInstance?.simulateMessage(JSON.stringify(event))

			expect(options.onAgentTransition).toHaveBeenCalledWith(
				"math_coach",
				"encouragement",
				"フラストレーション検出",
			)
		})

		it("onAgentTransitionが未設定でもエラーにならない", () => {
			const client = new VoiceWebSocketClient(defaultOptions)
			client.connect()
			mockWebSocketInstance?.simulateOpen()

			const event: ADKEvent = {
				agentTransition: {
					fromAgent: "router",
					toAgent: "math_coach",
					reason: "算数の問題を検出",
				},
			}

			expect(() => {
				mockWebSocketInstance?.simulateMessage(JSON.stringify(event))
			}).not.toThrow()
		})
	})

	describe("感情更新イベント", () => {
		it("感情更新イベントを受信してonEmotionUpdateコールバックを呼ぶ", () => {
			const options = {
				...createDefaultOptions(),
				onEmotionUpdate: vi.fn(),
			}
			const client = new VoiceWebSocketClient(options)
			client.connect()
			mockWebSocketInstance?.simulateOpen()

			const event: ADKEvent = {
				emotionUpdate: {
					emotion: "frustrated",
					frustrationLevel: 0.8,
					engagementLevel: 0.3,
				},
			}
			mockWebSocketInstance?.simulateMessage(JSON.stringify(event))

			expect(options.onEmotionUpdate).toHaveBeenCalledWith("frustrated", 0.8, 0.3)
		})

		it("感情更新で各レベル値が正しく渡される", () => {
			const options = {
				...createDefaultOptions(),
				onEmotionUpdate: vi.fn(),
			}
			const client = new VoiceWebSocketClient(options)
			client.connect()
			mockWebSocketInstance?.simulateOpen()

			const event: ADKEvent = {
				emotionUpdate: {
					emotion: "happy",
					frustrationLevel: 0.1,
					engagementLevel: 0.9,
				},
			}
			mockWebSocketInstance?.simulateMessage(JSON.stringify(event))

			expect(options.onEmotionUpdate).toHaveBeenCalledWith("happy", 0.1, 0.9)
		})

		it("onEmotionUpdateが未設定でもエラーにならない", () => {
			const client = new VoiceWebSocketClient(defaultOptions)
			client.connect()
			mockWebSocketInstance?.simulateOpen()

			const event: ADKEvent = {
				emotionUpdate: {
					emotion: "neutral",
					frustrationLevel: 0.0,
					engagementLevel: 0.5,
				},
			}

			expect(() => {
				mockWebSocketInstance?.simulateMessage(JSON.stringify(event))
			}).not.toThrow()
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

	describe("画像イベント", () => {
		describe("sendImageStart()", () => {
			it("接続中にstart_with_imageメッセージを送信する", () => {
				const client = new VoiceWebSocketClient(defaultOptions)
				client.connect()
				mockWebSocketInstance?.simulateOpen()

				client.sendImageStart("3 + 5 = ?", "gs://bucket/image.jpg", "math", { source: "camera" })

				expect(mockWebSocketInstance?.send).toHaveBeenCalledWith(
					JSON.stringify({
						type: "start_with_image",
						payload: {
							problem_text: "3 + 5 = ?",
							image_url: "gs://bucket/image.jpg",
							problem_type: "math",
							metadata: { source: "camera" },
						},
					}),
				)
			})

			it("未接続時は送信しない", () => {
				const client = new VoiceWebSocketClient(defaultOptions)
				client.connect()
				// simulateOpen()を呼ばない（未接続状態）

				client.sendImageStart("問題文", "gs://bucket/image.jpg")

				expect(mockWebSocketInstance?.send).not.toHaveBeenCalled()
			})

			it("オプションパラメータなしで送信できる", () => {
				const client = new VoiceWebSocketClient(defaultOptions)
				client.connect()
				mockWebSocketInstance?.simulateOpen()

				client.sendImageStart("問題文", "gs://bucket/image.jpg")

				expect(mockWebSocketInstance?.send).toHaveBeenCalledWith(
					JSON.stringify({
						type: "start_with_image",
						payload: {
							problem_text: "問題文",
							image_url: "gs://bucket/image.jpg",
						},
					}),
				)
			})
		})

		describe("画像問題確認イベント受信", () => {
			it("image_problem_confirmedイベントでコールバックを呼ぶ", () => {
				const options = {
					...defaultOptions,
					onImageProblemConfirmed: vi.fn(),
				}
				const client = new VoiceWebSocketClient(options)
				client.connect()
				mockWebSocketInstance?.simulateOpen()

				const event = {
					type: "image_problem_confirmed",
					payload: {
						problem_id: "uuid-123",
						coach_response: "画像から問題を読み取りました！",
					},
				}
				mockWebSocketInstance?.simulateMessage(JSON.stringify(event))

				expect(options.onImageProblemConfirmed).toHaveBeenCalledWith(
					"uuid-123",
					"画像から問題を読み取りました！",
				)
			})

			it("onImageProblemConfirmedが未設定でもエラーにならない", () => {
				const client = new VoiceWebSocketClient(defaultOptions)
				client.connect()
				mockWebSocketInstance?.simulateOpen()

				const event = {
					type: "image_problem_confirmed",
					payload: {
						problem_id: "uuid-123",
						coach_response: "確認しました",
					},
				}

				expect(() => {
					mockWebSocketInstance?.simulateMessage(JSON.stringify(event))
				}).not.toThrow()
			})
		})

		describe("画像認識エラーイベント受信", () => {
			it("image_recognition_errorイベントでコールバックを呼ぶ", () => {
				const options = {
					...defaultOptions,
					onImageRecognitionError: vi.fn(),
				}
				const client = new VoiceWebSocketClient(options)
				client.connect()
				mockWebSocketInstance?.simulateOpen()

				const event = {
					type: "image_recognition_error",
					payload: {
						error: "画像が不鮮明です",
						code: "INVALID_PAYLOAD",
					},
				}
				mockWebSocketInstance?.simulateMessage(JSON.stringify(event))

				expect(options.onImageRecognitionError).toHaveBeenCalledWith(
					"画像が不鮮明です",
					"INVALID_PAYLOAD",
				)
			})

			it("onImageRecognitionErrorが未設定でもエラーにならない", () => {
				const client = new VoiceWebSocketClient(defaultOptions)
				client.connect()
				mockWebSocketInstance?.simulateOpen()

				const event = {
					type: "image_recognition_error",
					payload: {
						error: "エラー",
						code: "ERROR",
					},
				}

				expect(() => {
					mockWebSocketInstance?.simulateMessage(JSON.stringify(event))
				}).not.toThrow()
			})
		})
	})
})
