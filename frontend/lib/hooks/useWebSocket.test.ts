import { act, renderHook, waitFor } from "@testing-library/react"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import { useWebSocket } from "./useWebSocket"

// Mock WebSocket
class MockWebSocket {
	static CONNECTING = 0
	static OPEN = 1
	static CLOSING = 2
	static CLOSED = 3

	url: string
	readyState: number = MockWebSocket.CONNECTING
	onopen: ((event: Event) => void) | null = null
	onclose: ((event: CloseEvent) => void) | null = null
	onmessage: ((event: MessageEvent) => void) | null = null
	onerror: ((event: Event) => void) | null = null

	constructor(url: string) {
		this.url = url
		// Simulate async connection
		setTimeout(() => {
			this.readyState = MockWebSocket.OPEN
			this.onopen?.(new Event("open"))
		}, 0)
	}

	send = vi.fn()
	close = vi.fn(() => {
		this.readyState = MockWebSocket.CLOSED
		this.onclose?.(new CloseEvent("close"))
	})

	// Helper to simulate receiving a message
	simulateMessage(data: string | ArrayBuffer) {
		this.onmessage?.(new MessageEvent("message", { data }))
	}

	// Helper to simulate error
	simulateError() {
		this.onerror?.(new Event("error"))
	}
}

describe("useWebSocket", () => {
	let originalWebSocket: typeof WebSocket

	beforeEach(() => {
		originalWebSocket = globalThis.WebSocket
		// biome-ignore lint/suspicious/noExplicitAny: mocking WebSocket
		globalThis.WebSocket = MockWebSocket as any
	})

	afterEach(() => {
		globalThis.WebSocket = originalWebSocket
		vi.clearAllMocks()
	})

	it("initializes with disconnected state", () => {
		const { result } = renderHook(() => useWebSocket("wss://example.com/ws"))
		expect(result.current.connectionState).toBe("disconnected")
	})

	it("connects and updates state to connected", async () => {
		const { result } = renderHook(() => useWebSocket("wss://example.com/ws"))

		act(() => {
			result.current.connect()
		})

		await waitFor(() => {
			expect(result.current.connectionState).toBe("connected")
		})
	})

	it("disconnects and updates state", async () => {
		const { result } = renderHook(() => useWebSocket("wss://example.com/ws"))

		act(() => {
			result.current.connect()
		})

		await waitFor(() => {
			expect(result.current.connectionState).toBe("connected")
		})

		act(() => {
			result.current.disconnect()
		})

		await waitFor(() => {
			expect(result.current.connectionState).toBe("disconnected")
		})
	})

	it("sends audio data when connected", async () => {
		const { result } = renderHook(() => useWebSocket("wss://example.com/ws"))

		act(() => {
			result.current.connect()
		})

		await waitFor(() => {
			expect(result.current.connectionState).toBe("connected")
		})

		const audioData = new ArrayBuffer(1024)
		const mockWs = result.current.socket as unknown as MockWebSocket
		act(() => {
			result.current.sendAudio(audioData)
		})

		// Verify send was called on the instance
		expect(mockWs.send).toHaveBeenCalledWith(audioData)
	})

	it("does not send audio when disconnected", () => {
		const { result } = renderHook(() => useWebSocket("wss://example.com/ws"))

		const audioData = new ArrayBuffer(1024)
		act(() => {
			result.current.sendAudio(audioData)
		})

		// socket should be null when not connected
		expect(result.current.socket).toBeNull()
	})

	it("calls onMessage when receiving text message", async () => {
		const onMessage = vi.fn()
		const { result } = renderHook(() => useWebSocket("wss://example.com/ws", { onMessage }))

		act(() => {
			result.current.connect()
		})

		await waitFor(() => {
			expect(result.current.connectionState).toBe("connected")
		})

		// Simulate receiving a message
		const mockWs = result.current.socket as unknown as MockWebSocket
		act(() => {
			mockWs.simulateMessage(JSON.stringify({ type: "transcript", text: "Hello" }))
		})

		expect(onMessage).toHaveBeenCalled()
	})
})
