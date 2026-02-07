/**
 * E2E Integration Test - Global Setup
 *
 * Docker Compose で E2E モードのバックエンドを起動し、
 * ヘルスチェックが通るまで待機する。
 */

import { execSync } from "node:child_process"

const COMPOSE_FILE = "../docker-compose.e2e.yml"
const BACKEND_URL = process.env.E2E_BACKEND_URL ?? "http://localhost:8000"
const MAX_RETRIES = 30
const RETRY_INTERVAL_MS = 2_000

async function waitForBackend(): Promise<void> {
	for (let i = 0; i < MAX_RETRIES; i++) {
		try {
			const response = await fetch(`${BACKEND_URL}/health`)
			if (response.ok) {
				console.log(`Backend is ready (attempt ${i + 1})`)
				return
			}
		} catch {
			// ignore connection errors during startup
		}
		await new Promise((resolve) => setTimeout(resolve, RETRY_INTERVAL_MS))
	}
	throw new Error(
		`Backend did not become ready within ${(MAX_RETRIES * RETRY_INTERVAL_MS) / 1000}s`,
	)
}

export default async function globalSetup(): Promise<void> {
	console.log("Starting backend via Docker Compose...")
	try {
		execSync(`docker compose -f ${COMPOSE_FILE} up -d backend --wait`, {
			cwd: process.cwd().replace("/e2e", "").replace("/frontend", ""),
			stdio: "inherit",
		})
	} catch {
		console.log("Docker Compose start failed, checking if backend is already running...")
	}

	await waitForBackend()
	console.log("Backend is ready for integration tests")
}
