/**
 * E2E Integration Test - Global Teardown
 *
 * Docker Compose で起動したバックエンドを停止する。
 */

import { execSync } from "node:child_process"

const COMPOSE_FILE = "../docker-compose.e2e.yml"

export default async function globalTeardown(): Promise<void> {
	console.log("Stopping backend via Docker Compose...")
	try {
		execSync(`docker compose -f ${COMPOSE_FILE} down`, {
			cwd: process.cwd().replace("/e2e", "").replace("/frontend", ""),
			stdio: "inherit",
		})
	} catch {
		console.log("Docker Compose teardown failed (may already be stopped)")
	}
}
