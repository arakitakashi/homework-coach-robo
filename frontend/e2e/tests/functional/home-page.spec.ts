import { expect, test } from "../../fixtures/base"
import { HOME } from "../../helpers/selectors"

test.describe("Home Page", () => {
	test.beforeEach(async ({ page }) => {
		await page.goto("/")
	})

	test("displays all UI elements", async ({ page }) => {
		// タイトル
		await expect(page.getByRole("heading", { name: HOME.title })).toBeVisible()

		// サブタイトル
		await expect(page.getByText(HOME.subtitle)).toBeVisible()

		// キャラクター選択プロンプト
		await expect(page.getByText(HOME.characterPrompt)).toBeVisible()

		// スタートボタン
		await expect(page.getByRole("button", { name: HOME.startButton })).toBeVisible()
	})

	test("displays all four character options", async ({ page }) => {
		for (const label of Object.values(HOME.characters)) {
			await expect(page.getByRole("button", { name: label })).toBeVisible()
		}
	})

	test("robot is selected by default", async ({ page }) => {
		const robotButton = page.getByRole("button", { name: HOME.characters.robot })
		await expect(robotButton).toHaveAttribute("aria-pressed", "true")

		// 他のキャラクターは未選択
		const wizardButton = page.getByRole("button", { name: HOME.characters.wizard })
		await expect(wizardButton).toHaveAttribute("aria-pressed", "false")
	})

	test("clicking a character selects it", async ({ page }) => {
		const wizardButton = page.getByRole("button", { name: HOME.characters.wizard })
		await wizardButton.click()
		await expect(wizardButton).toHaveAttribute("aria-pressed", "true")

		// 元のキャラクターは非選択に
		const robotButton = page.getByRole("button", { name: HOME.characters.robot })
		await expect(robotButton).toHaveAttribute("aria-pressed", "false")
	})

	test("start button navigates with selected character", async ({ page, mockAPI }) => {
		await mockAPI.mockAllSessionAPIs()

		// 宇宙飛行士を選択
		await page.getByRole("button", { name: HOME.characters.astronaut }).click()

		// はじめるボタンをクリック
		await page.getByRole("button", { name: HOME.startButton }).click()

		// URLにcharacter=astronautが含まれる
		await page.waitForURL("**/session?character=astronaut")
	})
})
