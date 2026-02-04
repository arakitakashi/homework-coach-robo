import { useCallback, useRef, useState } from "react"
import type { WebSocketConnectionState, WebSocketIncomingMessage } from "@/types"

interface UseWebSocketOptions {
	onMessage?: (message: WebSocketIncomingMessage) => void
	onConnect?: () => void
	onDisconnect?: () => void
	onError?: (error: Event) => void
}

interface UseWebSocketReturn {
	connectionState: WebSocketConnectionState
	connect: () => void
	disconnect: () => void
	sendAudio: (data: ArrayBuffer) => void
	socket: WebSocket | null
}

export function useWebSocket(url: string, options: UseWebSocketOptions = {}): UseWebSocketReturn {
	const { onMessage, onConnect, onDisconnect, onError } = options
	const [connectionState, setConnectionState] = useState<WebSocketConnectionState>("disconnected")
	const socketRef = useRef<WebSocket | null>(null)

	const connect = useCallback(() => {
		if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
			return
		}

		setConnectionState("connecting")

		try {
			const ws = new WebSocket(url)
			socketRef.current = ws

			ws.onopen = () => {
				setConnectionState("connected")
				onConnect?.()
			}

			ws.onclose = () => {
				setConnectionState("disconnected")
				socketRef.current = null
				onDisconnect?.()
			}

			ws.onerror = (event) => {
				setConnectionState("error")
				onError?.(event)
			}

			ws.onmessage = (event) => {
				if (!onMessage) return

				try {
					if (typeof event.data === "string") {
						const message = JSON.parse(event.data) as WebSocketIncomingMessage
						onMessage(message)
					} else if (event.data instanceof ArrayBuffer) {
						onMessage({ type: "audio", data: event.data })
					}
				} catch {
					console.error("Failed to parse WebSocket message")
				}
			}
		} catch {
			setConnectionState("error")
		}
	}, [url, onMessage, onConnect, onDisconnect, onError])

	const disconnect = useCallback(() => {
		if (socketRef.current) {
			socketRef.current.close()
			socketRef.current = null
		}
	}, [])

	const sendAudio = useCallback((data: ArrayBuffer) => {
		if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
			socketRef.current.send(data)
		}
	}, [])

	return {
		connectionState,
		connect,
		disconnect,
		sendAudio,
		socket: socketRef.current,
	}
}
