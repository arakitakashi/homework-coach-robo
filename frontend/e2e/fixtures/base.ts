/**
 * E2Eテスト共通フィクスチャ
 *
 * MockAPIクラスでpage.route()をラップし、
 * バックエンドAPIのモックを簡潔に設定できるようにする。
 */

import { test as base, type Page } from "@playwright/test"
import { API } from "../helpers/selectors"
import { buildSSEBody, mockSessionResponse } from "../helpers/sse-mock"

/** APIモック設定オプション */
interface MockSessionOptions {
	sessionId?: string
	status?: number
}

interface MockDialogueOptions {
	textChunks?: string[]
	sessionId?: string
}

/**
 * MockAPIクラス
 *
 * page.route() をラップし、REST/SSE APIのモックを設定する。
 * page.goto() の前に呼び出すこと（SessionContentのuseEffectがマウント時にAPI呼び出しするため）。
 */
export class MockAPI {
	constructor(private readonly page: Page) {}

	/** セッション作成APIをモック */
	async mockSessionCreate(options: MockSessionOptions = {}): Promise<void> {
		const { sessionId = "test-session-123", status = 200 } = options
		await this.page.route(API.sessionsCreate, async (route) => {
			if (route.request().method() === "POST") {
				await route.fulfill({
					status,
					contentType: "application/json",
					body: JSON.stringify(mockSessionResponse(sessionId)),
				})
			} else {
				await route.continue()
			}
		})
	}

	/** セッション削除APIをモック */
	async mockSessionDelete(status = 200): Promise<void> {
		await this.page.route(API.sessionById, async (route) => {
			if (route.request().method() === "DELETE") {
				await route.fulfill({ status })
			} else {
				await route.continue()
			}
		})
	}

	/** 対話SSEストリーミングをモック */
	async mockDialogueRun(options: MockDialogueOptions = {}): Promise<void> {
		const {
			textChunks = ["いい質問だね！", "いっしょに考えよう！"],
			sessionId = "test-session-123",
		} = options
		await this.page.route(API.dialogueRun, async (route) => {
			await route.fulfill({
				status: 200,
				contentType: "text/event-stream",
				body: buildSSEBody(textChunks, sessionId),
			})
		})
	}

	/** WebSocket接続をモック（接続のみ） */
	async mockWebSocket(): Promise<void> {
		await this.page.routeWebSocket(API.voiceStream, (ws) => {
			// WebSocket接続を受け入れるだけ（メッセージ処理は行わない）
			ws.onMessage(() => {
				// クライアントからのメッセージを無視
			})
		})
	}

	/** セッション作成エラーをモック */
	async mockSessionCreateError(status = 500, message = "Internal Server Error"): Promise<void> {
		await this.page.route(API.sessionsCreate, async (route) => {
			if (route.request().method() === "POST") {
				await route.fulfill({
					status,
					contentType: "application/json",
					body: JSON.stringify({ detail: message }),
				})
			} else {
				await route.continue()
			}
		})
	}

	/**
	 * セッションページの全APIをモック（基本セット）
	 * セッション作成 + 対話 + WebSocket + セッション削除
	 */
	async mockAllSessionAPIs(options: MockSessionOptions & MockDialogueOptions = {}): Promise<void> {
		await this.mockSessionCreate(options)
		await this.mockDialogueRun(options)
		await this.mockWebSocket()
		await this.mockSessionDelete()
	}
}

/** カスタムフィクスチャ付きtest */
export const test = base.extend<{ mockAPI: MockAPI }>({
	mockAPI: async ({ page }, use) => {
		const api = new MockAPI(page)
		await use(api)
	},
})

export { expect } from "@playwright/test"
