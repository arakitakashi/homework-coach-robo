/**
 * VisionClient テスト
 *
 * 画像認識APIクライアントのユニットテスト。
 * fetch をモックしてリクエスト/レスポンスの検証を行う。
 */

import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import { VisionClient } from "./visionClient"

// fetchのグローバルモック
const mockFetch = vi.fn()

describe("VisionClient", () => {
	let client: VisionClient

	beforeEach(() => {
		vi.stubGlobal("fetch", mockFetch)
		client = new VisionClient({ baseUrl: "http://localhost:8000" })
	})

	afterEach(() => {
		vi.restoreAllMocks()
	})

	describe("constructor", () => {
		it("カスタムbaseUrlを設定できる", () => {
			const customClient = new VisionClient({ baseUrl: "http://custom:9000" })
			expect(customClient).toBeDefined()
		})

		it("オプションなしでデフォルトURLを使用する", () => {
			const defaultClient = new VisionClient()
			expect(defaultClient).toBeDefined()
		})
	})

	describe("recognizeImage", () => {
		const mockRequest = {
			image: "base64encodeddata",
			recognition_type: "homework_problem" as const,
		}

		const mockResponse = {
			success: true,
			problems: [
				{
					text: "1 + 2 = ?",
					type: "arithmetic",
					difficulty: 1,
					expression: "1 + 2",
				},
			],
			confidence: 0.95,
			needs_confirmation: false,
		}

		it("正しいエンドポイントにPOSTリクエストを送信する", async () => {
			mockFetch.mockResolvedValue({
				ok: true,
				json: () => Promise.resolve(mockResponse),
			})

			await client.recognizeImage(mockRequest)

			expect(mockFetch).toHaveBeenCalledWith("http://localhost:8000/api/v1/vision/recognize", {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},
				body: JSON.stringify(mockRequest),
			})
		})

		it("認識結果を返す", async () => {
			mockFetch.mockResolvedValue({
				ok: true,
				json: () => Promise.resolve(mockResponse),
			})

			const result = await client.recognizeImage(mockRequest)

			expect(result).toEqual(mockResponse)
		})

		it("HTTPエラー時にエラーをスローする", async () => {
			mockFetch.mockResolvedValue({
				ok: false,
				status: 500,
				statusText: "Internal Server Error",
			})

			await expect(client.recognizeImage(mockRequest)).rejects.toThrow(
				"がぞうのよみとりにしっぱいしました: 500 Internal Server Error",
			)
		})

		it("ネットワークエラー時にエラーをスローする", async () => {
			mockFetch.mockRejectedValue(new Error("Network error"))

			await expect(client.recognizeImage(mockRequest)).rejects.toThrow("Network error")
		})
	})
})
