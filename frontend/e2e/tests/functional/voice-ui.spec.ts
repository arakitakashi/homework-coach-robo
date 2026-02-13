import { expect, test } from "../../fixtures/base"
import { SESSION, VOICE } from "../../helpers/selectors"

test.describe("Voice UI", () => {
	test.beforeEach(async ({ mockAPI, page }) => {
		await mockAPI.mockAllSessionAPIs()
		await page.goto("/session?character=robot")
		await expect(page.getByText(SESSION.welcomeMessage).first()).toBeVisible({ timeout: 10_000 })
	})

	test("displays voice interface elements", async ({ page }) => {
		// 録音ボタンが表示される
		const recordButton = page.getByLabel(VOICE.startRecordingLabel).first()
		await expect(recordButton).toBeVisible()

		// 音声レベルインジケーターが表示される
		await expect(page.getByRole("progressbar", { name: "音声レベル" }).first()).toBeVisible()
	})

	test("shows status text based on connection state", async ({ page }) => {
		// WebSocket接続後はステータステキストが表示される
		// 初期状態は「接続中...」または「話しかけてね」（接続状態に依存）
		const statusText = page
			.getByText(VOICE.idle)
			.first()
			.or(page.getByText(VOICE.connecting).first())
		await expect(statusText).toBeVisible()
	})

	test("record button has correct aria attributes", async ({ page }) => {
		const recordButton = page.getByLabel(VOICE.startRecordingLabel).first()
		await expect(recordButton).toHaveAttribute("aria-pressed", "false")
	})
})
