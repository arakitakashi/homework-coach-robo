/**
 * useDialogue フックのテスト
 */

import { act, renderHook } from "@testing-library/react"
import { createStore, Provider } from "jotai"
import { type ReactNode, useMemo } from "react"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import { characterStateAtom, dialogueTurnsAtom } from "@/store/atoms/dialogue"
import { sessionAtom } from "@/store/atoms/session"
import type { Session } from "@/types"
import { useDialogue } from "./useDialogue"

// DialogueClientをモック
vi.mock("@/lib/api", () => {
	// ファクトリー内でクラスを定義（ホイストされるため外部変数を参照できない）
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
			// テキストイベントをシミュレート
			this.options.onText("テスト回答")
			// 完了イベントをシミュレート
			this.options.onDone("session-1")
		}

		abort(): void {
			// 何もしない
		}
	}

	return {
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

describe("useDialogue", () => {
	const mockSession: Session = {
		id: "session-1",
		userId: "user-1",
		character: "robot",
		status: "active",
		startTime: new Date(),
	}

	beforeEach(() => {
		vi.clearAllMocks()
	})

	afterEach(() => {
		vi.restoreAllMocks()
	})

	it("初期状態ではisLoadingがfalse、errorがnull", () => {
		const { TestWrapper } = createTestWrapper()

		const { result } = renderHook(() => useDialogue(), { wrapper: TestWrapper })

		expect(result.current.isLoading).toBe(false)
		expect(result.current.error).toBeNull()
	})

	it("sendMessage呼び出し前はisLoadingがfalse", () => {
		const { store, TestWrapper } = createTestWrapper()

		// セッションを設定
		store.set(sessionAtom, mockSession)

		const { result } = renderHook(() => useDialogue(), { wrapper: TestWrapper })

		// sendMessageを呼び出す前はfalse
		expect(result.current.isLoading).toBe(false)
	})

	it("sendMessage完了後にisLoadingがfalseに戻る", async () => {
		const { store, TestWrapper } = createTestWrapper()

		// セッションを設定
		store.set(sessionAtom, mockSession)

		const { result } = renderHook(() => useDialogue(), { wrapper: TestWrapper })

		await act(async () => {
			await result.current.sendMessage("テスト")
		})

		expect(result.current.isLoading).toBe(false)
	})

	it("sendMessageで対話履歴にユーザーメッセージが追加される", async () => {
		const { store, TestWrapper } = createTestWrapper()

		// セッションを設定
		store.set(sessionAtom, mockSession)

		const { result } = renderHook(() => useDialogue(), { wrapper: TestWrapper })

		await act(async () => {
			await result.current.sendMessage("ユーザーの質問")
		})

		const dialogueTurns = store.get(dialogueTurnsAtom)
		const childTurn = dialogueTurns.find((turn) => turn.speaker === "child")

		expect(childTurn).toBeDefined()
		expect(childTurn?.text).toBe("ユーザーの質問")
	})

	it("sendMessageでロボットの回答が対話履歴に追加される", async () => {
		const { store, TestWrapper } = createTestWrapper()

		// セッションを設定
		store.set(sessionAtom, mockSession)

		const { result } = renderHook(() => useDialogue(), { wrapper: TestWrapper })

		await act(async () => {
			await result.current.sendMessage("テスト")
		})

		const dialogueTurns = store.get(dialogueTurnsAtom)
		const robotTurn = dialogueTurns.find((turn) => turn.speaker === "robot")

		expect(robotTurn).toBeDefined()
		expect(robotTurn?.text).toBe("テスト回答")
	})

	it("sendMessage前のキャラクター状態がidle", () => {
		const { store, TestWrapper } = createTestWrapper()

		// セッションを設定
		store.set(sessionAtom, mockSession)

		// フックを初期化（状態の初期化を確認するため）
		renderHook(() => useDialogue(), { wrapper: TestWrapper })

		// 初期状態はidle
		expect(store.get(characterStateAtom)).toBe("idle")
	})

	it("sendMessage完了後にキャラクター状態がidleに戻る", async () => {
		const { store, TestWrapper } = createTestWrapper()

		// セッションを設定
		store.set(sessionAtom, mockSession)

		const { result } = renderHook(() => useDialogue(), { wrapper: TestWrapper })

		await act(async () => {
			await result.current.sendMessage("テスト")
		})

		expect(store.get(characterStateAtom)).toBe("idle")
	})

	it("セッションがない場合はエラーを設定", async () => {
		const { TestWrapper } = createTestWrapper()

		const { result } = renderHook(() => useDialogue(), { wrapper: TestWrapper })

		await act(async () => {
			await result.current.sendMessage("テスト")
		})

		expect(result.current.error).toBe("セッションがありません")
	})

	it("clearErrorでエラーをクリアできる", async () => {
		const { TestWrapper } = createTestWrapper()

		const { result } = renderHook(() => useDialogue(), { wrapper: TestWrapper })

		// エラーを発生させる
		await act(async () => {
			await result.current.sendMessage("テスト")
		})

		expect(result.current.error).not.toBeNull()

		// エラーをクリア
		act(() => {
			result.current.clearError()
		})

		expect(result.current.error).toBeNull()
	})
})
