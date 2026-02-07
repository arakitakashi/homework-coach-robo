import { expect, test } from "../../fixtures/base"
import { HOME, SESSION } from "../../helpers/selectors"

test.describe("Session Creation", () => {
	test("shows loading spinner during session creation", async ({ page, mockAPI }) => {
		// レスポンスを遅延させてローディング状態を確認
		const deferred: { resolve: () => void } = { resolve: () => {} }
		const sessionPromise = new Promise<void>((resolve) => {
			deferred.resolve = resolve
		})

		await page.route("**/api/v1/dialogue/sessions", async (route) => {
			if (route.request().method() === "POST") {
				await sessionPromise
				await route.fulfill({
					status: 200,
					contentType: "application/json",
					body: JSON.stringify({
						session_id: "test-session-123",
						created_at: new Date().toISOString(),
					}),
				})
			} else {
				await route.continue()
			}
		})
		await mockAPI.mockWebSocket()

		await page.goto("/session?character=robot")

		// ローディング表示を確認
		await expect(page.getByText(SESSION.loading)).toBeVisible()

		// セッション作成を完了
		deferred.resolve()

		// メインUIが表示される
		await expect(page.getByText(SESSION.welcomeMessage)).toBeVisible({ timeout: 10_000 })
	})

	test("shows error message on session creation failure", async ({ page, mockAPI }) => {
		await mockAPI.mockSessionCreateError(500)

		await page.goto("/session?character=robot")

		// エラー画面が表示される
		await expect(page.getByText(SESSION.errorTitle)).toBeVisible({ timeout: 10_000 })

		// リトライボタンと戻るボタンが表示される
		await expect(page.getByRole("button", { name: SESSION.retryButton })).toBeVisible()
		await expect(page.getByRole("button", { name: SESSION.backButton })).toBeVisible()
	})

	test("retry button attempts session creation again", async ({ page, mockAPI }) => {
		let callCount = 0

		await page.route("**/api/v1/dialogue/sessions", async (route) => {
			if (route.request().method() === "POST") {
				callCount++
				if (callCount === 1) {
					// 1回目: エラー
					await route.fulfill({
						status: 500,
						contentType: "application/json",
						body: JSON.stringify({ detail: "Internal Server Error" }),
					})
				} else {
					// 2回目: 成功
					await route.fulfill({
						status: 200,
						contentType: "application/json",
						body: JSON.stringify({
							session_id: "test-session-123",
							created_at: new Date().toISOString(),
						}),
					})
				}
			} else {
				await route.continue()
			}
		})
		await mockAPI.mockWebSocket()

		await page.goto("/session?character=robot")

		// エラー画面
		await expect(page.getByText(SESSION.errorTitle)).toBeVisible({ timeout: 10_000 })

		// リトライ
		await page.getByRole("button", { name: SESSION.retryButton }).click()

		// 成功してメインUIが表示される
		await expect(page.getByText(SESSION.welcomeMessage)).toBeVisible({ timeout: 10_000 })
	})

	test("back button navigates to home page", async ({ page, mockAPI }) => {
		await mockAPI.mockSessionCreateError(500)

		await page.goto("/session?character=robot")

		await expect(page.getByText(SESSION.errorTitle)).toBeVisible({ timeout: 10_000 })

		// 「もどる」ボタンをクリック
		await page.getByRole("button", { name: SESSION.backButton }).click()

		// ホームページに遷移
		await page.waitForURL("**/")
		await expect(page.getByRole("heading", { name: HOME.title })).toBeVisible()
	})
})
