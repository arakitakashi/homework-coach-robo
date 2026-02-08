/**
 * SessionContent コンポーネントテスト
 */

import { act, render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { createStore, Provider } from "jotai"
import { type ReactNode, useMemo } from "react"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import { activeToolExecutionsAtom } from "@/store/atoms/phase2"
import type { ToolExecution } from "@/types"
import { SessionContent } from "./SessionContent"

// Next.js router mock
const mockPush = vi.fn()
vi.mock("next/navigation", () => ({
	useRouter: () => ({
		push: mockPush,
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
let mockCreateSessionError: Error | null = null
let mockDialogueText = ""
let mockDialogueError: string | null = null

// useVoiceStreamのコールバックをキャプチャする変数
let capturedVoiceStreamOptions: {
	onToolExecution?: (toolName: string, status: string, result?: Record<string, unknown>) => void
} = {}

// useVoiceStreamをモック（optionsをキャプチャ）
vi.mock("@/lib/hooks/useVoiceStream", () => ({
	useVoiceStream: (options?: {
		onToolExecution?: (toolName: string, status: string, result?: Record<string, unknown>) => void
	}) => {
		if (options) {
			capturedVoiceStreamOptions = options
		}
		return {
			connectionState: "disconnected",
			isRecording: false,
			audioLevel: 0,
			error: null,
			connect: vi.fn(),
			disconnect: vi.fn(),
			startRecording: vi.fn(),
			stopRecording: vi.fn(),
			sendText: vi.fn(),
			clearError: vi.fn(),
		}
	},
}))

// usePcmPlayerをモック
vi.mock("@/lib/hooks/usePcmPlayer", () => ({
	usePcmPlayer: () => ({
		isPlaying: false,
		feedAudio: vi.fn(),
		stop: vi.fn(),
		initialize: vi.fn().mockResolvedValue(undefined),
		cleanup: vi.fn(),
	}),
}))

// SessionClientをモック
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
			if (mockCreateSessionError) {
				throw mockCreateSessionError
			}
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
			if (mockDialogueError) {
				this.options.onError(mockDialogueError, "TEST_ERROR")
				return
			}
			if (mockDialogueText) {
				this.options.onText(mockDialogueText)
			}
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

// テスト用ラッパー
function createTestWrapper() {
	const store = createStore()
	const TestWrapper = ({ children }: { children: ReactNode }) => {
		const memoizedStore = useMemo(() => store, [])
		return <Provider store={memoizedStore}>{children}</Provider>
	}
	return { store, TestWrapper }
}

describe("SessionContent", () => {
	beforeEach(() => {
		mockCreateSessionResponse = {
			session_id: "test-session-123",
			problem: "テスト問題",
			current_hint_level: 1,
			tone: "encouraging",
			turns_count: 0,
			created_at: "2026-02-06T10:00:00Z",
		}
		mockCreateSessionError = null
		mockDialogueText = "ロボットからの回答"
		mockDialogueError = null
		mockPush.mockClear()
		capturedVoiceStreamOptions = {}
	})

	afterEach(() => {
		vi.clearAllMocks()
	})

	describe("初期化", () => {
		it("セッション作成後にメインUIが表示される", async () => {
			const { TestWrapper } = createTestWrapper()

			render(<SessionContent characterType="robot" />, { wrapper: TestWrapper })

			// セッション作成後、テキスト入力が表示されることを確認
			await waitFor(() => {
				expect(screen.getByPlaceholderText("ここにかいてね")).toBeInTheDocument()
			})
		})

		it("ウェルカムメッセージが表示される", async () => {
			const { TestWrapper } = createTestWrapper()

			render(<SessionContent characterType="robot" />, { wrapper: TestWrapper })

			await waitFor(() => {
				expect(screen.getByText("こんにちは！いっしょにがんばろうね！")).toBeInTheDocument()
			})
		})

		it("おわるボタンが表示される", async () => {
			const { TestWrapper } = createTestWrapper()

			render(<SessionContent characterType="robot" />, { wrapper: TestWrapper })

			await waitFor(() => {
				expect(screen.getByRole("button", { name: "おわる" })).toBeInTheDocument()
			})
		})
	})

	describe("セッション作成エラー", () => {
		it("エラー時にエラーメッセージが表示される", async () => {
			mockCreateSessionError = new Error("接続エラー")

			const { TestWrapper } = createTestWrapper()

			render(<SessionContent characterType="robot" />, { wrapper: TestWrapper })

			await waitFor(() => {
				expect(screen.getByText("接続エラー")).toBeInTheDocument()
			})
		})

		it("もういちどボタンでリトライできる", async () => {
			mockCreateSessionError = new Error("接続エラー")

			const { TestWrapper } = createTestWrapper()

			render(<SessionContent characterType="robot" />, { wrapper: TestWrapper })

			await waitFor(() => {
				expect(screen.getByRole("button", { name: "もういちど" })).toBeInTheDocument()
			})

			// エラーをクリアしてリトライ
			mockCreateSessionError = null

			const retryButton = screen.getByRole("button", { name: "もういちど" })
			await userEvent.click(retryButton)

			await waitFor(() => {
				expect(screen.getByPlaceholderText("ここにかいてね")).toBeInTheDocument()
			})
		})

		it("もどるボタンでホームに戻る", async () => {
			mockCreateSessionError = new Error("接続エラー")

			const { TestWrapper } = createTestWrapper()

			render(<SessionContent characterType="robot" />, { wrapper: TestWrapper })

			await waitFor(() => {
				expect(screen.getByRole("button", { name: "もどる" })).toBeInTheDocument()
			})

			const backButton = screen.getByRole("button", { name: "もどる" })
			await userEvent.click(backButton)

			expect(mockPush).toHaveBeenCalledWith("/")
		})
	})

	describe("メッセージ送信", () => {
		it("テキストを入力して送信できる", async () => {
			const { TestWrapper } = createTestWrapper()

			render(<SessionContent characterType="robot" />, { wrapper: TestWrapper })

			// セッション作成完了を待つ
			await waitFor(() => {
				expect(screen.getByPlaceholderText("ここにかいてね")).toBeInTheDocument()
			})

			const input = screen.getByPlaceholderText("ここにかいてね")
			await userEvent.type(input, "テストメッセージ")

			const submitButton = screen.getByRole("button", { name: "送信" })
			await userEvent.click(submitButton)

			// ユーザーメッセージが対話履歴に追加される
			await waitFor(() => {
				expect(screen.getByText("テストメッセージ")).toBeInTheDocument()
			})
		})

		it("ロボットの回答が対話履歴に追加される", async () => {
			const { TestWrapper } = createTestWrapper()

			render(<SessionContent characterType="robot" />, { wrapper: TestWrapper })

			await waitFor(() => {
				expect(screen.getByPlaceholderText("ここにかいてね")).toBeInTheDocument()
			})

			const input = screen.getByPlaceholderText("ここにかいてね")
			await userEvent.type(input, "テスト")

			const submitButton = screen.getByRole("button", { name: "送信" })
			await userEvent.click(submitButton)

			// ロボットの回答が表示される
			await waitFor(() => {
				expect(screen.getByText("ロボットからの回答")).toBeInTheDocument()
			})
		})
	})

	describe("セッション終了", () => {
		it("おわるボタンでホームに戻る", async () => {
			const { TestWrapper } = createTestWrapper()

			render(<SessionContent characterType="robot" />, { wrapper: TestWrapper })

			await waitFor(() => {
				expect(screen.getByRole("button", { name: "おわる" })).toBeInTheDocument()
			})

			const endButton = screen.getByRole("button", { name: "おわる" })
			await userEvent.click(endButton)

			await waitFor(() => {
				expect(mockPush).toHaveBeenCalledWith("/")
			})
		})
	})

	describe("ツール実行表示", () => {
		it("ツール実行中にToolExecutionDisplayが表示される", async () => {
			const { store, TestWrapper } = createTestWrapper()

			render(<SessionContent characterType="robot" />, { wrapper: TestWrapper })

			// セッション作成完了を待つ
			await waitFor(() => {
				expect(screen.getByPlaceholderText("ここにかいてね")).toBeInTheDocument()
			})

			// ツール実行中の状態をatomに設定
			const toolExecution: ToolExecution = {
				toolName: "calculate_tool",
				status: "running",
				timestamp: new Date(),
			}
			store.set(activeToolExecutionsAtom, [toolExecution])

			// ToolExecutionDisplayが表示される
			await waitFor(() => {
				expect(screen.getByText("けいさん")).toBeInTheDocument()
			})
		})

		it("ツール実行がない場合はToolExecutionDisplayが非表示", async () => {
			const { TestWrapper } = createTestWrapper()

			render(<SessionContent characterType="robot" />, { wrapper: TestWrapper })

			// セッション作成完了を待つ
			await waitFor(() => {
				expect(screen.getByPlaceholderText("ここにかいてね")).toBeInTheDocument()
			})

			// ToolExecutionDisplayが表示されない
			expect(screen.queryByText("けいさん")).not.toBeInTheDocument()
		})

		it("onToolExecutionコールバックがactiveToolExecutionsAtomを更新する", async () => {
			const { TestWrapper } = createTestWrapper()

			render(<SessionContent characterType="robot" />, { wrapper: TestWrapper })

			// セッション作成完了を待つ
			await waitFor(() => {
				expect(screen.getByPlaceholderText("ここにかいてね")).toBeInTheDocument()
			})

			// useVoiceStreamに渡されたonToolExecutionコールバックが存在することを確認
			expect(capturedVoiceStreamOptions.onToolExecution).toBeDefined()

			// コールバックを実行してツール実行イベントをシミュレート
			act(() => {
				capturedVoiceStreamOptions.onToolExecution?.("calculate_tool", "running")
			})

			// ToolExecutionDisplayにツール名が表示される
			await waitFor(() => {
				expect(screen.getByText("けいさん")).toBeInTheDocument()
			})
		})

		it("onToolExecutionコールバックでcompletedステータスを処理できる", async () => {
			const { TestWrapper } = createTestWrapper()

			render(<SessionContent characterType="robot" />, { wrapper: TestWrapper })

			// セッション作成完了を待つ
			await waitFor(() => {
				expect(screen.getByPlaceholderText("ここにかいてね")).toBeInTheDocument()
			})

			// ツール実行開始
			act(() => {
				capturedVoiceStreamOptions.onToolExecution?.("calculate_tool", "running")
			})

			await waitFor(() => {
				expect(screen.getByText("けいさん")).toBeInTheDocument()
			})

			// ツール実行完了
			act(() => {
				capturedVoiceStreamOptions.onToolExecution?.("calculate_tool", "completed", { answer: 42 })
			})

			// completedステータスで更新される
			await waitFor(() => {
				expect(screen.getByText("けいさん")).toBeInTheDocument()
			})
		})
	})
})
