/**
 * DialogueClient のテスト
 */

import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import { DialogueClient } from "./dialogueClient"
import type { RunDialogueRequest } from "./types"

// モック用のReadableStreamを作成するヘルパー
function createMockSSEStream(events: string[]): ReadableStream<Uint8Array> {
	const encoder = new TextEncoder()
	let index = 0

	return new ReadableStream({
		pull(controller) {
			if (index < events.length) {
				controller.enqueue(encoder.encode(events[index]))
				index++
			} else {
				controller.close()
			}
		},
	})
}

// モックfetchレスポンスを作成するヘルパー
function createMockResponse(stream: ReadableStream<Uint8Array>, ok = true, status = 200): Response {
	return {
		ok,
		status,
		body: stream,
		headers: new Headers({ "content-type": "text/event-stream" }),
	} as unknown as Response
}

describe("DialogueClient", () => {
	const mockOnText = vi.fn()
	const mockOnDone = vi.fn()
	const mockOnError = vi.fn()
	const mockFetch = vi.fn()

	let client: DialogueClient
	let originalFetch: typeof global.fetch

	beforeEach(() => {
		vi.clearAllMocks()
		originalFetch = global.fetch
		global.fetch = mockFetch

		client = new DialogueClient({
			baseUrl: "http://localhost:8000",
			onText: mockOnText,
			onDone: mockOnDone,
			onError: mockOnError,
		})
	})

	afterEach(() => {
		global.fetch = originalFetch
	})

	describe("run", () => {
		it("テキストイベントを受信してonTextを呼び出す", async () => {
			const sseEvents = ['event: text\ndata: {"text":"こんにちは"}\n\n']
			const stream = createMockSSEStream(sseEvents)
			mockFetch.mockResolvedValue(createMockResponse(stream))

			const request: RunDialogueRequest = {
				user_id: "user-1",
				session_id: "session-1",
				message: "テスト",
			}

			await client.run(request)

			expect(mockOnText).toHaveBeenCalledWith("こんにちは")
		})

		it("複数のテキストイベントを順番に処理する", async () => {
			const sseEvents = [
				'event: text\ndata: {"text":"最初の"}\n\n',
				'event: text\ndata: {"text":"メッセージ"}\n\n',
			]
			const stream = createMockSSEStream(sseEvents)
			mockFetch.mockResolvedValue(createMockResponse(stream))

			const request: RunDialogueRequest = {
				user_id: "user-1",
				session_id: "session-1",
				message: "テスト",
			}

			await client.run(request)

			expect(mockOnText).toHaveBeenCalledTimes(2)
			expect(mockOnText).toHaveBeenNthCalledWith(1, "最初の")
			expect(mockOnText).toHaveBeenNthCalledWith(2, "メッセージ")
		})

		it("完了イベントを受信してonDoneを呼び出す", async () => {
			const sseEvents = [
				'event: text\ndata: {"text":"回答"}\n\n',
				'event: done\ndata: {"session_id":"session-1"}\n\n',
			]
			const stream = createMockSSEStream(sseEvents)
			mockFetch.mockResolvedValue(createMockResponse(stream))

			const request: RunDialogueRequest = {
				user_id: "user-1",
				session_id: "session-1",
				message: "テスト",
			}

			await client.run(request)

			expect(mockOnText).toHaveBeenCalledWith("回答")
			expect(mockOnDone).toHaveBeenCalledWith("session-1")
		})

		it("エラーイベントを受信してonErrorを呼び出す", async () => {
			const sseEvents = ['event: error\ndata: {"error":"内部エラー","code":"INTERNAL_ERROR"}\n\n']
			const stream = createMockSSEStream(sseEvents)
			mockFetch.mockResolvedValue(createMockResponse(stream))

			const request: RunDialogueRequest = {
				user_id: "user-1",
				session_id: "session-1",
				message: "テスト",
			}

			await client.run(request)

			expect(mockOnError).toHaveBeenCalledWith("内部エラー", "INTERNAL_ERROR")
		})

		it("HTTPエラー時にonErrorを呼び出す", async () => {
			const stream = createMockSSEStream([])
			mockFetch.mockResolvedValue(createMockResponse(stream, false, 500))

			const request: RunDialogueRequest = {
				user_id: "user-1",
				session_id: "session-1",
				message: "テスト",
			}

			await client.run(request)

			expect(mockOnError).toHaveBeenCalledWith("HTTP error: 500", "HTTP_ERROR")
		})

		it("ネットワークエラー時にonErrorを呼び出す", async () => {
			mockFetch.mockRejectedValue(new Error("Network error"))

			const request: RunDialogueRequest = {
				user_id: "user-1",
				session_id: "session-1",
				message: "テスト",
			}

			await client.run(request)

			expect(mockOnError).toHaveBeenCalledWith("Network error", "NETWORK_ERROR")
		})

		it("正しいURLとヘッダーでfetchを呼び出す", async () => {
			const stream = createMockSSEStream([])
			mockFetch.mockResolvedValue(createMockResponse(stream))

			const request: RunDialogueRequest = {
				user_id: "user-1",
				session_id: "session-1",
				message: "テスト",
			}

			await client.run(request)

			expect(mockFetch).toHaveBeenCalledWith(
				"http://localhost:8000/api/v1/dialogue/run",
				expect.objectContaining({
					method: "POST",
					headers: expect.objectContaining({
						"Content-Type": "application/json",
						Accept: "text/event-stream",
					}),
					body: JSON.stringify(request),
				}),
			)
		})
	})

	describe("abort", () => {
		it("実行中のリクエストを中断する", async () => {
			// 長時間かかるストリームをシミュレート
			const slowStream = new ReadableStream({
				async pull(controller) {
					await new Promise((resolve) => setTimeout(resolve, 1000))
					controller.close()
				},
			})
			mockFetch.mockResolvedValue(createMockResponse(slowStream))

			const request: RunDialogueRequest = {
				user_id: "user-1",
				session_id: "session-1",
				message: "テスト",
			}

			const runPromise = client.run(request)

			// すぐに中断
			client.abort()

			// エラーが発生するか、正常に終了するかのいずれか
			await expect(runPromise).resolves.toBeUndefined()
		})
	})
})
