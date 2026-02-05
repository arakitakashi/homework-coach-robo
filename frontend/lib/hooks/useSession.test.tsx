/**
 * useSession フックテスト
 */

import { act, renderHook } from "@testing-library/react"
import { createStore, Provider } from "jotai"
import { type ReactNode, useMemo } from "react"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import { useSession } from "./useSession"

// モック用のレスポンスと動作を格納するグローバル変数
let mockCreateSessionResponse: {
	session_id: string
	problem: string
	current_hint_level: number
	tone: string
	turns_count: number
	created_at: string
} | null = null
let mockCreateSessionError: Error | null = null
let mockDeleteSessionError: Error | null = null
let _createSessionCallCount = 0
let deleteSessionCallCount = 0

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
			_createSessionCallCount++
			if (mockCreateSessionError) {
				throw mockCreateSessionError
			}
			if (!mockCreateSessionResponse) {
				throw new Error("モックレスポンスが設定されていません")
			}
			return mockCreateSessionResponse
		}

		async deleteSession(): Promise<void> {
			deleteSessionCallCount++
			if (mockDeleteSessionError) {
				throw mockDeleteSessionError
			}
		}
	}

	return {
		SessionClient: MockSessionClient,
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

describe("useSession", () => {
	beforeEach(() => {
		mockCreateSessionResponse = null
		mockCreateSessionError = null
		mockDeleteSessionError = null
		_createSessionCallCount = 0
		deleteSessionCallCount = 0
	})

	afterEach(() => {
		vi.clearAllMocks()
	})

	describe("初期状態", () => {
		it("sessionはnull、isCreatingはfalse", () => {
			const { TestWrapper } = createTestWrapper()
			const { result } = renderHook(() => useSession(), { wrapper: TestWrapper })

			expect(result.current.session).toBeNull()
			expect(result.current.isCreating).toBe(false)
			expect(result.current.error).toBeNull()
		})
	})

	describe("createSession", () => {
		it("正常にセッションを作成できる", async () => {
			mockCreateSessionResponse = {
				session_id: "test-session-123",
				problem: "1+1=?",
				current_hint_level: 1,
				tone: "encouraging",
				turns_count: 0,
				created_at: "2026-02-06T10:00:00Z",
			}

			const { TestWrapper } = createTestWrapper()
			const { result } = renderHook(() => useSession(), { wrapper: TestWrapper })

			await act(async () => {
				await result.current.createSession("1+1=?", 1, "robot")
			})

			expect(result.current.session).not.toBeNull()
			expect(result.current.session?.id).toBe("test-session-123")
			expect(result.current.session?.character).toBe("robot")
			expect(result.current.isCreating).toBe(false)
			expect(result.current.error).toBeNull()
		})

		it("character_typeなしでも作成できる", async () => {
			mockCreateSessionResponse = {
				session_id: "test-session-456",
				problem: "2+2=?",
				current_hint_level: 1,
				tone: "encouraging",
				turns_count: 0,
				created_at: "2026-02-06T10:00:00Z",
			}

			const { TestWrapper } = createTestWrapper()
			const { result } = renderHook(() => useSession(), { wrapper: TestWrapper })

			await act(async () => {
				await result.current.createSession("2+2=?", 2)
			})

			expect(result.current.session).not.toBeNull()
			expect(result.current.session?.id).toBe("test-session-456")
			// characterTypeが指定されない場合はデフォルトの"robot"
			expect(result.current.session?.character).toBe("robot")
		})

		it("エラー時にerrorが設定される", async () => {
			mockCreateSessionError = new Error("ネットワークエラー")

			const { TestWrapper } = createTestWrapper()
			const { result } = renderHook(() => useSession(), { wrapper: TestWrapper })

			await act(async () => {
				await result.current.createSession("1+1=?", 1)
			})

			expect(result.current.session).toBeNull()
			expect(result.current.error).toBe("ネットワークエラー")
			expect(result.current.isCreating).toBe(false)
		})
	})

	describe("clearSession", () => {
		it("セッションをクリアできる", async () => {
			mockCreateSessionResponse = {
				session_id: "test-session-123",
				problem: "1+1=?",
				current_hint_level: 1,
				tone: "encouraging",
				turns_count: 0,
				created_at: "2026-02-06T10:00:00Z",
			}

			const { TestWrapper } = createTestWrapper()
			const { result } = renderHook(() => useSession(), { wrapper: TestWrapper })

			// まずセッションを作成
			await act(async () => {
				await result.current.createSession("1+1=?", 1)
			})

			expect(result.current.session).not.toBeNull()

			// セッションをクリア
			await act(async () => {
				await result.current.clearSession()
			})

			expect(result.current.session).toBeNull()
			expect(deleteSessionCallCount).toBe(1)
		})

		it("deleteSession失敗時もローカル状態はクリアする", async () => {
			mockCreateSessionResponse = {
				session_id: "test-session-123",
				problem: "1+1=?",
				current_hint_level: 1,
				tone: "encouraging",
				turns_count: 0,
				created_at: "2026-02-06T10:00:00Z",
			}

			const { TestWrapper } = createTestWrapper()
			const { result } = renderHook(() => useSession(), { wrapper: TestWrapper })

			await act(async () => {
				await result.current.createSession("1+1=?", 1)
			})

			// deleteSessionがエラーを投げるように設定
			mockDeleteSessionError = new Error("削除エラー")

			await act(async () => {
				await result.current.clearSession()
			})

			// エラーでもローカル状態はクリア
			expect(result.current.session).toBeNull()
		})

		it("セッションがない場合は何もしない", async () => {
			const { TestWrapper } = createTestWrapper()
			const { result } = renderHook(() => useSession(), { wrapper: TestWrapper })

			await act(async () => {
				await result.current.clearSession()
			})

			expect(deleteSessionCallCount).toBe(0)
			expect(result.current.session).toBeNull()
		})
	})

	describe("clearError", () => {
		it("エラーをクリアできる", async () => {
			mockCreateSessionError = new Error("テストエラー")

			const { TestWrapper } = createTestWrapper()
			const { result } = renderHook(() => useSession(), { wrapper: TestWrapper })

			await act(async () => {
				await result.current.createSession("1+1=?", 1)
			})

			expect(result.current.error).toBe("テストエラー")

			act(() => {
				result.current.clearError()
			})

			expect(result.current.error).toBeNull()
		})
	})
})
