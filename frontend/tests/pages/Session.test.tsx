import { act, render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { createStore, Provider } from "jotai"
import type { ReactNode } from "react"
import { beforeEach, describe, expect, it, vi } from "vitest"

// セッションページコンポーネントをテスト用にインポート
import { SessionContent } from "../../src/app/session/SessionContent"

// useRouterをモック
const mockPush = vi.fn()
vi.mock("next/navigation", () => ({
	useRouter: () => ({
		push: mockPush,
	}),
	useParams: () => ({
		id: "test-session-id",
	}),
}))

// モック用のグローバル変数
let mockCreateSessionResponse: {
	session_id: string
	problem: string
	current_hint_level: number
	tone: string
	turns_count: number
	created_at: string
} | null = null

// VoiceWebSocketClient のコールバックをキャプチャ
interface CapturedVoiceCallbacks {
	onAudioData: (data: ArrayBuffer) => void
	onTranscription: (text: string, isUser: boolean, finished: boolean) => void
	onTurnComplete: () => void
	onInterrupted: () => void
	onError: (error: string) => void
	onConnectionChange: (state: string) => void
}

let capturedVoiceCallbacks: CapturedVoiceCallbacks | null = null
const mockVoiceConnect = vi.fn()
const mockVoiceDisconnect = vi.fn()
let mockVoiceIsConnected = false

// SessionClient, DialogueClient, VoiceWebSocketClient をモック
vi.mock("@/lib/api", () => {
	class MockSessionClient {
		async createSession(): Promise<{
			session_id: string
			problem: string
			current_hint_level: number
			tone: string
			turns_count: number
			created_at: string
		}> {
			if (!mockCreateSessionResponse) {
				throw new Error("モックレスポンスが設定されていません")
			}
			return mockCreateSessionResponse
		}

		async deleteSession(): Promise<void> {
			// 何もしない
		}
	}

	class MockDialogueClient {
		private options: {
			onText: (text: string) => void
			onDone: (sessionId: string) => void
			onError: (error: string, code: string) => void
		}

		constructor(options: {
			baseUrl: string
			onText: (text: string) => void
			onDone: (sessionId: string) => void
			onError: (error: string, code: string) => void
		}) {
			this.options = options
		}

		async run(): Promise<void> {
			this.options.onText("テスト回答")
			this.options.onDone("session-1")
		}

		abort(): void {
			// 何もしない
		}
	}

	class MockVoiceWebSocketClient {
		constructor(
			options: CapturedVoiceCallbacks & { baseUrl: string; userId: string; sessionId: string },
		) {
			capturedVoiceCallbacks = {
				onAudioData: options.onAudioData,
				onTranscription: options.onTranscription,
				onTurnComplete: options.onTurnComplete,
				onInterrupted: options.onInterrupted,
				onError: options.onError,
				onConnectionChange: options.onConnectionChange,
			}
		}
		connect = mockVoiceConnect
		disconnect = mockVoiceDisconnect
		sendAudio = vi.fn()
		sendText = vi.fn()
		get isConnected() {
			return mockVoiceIsConnected
		}
	}

	return {
		SessionClient: MockSessionClient,
		DialogueClient: MockDialogueClient,
		VoiceWebSocketClient: MockVoiceWebSocketClient,
	}
})

// テスト用のラッパー（Jotaiストアをリセット）
function TestWrapper({ children }: { children: ReactNode }) {
	const store = createStore()
	return <Provider store={store}>{children}</Provider>
}

const renderWithProvider = (ui: ReactNode) => render(ui, { wrapper: TestWrapper })

// WebSocketをモック
class MockWebSocket {
	static CONNECTING = 0
	static OPEN = 1
	static CLOSING = 2
	static CLOSED = 3

	readyState = MockWebSocket.OPEN
	onopen: (() => void) | null = null
	onmessage: ((event: { data: string }) => void) | null = null
	onerror: ((error: Error) => void) | null = null
	onclose: (() => void) | null = null
	send = vi.fn()
	close = vi.fn()

	constructor() {
		setTimeout(() => {
			this.onopen?.()
		}, 0)
	}
}

globalThis.WebSocket = MockWebSocket as unknown as typeof WebSocket

// AudioContextをモック
const mockAddModule = vi.fn().mockResolvedValue(undefined)
const mockAudioContextClose = vi.fn().mockResolvedValue(undefined)

class MockAudioContext {
	sampleRate = 24000
	state = "running"
	audioWorklet = {
		addModule: mockAddModule,
	}
	createBufferSource = vi.fn(() => ({
		connect: vi.fn(),
		start: vi.fn(),
		buffer: null,
	}))
	decodeAudioData = vi.fn()
	destination = {}
	close = mockAudioContextClose
	createMediaStreamSource = vi.fn().mockReturnValue({
		connect: vi.fn(),
	})
}

globalThis.AudioContext = MockAudioContext as unknown as typeof AudioContext

// AudioWorkletNode モック
class MockAudioWorkletNode {
	port = {
		postMessage: vi.fn(),
		onmessage: null as ((event: { data: Float32Array }) => void) | null,
	}
	connect = vi.fn()
	disconnect = vi.fn()
}

globalThis.AudioWorkletNode = MockAudioWorkletNode as unknown as typeof AudioWorkletNode

// MediaDevicesをモック
const mockMediaStream = {
	getTracks: () => [{ stop: vi.fn() }],
}

Object.defineProperty(navigator, "mediaDevices", {
	value: {
		getUserMedia: vi.fn().mockResolvedValue(mockMediaStream),
	},
	writable: true,
})

describe("SessionContent", () => {
	beforeEach(() => {
		mockPush.mockClear()
		vi.clearAllMocks()
		capturedVoiceCallbacks = null
		mockVoiceIsConnected = false
		// デフォルトのモックレスポンスを設定
		mockCreateSessionResponse = {
			session_id: "test-session-123",
			problem: "テスト問題",
			current_hint_level: 1,
			tone: "encouraging",
			turns_count: 0,
			created_at: "2026-02-06T10:00:00Z",
		}
	})

	it("renders character display", async () => {
		renderWithProvider(<SessionContent characterType="robot" />)
		// セッション作成完了を待つ
		await waitFor(() => {
			expect(screen.getByRole("img", { name: /ロボットキャラクター/i })).toBeInTheDocument()
		})
	})

	it("renders voice interface", async () => {
		renderWithProvider(<SessionContent characterType="robot" />)
		await waitFor(() => {
			expect(screen.getAllByRole("button", { name: /録音/i })[0]).toBeInTheDocument()
		})
	})

	it("renders dialogue history", async () => {
		renderWithProvider(<SessionContent characterType="robot" />)
		await waitFor(() => {
			expect(screen.getAllByRole("log")[0]).toBeInTheDocument()
		})
	})

	it("renders hint indicator", async () => {
		renderWithProvider(<SessionContent characterType="robot" />)
		await waitFor(() => {
			expect(screen.getByRole("group", { name: /ヒントレベル/i })).toBeInTheDocument()
		})
	})

	it("renders progress display", async () => {
		renderWithProvider(<SessionContent characterType="robot" />)
		await waitFor(() => {
			expect(screen.getAllByText(/ポイント/i)[0]).toBeInTheDocument()
		})
	})

	it("shows welcome message from AI", async () => {
		renderWithProvider(<SessionContent characterType="robot" />)
		// AIからのウェルカムメッセージがある（useEffectで追加されるので待機）
		await waitFor(() => {
			expect(screen.getAllByText(/こんにちは/i)[0]).toBeInTheDocument()
		})
	})

	it("has end session button", async () => {
		renderWithProvider(<SessionContent characterType="robot" />)
		await waitFor(() => {
			expect(screen.getByRole("button", { name: /おわる/i })).toBeInTheDocument()
		})
	})

	it("navigates home when session ended", async () => {
		const user = userEvent.setup()
		renderWithProvider(<SessionContent characterType="robot" />)

		// セッション作成完了を待つ
		await waitFor(() => {
			expect(screen.getByRole("button", { name: /おわる/i })).toBeInTheDocument()
		})

		const endButton = screen.getByRole("button", { name: /おわる/i })
		await user.click(endButton)

		await waitFor(() => {
			expect(mockPush).toHaveBeenCalledWith("/")
		})
	})

	it("is accessible with proper landmarks", async () => {
		renderWithProvider(<SessionContent characterType="robot" />)
		// ローディング中もmainがあるはず
		expect(screen.getByRole("main")).toBeInTheDocument()
	})

	describe("WebSocket音声統合", () => {
		it("セッション作成後にWebSocket接続を開始する", async () => {
			renderWithProvider(<SessionContent characterType="robot" />)

			await waitFor(() => {
				expect(mockVoiceConnect).toHaveBeenCalled()
			})
		})

		it("トランスクリプション（ユーザー、finished=true）で対話履歴にターンが追加される", async () => {
			renderWithProvider(<SessionContent characterType="robot" />)

			// セッション作成完了を待つ
			await waitFor(() => {
				expect(capturedVoiceCallbacks).not.toBeNull()
			})

			// ユーザーのトランスクリプション（finished=true）をシミュレート
			act(() => {
				capturedVoiceCallbacks?.onTranscription("3たす5はいくつ？", true, true)
			})

			await waitFor(() => {
				expect(screen.getAllByText("3たす5はいくつ？")[0]).toBeInTheDocument()
			})
		})

		it("トランスクリプション（AI、finished=true）で対話履歴にターンが追加される", async () => {
			renderWithProvider(<SessionContent characterType="robot" />)

			await waitFor(() => {
				expect(capturedVoiceCallbacks).not.toBeNull()
			})

			// AIのトランスクリプション（finished=true）をシミュレート
			act(() => {
				capturedVoiceCallbacks?.onTranscription("この問題、何を聞いてると思う？", false, true)
			})

			await waitFor(() => {
				expect(screen.getAllByText("この問題、何を聞いてると思う？")[0]).toBeInTheDocument()
			})
		})

		it("トランスクリプション（finished=false）では対話履歴に追加しない", async () => {
			renderWithProvider(<SessionContent characterType="robot" />)

			await waitFor(() => {
				expect(capturedVoiceCallbacks).not.toBeNull()
			})

			// 部分的なトランスクリプション（finished=false）
			act(() => {
				capturedVoiceCallbacks?.onTranscription("3たす", true, false)
			})

			// 部分テキストは対話履歴に表示されない
			expect(screen.queryByText("3たす")).not.toBeInTheDocument()
		})

		it("セッション終了時にWebSocket接続を切断する", async () => {
			const user = userEvent.setup()
			renderWithProvider(<SessionContent characterType="robot" />)

			await waitFor(() => {
				expect(screen.getByRole("button", { name: /おわる/i })).toBeInTheDocument()
			})

			const endButton = screen.getByRole("button", { name: /おわる/i })
			await user.click(endButton)

			await waitFor(() => {
				expect(mockVoiceDisconnect).toHaveBeenCalled()
			})
		})
	})
})
