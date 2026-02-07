/**
 * Integration Test: Session API
 *
 * Docker Compose で起動したバックエンド（E2Eモード）に対して、
 * 実際のHTTP通信でセッションCRUD操作を検証する。
 */

import { expect, test } from "@playwright/test"

const BACKEND_URL = process.env.E2E_BACKEND_URL ?? "http://localhost:8000"

test.describe("Session API (Integration)", () => {
	test("backend health check responds", async ({ request }) => {
		const response = await request.get(`${BACKEND_URL}/health`)
		expect(response.ok()).toBeTruthy()
		const body = await response.json()
		expect(body.status).toBe("healthy")
	})

	test("create session returns session_id", async ({ request }) => {
		const response = await request.post(`${BACKEND_URL}/api/v1/dialogue/sessions`, {
			data: {
				problem: "1+1はなに？",
				child_grade: 1,
				character_type: "robot",
			},
		})
		expect(response.status()).toBe(201)

		const body = await response.json()
		expect(body.session_id).toBeTruthy()
		expect(body.problem).toBe("1+1はなに？")
		expect(body.created_at).toBeTruthy()
	})

	test("get session returns session info", async ({ request }) => {
		// セッション作成
		const createResponse = await request.post(`${BACKEND_URL}/api/v1/dialogue/sessions`, {
			data: {
				problem: "2+3はなに？",
				child_grade: 1,
			},
		})
		const { session_id } = await createResponse.json()

		// セッション取得
		const getResponse = await request.get(`${BACKEND_URL}/api/v1/dialogue/sessions/${session_id}`)
		expect(getResponse.ok()).toBeTruthy()

		const body = await getResponse.json()
		expect(body.session_id).toBe(session_id)
		expect(body.problem).toBe("2+3はなに？")
	})

	test("delete session returns 204", async ({ request }) => {
		// セッション作成
		const createResponse = await request.post(`${BACKEND_URL}/api/v1/dialogue/sessions`, {
			data: {
				problem: "テスト問題",
				child_grade: 2,
			},
		})
		const { session_id } = await createResponse.json()

		// セッション削除
		const deleteResponse = await request.delete(
			`${BACKEND_URL}/api/v1/dialogue/sessions/${session_id}`,
		)
		expect(deleteResponse.status()).toBe(204)

		// 削除後は404
		const getResponse = await request.get(`${BACKEND_URL}/api/v1/dialogue/sessions/${session_id}`)
		expect(getResponse.status()).toBe(404)
	})

	test("get nonexistent session returns 404", async ({ request }) => {
		const response = await request.get(`${BACKEND_URL}/api/v1/dialogue/sessions/nonexistent-id`)
		expect(response.status()).toBe(404)
	})
})
