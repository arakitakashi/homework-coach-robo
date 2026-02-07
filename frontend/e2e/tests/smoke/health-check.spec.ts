import { expect, test } from "@playwright/test"

test.describe("Health Check", () => {
	test("home page loads successfully", async ({ page }) => {
		const response = await page.goto("/")
		expect(response?.status()).toBe(200)
	})

	test("home page displays app title", async ({ page }) => {
		await page.goto("/")
		await expect(page.getByRole("heading", { name: "宿題コーチロボット" })).toBeVisible()
	})
})
