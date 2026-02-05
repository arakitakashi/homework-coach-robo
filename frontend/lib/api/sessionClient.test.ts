/**
 * SessionClient テスト
 */

import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import { SessionClient } from "./sessionClient"
import type { CreateSessionRequest, SessionApiResponse } from "./types"

describe("SessionClient", () => {
	let client: SessionClient
	let mockFetch: ReturnType<typeof vi.fn>
	const originalFetch = global.fetch

	beforeEach(() => {
		mockFetch = vi.fn()
		global.fetch = mockFetch as typeof fetch
		client = new SessionClient({ baseUrl: "http://localhost:8000" })
	})

	afterEach(() => {
		global.fetch = originalFetch
		vi.restoreAllMocks()
	})

	describe("createSession", () => {
		it("正常にセッションを作成できる", async () => {
			const mockResponse: SessionApiResponse = {
				session_id: "test-session-123",
				problem: "1+1=?",
				current_hint_level: 1,
				tone: "encouraging",
				turns_count: 0,
				created_at: "2026-02-06T10:00:00Z",
			}

			mockFetch.mockResolvedValueOnce({
				ok: true,
				json: () => Promise.resolve(mockResponse),
			})

			const request: CreateSessionRequest = {
				problem: "1+1=?",
				child_grade: 1,
				character_type: "robot",
			}

			const result = await client.createSession(request)

			expect(result).toEqual(mockResponse)
			expect(mockFetch).toHaveBeenCalledWith(
				"http://localhost:8000/api/v1/dialogue/sessions",
				expect.objectContaining({
					method: "POST",
					headers: {
						"Content-Type": "application/json",
					},
					body: JSON.stringify(request),
				}),
			)
		})

		it("character_typeなしでも作成できる", async () => {
			const mockResponse: SessionApiResponse = {
				session_id: "test-session-456",
				problem: "2+2=?",
				current_hint_level: 1,
				tone: "encouraging",
				turns_count: 0,
				created_at: "2026-02-06T10:00:00Z",
			}

			mockFetch.mockResolvedValueOnce({
				ok: true,
				json: () => Promise.resolve(mockResponse),
			})

			const request: CreateSessionRequest = {
				problem: "2+2=?",
				child_grade: 2,
			}

			const result = await client.createSession(request)

			expect(result).toEqual(mockResponse)
		})

		it("HTTPエラー時にエラーをスローする", async () => {
			mockFetch.mockResolvedValueOnce({
				ok: false,
				status: 400,
				statusText: "Bad Request",
			})

			const request: CreateSessionRequest = {
				problem: "",
				child_grade: 1,
			}

			await expect(client.createSession(request)).rejects.toThrow(
				"セッション作成に失敗しました: 400 Bad Request",
			)
		})

		it("ネットワークエラー時にエラーをスローする", async () => {
			mockFetch.mockRejectedValueOnce(new Error("Network error"))

			const request: CreateSessionRequest = {
				problem: "1+1=?",
				child_grade: 1,
			}

			await expect(client.createSession(request)).rejects.toThrow("Network error")
		})
	})

	describe("getSession", () => {
		it("正常にセッションを取得できる", async () => {
			const mockResponse: SessionApiResponse = {
				session_id: "test-session-123",
				problem: "1+1=?",
				current_hint_level: 2,
				tone: "curious",
				turns_count: 3,
				created_at: "2026-02-06T10:00:00Z",
			}

			mockFetch.mockResolvedValueOnce({
				ok: true,
				json: () => Promise.resolve(mockResponse),
			})

			const result = await client.getSession("test-session-123")

			expect(result).toEqual(mockResponse)
			expect(mockFetch).toHaveBeenCalledWith(
				"http://localhost:8000/api/v1/dialogue/sessions/test-session-123",
				expect.objectContaining({
					method: "GET",
				}),
			)
		})

		it("404エラー時にエラーをスローする", async () => {
			mockFetch.mockResolvedValueOnce({
				ok: false,
				status: 404,
				statusText: "Not Found",
			})

			await expect(client.getSession("nonexistent")).rejects.toThrow(
				"セッション取得に失敗しました: 404 Not Found",
			)
		})
	})

	describe("deleteSession", () => {
		it("正常にセッションを削除できる", async () => {
			mockFetch.mockResolvedValueOnce({
				ok: true,
			})

			await client.deleteSession("test-session-123")

			expect(mockFetch).toHaveBeenCalledWith(
				"http://localhost:8000/api/v1/dialogue/sessions/test-session-123",
				expect.objectContaining({
					method: "DELETE",
				}),
			)
		})

		it("404エラー時にエラーをスローする", async () => {
			mockFetch.mockResolvedValueOnce({
				ok: false,
				status: 404,
				statusText: "Not Found",
			})

			await expect(client.deleteSession("nonexistent")).rejects.toThrow(
				"セッション削除に失敗しました: 404 Not Found",
			)
		})
	})

	describe("baseUrl設定", () => {
		it("デフォルトのbaseUrlを使用する", () => {
			const defaultClient = new SessionClient()
			expect(defaultClient).toBeDefined()
		})
	})
})
