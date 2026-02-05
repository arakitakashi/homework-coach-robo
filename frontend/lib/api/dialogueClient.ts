/**
 * SSE対話クライアント
 *
 * バックエンドの /api/v1/dialogue/run エンドポイントに接続し、
 * SSEストリーミングでレスポンスを受信する。
 */

import type { DoneEvent, ErrorEvent, RunDialogueRequest, SSEEventType, TextEvent } from "./types"

/** DialogueClientのオプション */
export interface DialogueClientOptions {
	/** バックエンドのベースURL */
	baseUrl: string
	/** テキストイベント受信時のコールバック */
	onText: (text: string) => void
	/** 完了イベント受信時のコールバック */
	onDone: (sessionId: string) => void
	/** エラーイベント受信時のコールバック */
	onError: (error: string, code: string) => void
}

/** SSEイベントのパース結果 */
interface ParsedSSEEvent {
	type: SSEEventType
	data: string
}

/**
 * SSE対話クライアント
 *
 * fetch + ReadableStreamを使用してSSEストリーミングを処理する。
 * EventSourceはPOSTメソッドをサポートしないため、fetchを使用。
 */
export class DialogueClient {
	private readonly baseUrl: string
	private readonly onText: (text: string) => void
	private readonly onDone: (sessionId: string) => void
	private readonly onError: (error: string, code: string) => void
	private abortController: AbortController | null = null

	constructor(options: DialogueClientOptions) {
		this.baseUrl = options.baseUrl
		this.onText = options.onText
		this.onDone = options.onDone
		this.onError = options.onError
	}

	/**
	 * 対話を実行する
	 *
	 * @param request - 対話リクエスト
	 */
	async run(request: RunDialogueRequest): Promise<void> {
		this.abortController = new AbortController()

		try {
			const response = await fetch(`${this.baseUrl}/api/v1/dialogue/run`, {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
					Accept: "text/event-stream",
				},
				body: JSON.stringify(request),
				signal: this.abortController.signal,
			})

			if (!response.ok) {
				this.onError(`HTTP error: ${response.status}`, "HTTP_ERROR")
				return
			}

			await this.processStream(response)
		} catch (error) {
			if (error instanceof Error && error.name === "AbortError") {
				// 中断された場合は何もしない
				return
			}
			const message = error instanceof Error ? error.message : "Unknown error"
			this.onError(message, "NETWORK_ERROR")
		}
	}

	/**
	 * 実行中のリクエストを中断する
	 */
	abort(): void {
		if (this.abortController) {
			this.abortController.abort()
			this.abortController = null
		}
	}

	/**
	 * SSEストリームを処理する
	 */
	private async processStream(response: Response): Promise<void> {
		const reader = response.body?.getReader()
		if (!reader) {
			this.onError("Response body is null", "STREAM_ERROR")
			return
		}

		const decoder = new TextDecoder()
		let buffer = ""

		try {
			while (true) {
				const { done, value } = await reader.read()
				if (done) break

				buffer += decoder.decode(value, { stream: true })

				// バッファからイベントを抽出して処理
				const events = this.extractEvents(buffer)
				buffer = events.remainingBuffer

				for (const event of events.parsedEvents) {
					this.handleEvent(event)
				}
			}
		} finally {
			reader.releaseLock()
		}
	}

	/**
	 * バッファからSSEイベントを抽出する
	 */
	private extractEvents(buffer: string): {
		parsedEvents: ParsedSSEEvent[]
		remainingBuffer: string
	} {
		const parsedEvents: ParsedSSEEvent[] = []
		const eventSeparator = "\n\n"
		let remainingBuffer = buffer

		while (remainingBuffer.includes(eventSeparator)) {
			const eventEnd = remainingBuffer.indexOf(eventSeparator)
			const eventText = remainingBuffer.slice(0, eventEnd)
			remainingBuffer = remainingBuffer.slice(eventEnd + eventSeparator.length)

			const parsed = this.parseSSEEvent(eventText)
			if (parsed) {
				parsedEvents.push(parsed)
			}
		}

		return { parsedEvents, remainingBuffer }
	}

	/**
	 * SSEイベントテキストをパースする
	 */
	private parseSSEEvent(eventText: string): ParsedSSEEvent | null {
		const lines = eventText.split("\n")
		let eventType: SSEEventType | null = null
		let data: string | null = null

		for (const line of lines) {
			if (line.startsWith("event: ")) {
				eventType = line.slice(7) as SSEEventType
			} else if (line.startsWith("data: ")) {
				data = line.slice(6)
			}
		}

		if (eventType && data) {
			return { type: eventType, data }
		}

		return null
	}

	/**
	 * パースされたイベントを処理する
	 */
	private handleEvent(event: ParsedSSEEvent): void {
		try {
			switch (event.type) {
				case "text": {
					const textEvent = JSON.parse(event.data) as TextEvent
					this.onText(textEvent.text)
					break
				}
				case "done": {
					const doneEvent = JSON.parse(event.data) as DoneEvent
					this.onDone(doneEvent.session_id)
					break
				}
				case "error": {
					const errorEvent = JSON.parse(event.data) as ErrorEvent
					this.onError(errorEvent.error, errorEvent.code)
					break
				}
			}
		} catch {
			// JSONパースエラーは無視（不正なデータ）
			console.warn("Failed to parse SSE event data:", event.data)
		}
	}
}
