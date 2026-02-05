/**
 * セッションAPIクライアント
 *
 * バックエンドのセッションAPIを呼び出すクライアント。
 */

import type { CreateSessionRequest, SessionApiResponse } from "./types"

/** SessionClientのオプション */
export interface SessionClientOptions {
	/** バックエンドのベースURL */
	baseUrl?: string
}

/**
 * セッションAPIクライアント
 *
 * @example
 * ```typescript
 * const client = new SessionClient({ baseUrl: "http://localhost:8000" })
 * const session = await client.createSession({
 *   problem: "1+1=?",
 *   child_grade: 1,
 *   character_type: "robot"
 * })
 * ```
 */
export class SessionClient {
	private readonly baseUrl: string

	constructor(options?: SessionClientOptions) {
		this.baseUrl = options?.baseUrl ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"
	}

	/**
	 * セッションを作成する
	 *
	 * @param request - セッション作成リクエスト
	 * @returns セッション情報
	 * @throws {Error} HTTPエラーまたはネットワークエラー時
	 */
	async createSession(request: CreateSessionRequest): Promise<SessionApiResponse> {
		const response = await fetch(`${this.baseUrl}/api/v1/dialogue/sessions`, {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
			},
			body: JSON.stringify(request),
		})

		if (!response.ok) {
			throw new Error(`セッション作成に失敗しました: ${response.status} ${response.statusText}`)
		}

		return response.json()
	}

	/**
	 * セッションを取得する
	 *
	 * @param sessionId - セッションID
	 * @returns セッション情報
	 * @throws {Error} HTTPエラーまたはネットワークエラー時
	 */
	async getSession(sessionId: string): Promise<SessionApiResponse> {
		const response = await fetch(`${this.baseUrl}/api/v1/dialogue/sessions/${sessionId}`, {
			method: "GET",
		})

		if (!response.ok) {
			throw new Error(`セッション取得に失敗しました: ${response.status} ${response.statusText}`)
		}

		return response.json()
	}

	/**
	 * セッションを削除する
	 *
	 * @param sessionId - セッションID
	 * @throws {Error} HTTPエラーまたはネットワークエラー時
	 */
	async deleteSession(sessionId: string): Promise<void> {
		const response = await fetch(`${this.baseUrl}/api/v1/dialogue/sessions/${sessionId}`, {
			method: "DELETE",
		})

		if (!response.ok) {
			throw new Error(`セッション削除に失敗しました: ${response.status} ${response.statusText}`)
		}
	}
}
