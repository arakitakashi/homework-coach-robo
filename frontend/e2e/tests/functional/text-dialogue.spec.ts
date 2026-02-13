import { expect, test } from "../../fixtures/base"
import { SESSION } from "../../helpers/selectors"

test.describe("Text Dialogue", () => {
	test.beforeEach(async ({ mockAPI, page }) => {
		await mockAPI.mockAllSessionAPIs()
		await page.goto("/session?character=robot")
		// セッション作成完了を待つ（対話履歴内で確認）
		const dialogueLog = page.getByRole("log", { name: "対話履歴" })
		await expect(dialogueLog.getByText(SESSION.welcomeMessage)).toBeVisible({ timeout: 10_000 })
	})

	test("displays welcome message on session start", async ({ page }) => {
		// ウェルカムメッセージが対話履歴に表示される
		const dialogueLog = page.getByRole("log", { name: SESSION.dialogueLogAriaLabel }).first()
		await expect(dialogueLog).toBeVisible()
		await expect(dialogueLog.getByText(SESSION.welcomeMessage).first()).toBeVisible()
	})

	test("shows text input with placeholder", async ({ page }) => {
		const input = page.getByLabel(SESSION.inputAriaLabel).first()
		await expect(input).toBeVisible()
		await expect(input).toHaveAttribute("placeholder", SESSION.textInputPlaceholder)
	})

	test("send button is disabled when input is empty", async ({ page }) => {
		const sendButton = page.getByLabel(SESSION.sendAriaLabel).first()
		await expect(sendButton).toBeDisabled()
	})

	test("send button is enabled when input has text", async ({ page }) => {
		const input = page.getByLabel(SESSION.inputAriaLabel).first()
		await input.fill("1+1はなに？")

		const sendButton = page.getByLabel(SESSION.sendAriaLabel).first()
		await expect(sendButton).toBeEnabled()
	})

	test("sends message and displays robot response", async ({ page, mockAPI }) => {
		const userMessage = "1たす1はなに？"
		const robotChunks = ["いい質問だね！", "いっしょに考えよう！"]

		// 対話APIをモック（テキストチャンク付き）
		await mockAPI.mockDialogueRun({ textChunks: robotChunks })

		const input = page.getByLabel(SESSION.inputAriaLabel).first()
		await input.fill(userMessage)

		const sendButton = page.getByLabel(SESSION.sendAriaLabel).first()
		await sendButton.click()

		// ユーザーメッセージが対話履歴に表示される
		const dialogueLog = page.getByRole("log", { name: SESSION.dialogueLogAriaLabel }).first()
		await expect(dialogueLog.getByText(userMessage)).toBeVisible({ timeout: 5_000 })

		// ロボットの応答が表示される（チャンクが結合される）
		const combinedResponse = robotChunks.join("")
		await expect(dialogueLog.getByText(combinedResponse)).toBeVisible({ timeout: 5_000 })

		// 入力フィールドがクリアされる
		await expect(input).toHaveValue("")
	})

	test("sends message with Enter key", async ({ page, mockAPI }) => {
		await mockAPI.mockDialogueRun({ textChunks: ["わかった！"] })

		const input = page.getByLabel(SESSION.inputAriaLabel).first()
		await input.fill("たすけて")
		await input.press("Enter")

		// メッセージが送信される
		const dialogueLog = page.getByRole("log", { name: SESSION.dialogueLogAriaLabel }).first()
		await expect(dialogueLog.getByText("たすけて")).toBeVisible({ timeout: 5_000 })
	})
})
