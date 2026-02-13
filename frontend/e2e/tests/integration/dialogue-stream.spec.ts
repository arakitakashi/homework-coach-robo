/**
 * Integration Test: Dialogue SSE Streaming
 *
 * Docker Compose で起動したバックエンド（E2Eモード）に対して、
 * 実際のSSEストリーミング通信を検証する。
 */

import { expect, test } from "@playwright/test"

const BACKEND_URL = process.env.E2E_BACKEND_URL ?? "http://localhost:8000"

test.describe("Dialogue Stream (Integration)", () => {
	let sessionId: string

	test.beforeEach(async ({ request }) => {
		// 各テスト前にセッションを作成
		const response = await request.post(`${BACKEND_URL}/api/v1/dialogue/sessions`, {
			data: {
				problem: "テスト問題",
				child_grade: 1,
				character_type: "robot",
			},
		})
		const body = await response.json()
		sessionId = body.session_id
	})

	test("SSE stream returns text and done events", async ({ request }) => {
		const response = await request.post(`${BACKEND_URL}/api/v1/dialogue/run`, {
			headers: {
				"Content-Type": "application/json",
				Accept: "text/event-stream",
			},
			data: {
				user_id: "test-user",
				session_id: sessionId,
				message: "1たす1はなに？",
			},
		})

		expect(response.ok()).toBeTruthy()
		expect(response.headers()["content-type"]).toContain("text/event-stream")

		const body = await response.text()

		// テキストイベントが含まれる（MockAgentRunnerServiceの定型レスポンス）
		expect(body).toContain("event: text")
		expect(body).toContain('"text"')

		// 完了イベントが含まれる
		expect(body).toContain("event: done")
		expect(body).toContain('"session_id"')
	})

	test("SSE stream contains mock socratic responses", async ({ request }) => {
		const response = await request.post(`${BACKEND_URL}/api/v1/dialogue/run`, {
			headers: {
				"Content-Type": "application/json",
				Accept: "text/event-stream",
			},
			data: {
				user_id: "test-user",
				session_id: sessionId,
				message: "たすけて",
			},
		})

		const body = await response.text()

		// MockAgentRunnerServiceの定型レスポンスが含まれる
		expect(body).toContain("いい質問だね！")
		expect(body).toContain("いっしょに考えよう！")
		expect(body).toContain("この問題は何を聞いていると思う？")
	})

	test("full UI flow with real backend", async ({ page, request }) => {
		// APIルートをプロキシ（バックエンドに転送）
		await page.route("**/api/v1/**", async (route) => {
			const url = route
				.request()
				.url()
				.replace(/http:\/\/localhost:\d+/, BACKEND_URL)
			const response = await request.fetch(url, {
				method: route.request().method(),
				headers: route.request().headers(),
				data: route.request().postData() ?? undefined,
			})
			await route.fulfill({
				status: response.status(),
				headers: Object.fromEntries(
					Object.entries(response.headers()).filter(
						([key]) => key.toLowerCase() !== "transfer-encoding",
					),
				),
				body: Buffer.from(await response.body()),
			})
		})

		// WebSocketはモック（統合テストでもLive APIは不使用）
		await page.routeWebSocket("**/ws/**", (ws) => {
			ws.onMessage(() => {})
		})

		await page.goto("/session?character=robot")

		// ウェルカムメッセージ表示（対話履歴内で確認）
		const dialogueLog = page.getByRole("log", { name: "対話履歴" })
		await expect(dialogueLog.getByText("こんにちは！いっしょにがんばろうね！")).toBeVisible({
			timeout: 10_000,
		})

		// テキスト入力して送信（roleベースで表示要素を取得）
		const input = page.getByRole("textbox", { name: "メッセージ入力" })
		await input.fill("1たす1はなに？")
		await page.getByRole("button", { name: "送信" }).click()

		// MockAgentRunnerServiceの応答が表示される
		await expect(dialogueLog.getByText("いい質問だね！")).toBeVisible({ timeout: 10_000 })
	})
})
