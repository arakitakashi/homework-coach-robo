/**
 * useVoiceStream フックテスト
 */

import { act, renderHook } from "@testing-library/react"
import { createStore, Provider } from "jotai"
import type { ReactNode } from "react"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import { useVoiceStream } from "./useVoiceStream"

// VoiceWebSocketClient モック（vi.hoistedでホイスト時に使用可能にする）
const {
	mockConnect,
	mockDisconnect,
	mockSendText,
	getMockClientOptions,
	setMockClientOptions,
	setMockIsConnected,
	MockVoiceWebSocketClient,
} = vi.hoisted(() => {
	const mockConnect = vi.fn()
	const mockDisconnect = vi.fn()
	const mockSendAudio = vi.fn()
	const mockSendText = vi.fn()

	interface MockClientOptions {
		baseUrl: string
		userId: string
		sessionId: string
		onAudioData: (data: ArrayBuffer) => void
		onTranscription: (text: string, isUser: boolean, finished: boolean) => void
		onTurnComplete: () => void
		onInterrupted: () => void
		onError: (error: string) => void
		onConnectionChange: (state: string) => void
	}

	let mockClientOptions: MockClientOptions | null = null
	let mockIsConnected = false

	// クラスベースのモック
	class MockVoiceWebSocketClient {
		constructor(options: MockClientOptions) {
			mockClientOptions = options
		}
		connect = mockConnect
		disconnect = mockDisconnect
		sendAudio = mockSendAudio
		sendText = mockSendText
		get isConnected() {
			return mockIsConnected
		}
	}

	return {
		mockConnect,
		mockDisconnect,
		mockSendText,
		getMockClientOptions: () => mockClientOptions,
		setMockClientOptions: (opts: MockClientOptions | null) => {
			mockClientOptions = opts
		},
		setMockIsConnected: (val: boolean) => {
			mockIsConnected = val
		},
		MockVoiceWebSocketClient,
	}
})

vi.mock("@/lib/api", () => ({
	VoiceWebSocketClient: MockVoiceWebSocketClient,
}))

// AudioContext モック
const mockClose = vi.fn()
const mockAddModule = vi.fn().mockResolvedValue(undefined)
const mockCreateMediaStreamSource = vi.fn().mockReturnValue({
	connect: vi.fn(),
})

class MockAudioContext {
	sampleRate = 16000
	audioWorklet = {
		addModule: mockAddModule,
	}
	createMediaStreamSource = mockCreateMediaStreamSource
	close = mockClose
	destination = {}
}

class MockAudioWorkletNode {
	port = {
		onmessage: null as ((event: { data: Float32Array }) => void) | null,
		postMessage: vi.fn(),
	}
	connect = vi.fn()
	disconnect = vi.fn()
}

globalThis.AudioContext = MockAudioContext as unknown as typeof AudioContext
globalThis.AudioWorkletNode = MockAudioWorkletNode as unknown as typeof AudioWorkletNode

// MediaDevices モック
const mockGetUserMedia = vi.fn().mockResolvedValue({
	getTracks: () => [{ stop: vi.fn() }],
})

Object.defineProperty(navigator, "mediaDevices", {
	value: { getUserMedia: mockGetUserMedia },
	writable: true,
})

// テスト用ラッパー
function createTestWrapper() {
	const store = createStore()
	const TestWrapper = ({ children }: { children: ReactNode }) => (
		<Provider store={store}>{children}</Provider>
	)
	return { store, TestWrapper }
}

describe("useVoiceStream", () => {
	beforeEach(() => {
		vi.clearAllMocks()
		setMockClientOptions(null)
		setMockIsConnected(false)
	})

	afterEach(() => {
		vi.restoreAllMocks()
	})

	describe("初期状態", () => {
		it("初期状態が正しい", () => {
			const { TestWrapper } = createTestWrapper()
			const { result } = renderHook(() => useVoiceStream(), { wrapper: TestWrapper })

			expect(result.current.connectionState).toBe("disconnected")
			expect(result.current.isRecording).toBe(false)
			expect(result.current.error).toBeNull()
		})
	})

	describe("接続", () => {
		it("connect()でWebSocket接続を開始する", () => {
			const { TestWrapper } = createTestWrapper()
			const { result } = renderHook(() => useVoiceStream(), { wrapper: TestWrapper })

			act(() => {
				result.current.connect("user-1", "session-1")
			})

			expect(mockConnect).toHaveBeenCalled()
		})

		it("接続状態の変更がconnectionStateに反映される", () => {
			const { TestWrapper } = createTestWrapper()
			const { result } = renderHook(() => useVoiceStream(), { wrapper: TestWrapper })

			act(() => {
				result.current.connect("user-1", "session-1")
			})

			// コールバックをシミュレート
			act(() => {
				getMockClientOptions()?.onConnectionChange("connected")
			})

			expect(result.current.connectionState).toBe("connected")
		})
	})

	describe("切断", () => {
		it("disconnect()でWebSocket接続を切断する", () => {
			const { TestWrapper } = createTestWrapper()
			const { result } = renderHook(() => useVoiceStream(), { wrapper: TestWrapper })

			act(() => {
				result.current.connect("user-1", "session-1")
			})

			act(() => {
				result.current.disconnect()
			})

			expect(mockDisconnect).toHaveBeenCalled()
		})
	})

	describe("録音", () => {
		it("startRecording()で録音を開始する", async () => {
			const { TestWrapper } = createTestWrapper()
			const { result } = renderHook(() => useVoiceStream(), { wrapper: TestWrapper })

			// 接続
			act(() => {
				result.current.connect("user-1", "session-1")
			})
			act(() => {
				getMockClientOptions()?.onConnectionChange("connected")
				setMockIsConnected(true)
			})

			// 録音開始
			await act(async () => {
				await result.current.startRecording()
			})

			expect(result.current.isRecording).toBe(true)
			expect(mockGetUserMedia).toHaveBeenCalled()
		})

		it("stopRecording()で録音を停止する", async () => {
			const { TestWrapper } = createTestWrapper()
			const { result } = renderHook(() => useVoiceStream(), { wrapper: TestWrapper })

			// 接続
			act(() => {
				result.current.connect("user-1", "session-1")
			})
			act(() => {
				getMockClientOptions()?.onConnectionChange("connected")
				setMockIsConnected(true)
			})

			// 録音開始
			await act(async () => {
				await result.current.startRecording()
			})

			// 録音停止
			act(() => {
				result.current.stopRecording()
			})

			expect(result.current.isRecording).toBe(false)
		})
	})

	describe("テキスト送信", () => {
		it("sendText()でテキストを送信する", () => {
			const { TestWrapper } = createTestWrapper()
			const { result } = renderHook(() => useVoiceStream(), { wrapper: TestWrapper })

			act(() => {
				result.current.connect("user-1", "session-1")
			})
			act(() => {
				getMockClientOptions()?.onConnectionChange("connected")
				setMockIsConnected(true)
			})

			act(() => {
				result.current.sendText("テストメッセージ")
			})

			expect(mockSendText).toHaveBeenCalledWith("テストメッセージ")
		})
	})

	describe("トランスクリプション", () => {
		it("トランスクリプションを受信してコールバックを呼ぶ", () => {
			const { TestWrapper } = createTestWrapper()
			const onTranscription = vi.fn()
			const { result } = renderHook(() => useVoiceStream({ onTranscription }), {
				wrapper: TestWrapper,
			})

			act(() => {
				result.current.connect("user-1", "session-1")
			})

			// トランスクリプションをシミュレート
			act(() => {
				getMockClientOptions()?.onTranscription("テスト", true, true)
			})

			expect(onTranscription).toHaveBeenCalledWith("テスト", true, true)
		})
	})

	describe("audioLevel", () => {
		it("初期値が0である", () => {
			const { TestWrapper } = createTestWrapper()
			const { result } = renderHook(() => useVoiceStream(), { wrapper: TestWrapper })

			expect(result.current.audioLevel).toBe(0)
		})

		it("録音開始時はaudioLevelが0のまま（データ受信前）", async () => {
			const { TestWrapper } = createTestWrapper()
			const { result } = renderHook(() => useVoiceStream(), { wrapper: TestWrapper })

			// 接続
			act(() => {
				result.current.connect("user-1", "session-1")
			})
			act(() => {
				getMockClientOptions()?.onConnectionChange("connected")
				setMockIsConnected(true)
			})

			// 録音開始
			await act(async () => {
				await result.current.startRecording()
			})

			// workletからデータ受信前はaudioLevelは0
			expect(result.current.audioLevel).toBe(0)
		})

		it("録音停止でaudioLevelが0にリセットされる", async () => {
			const { TestWrapper } = createTestWrapper()
			const { result } = renderHook(() => useVoiceStream(), { wrapper: TestWrapper })

			// 接続
			act(() => {
				result.current.connect("user-1", "session-1")
			})
			act(() => {
				getMockClientOptions()?.onConnectionChange("connected")
				setMockIsConnected(true)
			})

			// 録音開始
			await act(async () => {
				await result.current.startRecording()
			})

			// 録音停止
			act(() => {
				result.current.stopRecording()
			})

			expect(result.current.audioLevel).toBe(0)
		})
	})

	describe("エラーハンドリング", () => {
		it("エラーがerror状態に反映される", () => {
			const { TestWrapper } = createTestWrapper()
			const { result } = renderHook(() => useVoiceStream(), { wrapper: TestWrapper })

			act(() => {
				result.current.connect("user-1", "session-1")
			})

			// エラーをシミュレート
			act(() => {
				getMockClientOptions()?.onError("接続エラー")
			})

			expect(result.current.error).toBe("接続エラー")
		})

		it("clearError()でエラーをクリアする", () => {
			const { TestWrapper } = createTestWrapper()
			const { result } = renderHook(() => useVoiceStream(), { wrapper: TestWrapper })

			act(() => {
				result.current.connect("user-1", "session-1")
			})

			act(() => {
				getMockClientOptions()?.onError("接続エラー")
			})

			act(() => {
				result.current.clearError()
			})

			expect(result.current.error).toBeNull()
		})
	})
})
