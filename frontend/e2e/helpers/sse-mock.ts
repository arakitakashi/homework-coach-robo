/**
 * SSEレスポンスボディ生成ヘルパー
 *
 * バックエンドのSSEストリーミングをモックする際に使用する。
 * フロントエンドはfetch + ReadableStreamでSSEを処理するため、
 * Content-Type: text/event-stream のレスポンスを生成する。
 */

/** SSEテキストイベントを生成 */
export function sseTextEvent(text: string): string {
	return `event: text\ndata: ${JSON.stringify({ text })}\n\n`
}

/** SSE完了イベントを生成 */
export function sseDoneEvent(sessionId: string): string {
	return `event: done\ndata: ${JSON.stringify({ session_id: sessionId })}\n\n`
}

/** SSEエラーイベントを生成 */
export function sseErrorEvent(error: string, code: string): string {
	return `event: error\ndata: ${JSON.stringify({ error, code })}\n\n`
}

/** 複数のテキストチャンクと完了イベントからSSEレスポンスボディを生成 */
export function buildSSEBody(textChunks: string[], sessionId: string): string {
	const events = textChunks.map((chunk) => sseTextEvent(chunk))
	events.push(sseDoneEvent(sessionId))
	return events.join("")
}

/** セッション作成APIのモックレスポンスを生成 */
export function mockSessionResponse(sessionId = "test-session-123"): Record<string, unknown> {
	return {
		session_id: sessionId,
		created_at: new Date().toISOString(),
	}
}
