import { expect, test } from "../../fixtures/base"
import { HOME, SESSION } from "../../helpers/selectors"

test.describe("Session Cleanup", () => {
	test.beforeEach(async ({ mockAPI, page }) => {
		await mockAPI.mockAllSessionAPIs()
		await page.goto("/session?character=robot")
		await expect(page.getByText(SESSION.welcomeMessage)).toBeVisible({ timeout: 10_000 })
	})

	test("end button returns to home page", async ({ page }) => {
		await page.getByRole("button", { name: SESSION.endButton }).click()

		await page.waitForURL("**/")
		await expect(page.getByRole("heading", { name: HOME.title })).toBeVisible()
	})

	test("end button calls session delete API", async ({ page }) => {
		let deleteCalled = false

		// 削除APIのモニタリング（既存モックの上に追加）
		page.on("request", (request) => {
			if (request.method() === "DELETE" && request.url().includes("/api/v1/dialogue/sessions/")) {
				deleteCalled = true
			}
		})

		await page.getByRole("button", { name: SESSION.endButton }).click()
		await page.waitForURL("**/")

		expect(deleteCalled).toBe(true)
	})

	test("can start new session after ending previous one", async ({ page, mockAPI }) => {
		// セッション終了
		await page.getByRole("button", { name: SESSION.endButton }).click()
		await page.waitForURL("**/")

		// ホームページに戻り、新しいセッションを開始
		await expect(page.getByRole("heading", { name: HOME.title })).toBeVisible()

		// 別のキャラクターを選択して再度開始
		await page.getByRole("button", { name: HOME.characters.wizard }).click()

		// 新しいセッション用のモックを再設定
		await mockAPI.mockAllSessionAPIs({ sessionId: "test-session-456" })

		await page.getByRole("button", { name: HOME.startButton }).click()
		await page.waitForURL("**/session?character=wizard")

		// 新しいセッションのウェルカムメッセージが表示される
		await expect(page.getByText(SESSION.welcomeMessage)).toBeVisible({ timeout: 10_000 })
	})
})
