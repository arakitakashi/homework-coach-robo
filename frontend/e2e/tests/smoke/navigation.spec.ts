import { expect, test } from "../../fixtures/base"
import { HOME, SESSION } from "../../helpers/selectors"

test.describe("Navigation", () => {
	test("navigates from home to session page", async ({ page, mockAPI }) => {
		// セッションページのAPIをモック（セッション作成 + WebSocket）
		await mockAPI.mockAllSessionAPIs()

		await page.goto("/")

		// 「はじめる」ボタンをクリック
		await page.getByRole("button", { name: HOME.startButton }).click()

		// セッションページに遷移
		await page.waitForURL("**/session?character=robot")

		// セッションUIが表示される（ローディング→メインUI）
		await expect(page.getByText(SESSION.welcomeMessage).first()).toBeVisible({ timeout: 10_000 })
	})

	test("session page shows loading then content", async ({ page, mockAPI }) => {
		await mockAPI.mockAllSessionAPIs()

		await page.goto("/session?character=robot")

		// メインUIが表示される
		await expect(page.getByText(SESSION.welcomeMessage).first()).toBeVisible({ timeout: 10_000 })

		// 終了ボタンが表示される
		await expect(page.getByRole("button", { name: SESSION.endButton }).first()).toBeVisible()
	})

	test("end button navigates back to home", async ({ page, mockAPI }) => {
		await mockAPI.mockAllSessionAPIs()

		await page.goto("/session?character=robot")
		await expect(page.getByText(SESSION.welcomeMessage).first()).toBeVisible({ timeout: 10_000 })

		// 「おわる」ボタンをクリック
		await page.getByRole("button", { name: SESSION.endButton }).first().click()

		// ホームページに遷移
		await page.waitForURL("**/")
		await expect(page.getByRole("heading", { name: HOME.title })).toBeVisible()
	})
})
