import { render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { createStore, Provider } from "jotai"
import type { ReactNode } from "react"
import { beforeEach, describe, expect, it, vi } from "vitest"

// セッションページコンポーネントをテスト用にインポート
import { SessionContent } from "../../src/app/session/SessionContent"

// テスト用のラッパー（Jotaiストアをリセット）
function TestWrapper({ children }: { children: ReactNode }) {
	const store = createStore()
	return <Provider store={store}>{children}</Provider>
}

const renderWithProvider = (ui: ReactNode) => render(ui, { wrapper: TestWrapper })

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
	})

	it("renders character display", () => {
		renderWithProvider(<SessionContent characterType="robot" />)
		expect(screen.getByRole("img", { name: /ロボットキャラクター/i })).toBeInTheDocument()
	})

	it("renders voice interface", () => {
		renderWithProvider(<SessionContent characterType="robot" />)
		expect(screen.getByRole("button", { name: /録音/i })).toBeInTheDocument()
	})

	it("renders dialogue history", () => {
		renderWithProvider(<SessionContent characterType="robot" />)
		expect(screen.getByRole("log")).toBeInTheDocument()
	})

	it("renders hint indicator", () => {
		renderWithProvider(<SessionContent characterType="robot" />)
		expect(screen.getByRole("group", { name: /ヒントレベル/i })).toBeInTheDocument()
	})

	it("renders progress display", () => {
		renderWithProvider(<SessionContent characterType="robot" />)
		expect(screen.getByText(/ポイント/i)).toBeInTheDocument()
	})

	it("shows welcome message from AI", async () => {
		renderWithProvider(<SessionContent characterType="robot" />)
		// AIからのウェルカムメッセージがある（useEffectで追加されるので待機）
		await waitFor(() => {
			expect(screen.getByText(/こんにちは/i)).toBeInTheDocument()
		})
	})

	it("has end session button", () => {
		renderWithProvider(<SessionContent characterType="robot" />)
		expect(screen.getByRole("button", { name: /おわる/i })).toBeInTheDocument()
	})

	it("navigates home when session ended", async () => {
		const user = userEvent.setup()
		renderWithProvider(<SessionContent characterType="robot" />)

		const endButton = screen.getByRole("button", { name: /おわる/i })
		await user.click(endButton)

		expect(mockPush).toHaveBeenCalledWith("/")
	})

	it("is accessible with proper landmarks", () => {
		renderWithProvider(<SessionContent characterType="robot" />)
		expect(screen.getByRole("main")).toBeInTheDocument()
	})
})
