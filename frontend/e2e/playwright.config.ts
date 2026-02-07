import { defineConfig, devices } from "@playwright/test"

const baseURL = process.env.E2E_BASE_URL ?? "http://localhost:3000"
const backendURL = process.env.E2E_BACKEND_URL ?? "http://localhost:8000"

export default defineConfig({
	testDir: "./tests",
	fullyParallel: true,
	forbidOnly: !!process.env.CI,
	retries: process.env.CI ? 2 : 0,
	workers: process.env.CI ? 1 : undefined,
	reporter: process.env.CI ? "github" : "html",
	timeout: 30_000,
	expect: {
		timeout: 5_000,
	},
	use: {
		baseURL,
		trace: "on-first-retry",
		screenshot: "only-on-failure",
	},
	projects: [
		{
			name: "smoke",
			testDir: "./tests/smoke",
			use: { ...devices["Desktop Chrome"] },
		},
		{
			name: "functional",
			testDir: "./tests/functional",
			use: { ...devices["Desktop Chrome"] },
		},
		{
			name: "integration",
			testDir: "./tests/integration",
			use: { ...devices["Desktop Chrome"] },
			metadata: { backendURL },
			globalSetup: "./global-setup.ts",
			globalTeardown: "./global-teardown.ts",
		},
	],
	webServer: {
		command: "bun run dev",
		url: baseURL,
		reuseExistingServer: !process.env.CI,
		timeout: 120_000,
	},
})
