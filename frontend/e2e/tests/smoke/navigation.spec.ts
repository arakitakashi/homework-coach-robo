import { expect, test } from "../../fixtures/base"
import { HOME, INPUT_MODE_SELECTOR, SESSION } from "../../helpers/selectors"

test.describe("Navigation", () => {
	test("navigates from home to session page", async ({ page, mockAPI }) => {
		// セッションページのAPIをモック（セッション作成 + WebSocket）
		await mockAPI.mockAllSessionAPIs()

		await page.goto("/")

		// 「はじめる」ボタンをクリック
		await page.getByRole("button", { name: HOME.startButton }).click()

		// セッションページに遷移
		await page.waitForURL("**/session?character=robot")

		// InputModeSelectorで音声モードを選択
		await expect(page.getByText(INPUT_MODE_SELECTOR.title)).toBeVisible({ timeout: 10_000 })
		await page.getByRole("button", { name: INPUT_MODE_SELECTOR.voiceButton }).click()

		// セッションUIが表示される（ローディング→メインUI、対話履歴内で確認）
		const dialogueLog = page.getByRole("log", { name: "対話履歴" })
		await expect(dialogueLog.getByText(SESSION.welcomeMessage)).toBeVisible({ timeout: 10_000 })
	})

	test("session page shows loading then content", async ({ page, mockAPI }) => {
		await mockAPI.mockAllSessionAPIs()

		await page.goto("/session?character=robot")

		// InputModeSelectorで音声モードを選択
		await expect(page.getByText(INPUT_MODE_SELECTOR.title)).toBeVisible({ timeout: 10_000 })
		await page.getByRole("button", { name: INPUT_MODE_SELECTOR.voiceButton }).click()

		// メインUIが表示される（対話履歴内で確認）
		const dialogueLog = page.getByRole("log", { name: "対話履歴" })
		await expect(dialogueLog.getByText(SESSION.welcomeMessage)).toBeVisible({ timeout: 10_000 })

		// 終了ボタンが表示される
		await expect(page.getByRole("button", { name: SESSION.endButton }).first()).toBeVisible()
	})

	test("end button navigates back to home", async ({ page, mockAPI }) => {
		await mockAPI.mockAllSessionAPIs()

		await page.goto("/session?character=robot")

		// InputModeSelectorで音声モードを選択
		await expect(page.getByText(INPUT_MODE_SELECTOR.title)).toBeVisible({ timeout: 10_000 })
		await page.getByRole("button", { name: INPUT_MODE_SELECTOR.voiceButton }).click()

		const dialogueLog = page.getByRole("log", { name: "対話履歴" })
		await expect(dialogueLog.getByText(SESSION.welcomeMessage)).toBeVisible({ timeout: 10_000 })

		// 「おわる」ボタンをクリック
		await page.getByRole("button", { name: SESSION.endButton }).first().click()

		// ホームページに遷移
		await page.waitForURL("**/")
		await expect(page.getByRole("heading", { name: HOME.title })).toBeVisible()
	})
})
