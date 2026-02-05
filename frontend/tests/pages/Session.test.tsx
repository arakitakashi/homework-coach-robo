import { render, screen, waitFor } from "@testing-library/react"
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

// SessionClient と DialogueClient をモック
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

	return {
		SessionClient: MockSessionClient,
		DialogueClient: MockDialogueClient,
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
const mockAudioContext = {
	createBufferSource: vi.fn(() => ({
		connect: vi.fn(),
		start: vi.fn(),
		buffer: null,
	})),
	decodeAudioData: vi.fn(),
	destination: {},
}

class MockAudioContext {
	createBufferSource = mockAudioContext.createBufferSource
	decodeAudioData = mockAudioContext.decodeAudioData
	destination = mockAudioContext.destination
}

globalThis.AudioContext = MockAudioContext as unknown as typeof AudioContext

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
			expect(screen.getByRole("button", { name: /録音/i })).toBeInTheDocument()
		})
	})

	it("renders dialogue history", async () => {
		renderWithProvider(<SessionContent characterType="robot" />)
		await waitFor(() => {
			expect(screen.getByRole("log")).toBeInTheDocument()
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
			expect(screen.getByText(/ポイント/i)).toBeInTheDocument()
		})
	})

	it("shows welcome message from AI", async () => {
		renderWithProvider(<SessionContent characterType="robot" />)
		// AIからのウェルカムメッセージがある（useEffectで追加されるので待機）
		await waitFor(() => {
			expect(screen.getByText(/こんにちは/i)).toBeInTheDocument()
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
})
