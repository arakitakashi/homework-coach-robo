/**
 * useVoiceStream フック
 *
 * WebSocketを使った双方向音声ストリーミングを管理するカスタムフック。
 * - VoiceWebSocketClientの接続管理
 * - AudioWorkletを使った音声録音
 * - 音声データのストリーミング送信
 */

import { useCallback, useRef, useState } from "react"
import type { VoiceConnectionState } from "@/lib/api"
import { VoiceWebSocketClient } from "@/lib/api"

/** フックのオプション */
export interface UseVoiceStreamOptions {
	/** 音声データ受信コールバック */
	onAudioData?: (data: ArrayBuffer) => void
	/** トランスクリプション受信コールバック */
	onTranscription?: (text: string, isUser: boolean, finished: boolean) => void
	/** ターン完了コールバック */
	onTurnComplete?: () => void
	/** 中断コールバック */
	onInterrupted?: () => void
	/** Phase 2a: ツール実行コールバック */
	onToolExecution?: (toolName: string, status: string, result?: Record<string, unknown>) => void
}

/** フックの戻り値 */
export interface UseVoiceStreamReturn {
	/** 接続状態 */
	connectionState: VoiceConnectionState
	/** 録音中フラグ */
	isRecording: boolean
	/** 音声レベル（0-1の範囲、RMS値） */
	audioLevel: number
	/** エラーメッセージ */
	error: string | null
	/** WebSocket接続を開始 */
	connect: (userId: string, sessionId: string) => void
	/** WebSocket接続を切断 */
	disconnect: () => void
	/** 録音を開始 */
	startRecording: () => Promise<void>
	/** 録音を停止 */
	stopRecording: () => void
	/** テキストメッセージを送信 */
	sendText: (text: string) => void
	/** エラーをクリア */
	clearError: () => void
}

/** Float32ArrayをInt16Array（PCM 16-bit）に変換 */
function convertFloat32ToPCM16(float32Array: Float32Array): ArrayBuffer {
	const pcm16 = new Int16Array(float32Array.length)
	for (let i = 0; i < float32Array.length; i++) {
		// -1.0 ~ 1.0 を -32768 ~ 32767 に変換
		const s = Math.max(-1, Math.min(1, float32Array[i]))
		pcm16[i] = s < 0 ? s * 0x8000 : s * 0x7fff
	}
	return pcm16.buffer
}

/**
 * 双方向音声ストリーミングを管理するフック
 */
export function useVoiceStream(options: UseVoiceStreamOptions = {}): UseVoiceStreamReturn {
	const { onAudioData, onTranscription, onTurnComplete, onInterrupted, onToolExecution } = options

	// 状態
	const [connectionState, setConnectionState] = useState<VoiceConnectionState>("disconnected")
	const [isRecording, setIsRecording] = useState(false)
	const [audioLevel, setAudioLevel] = useState(0)
	const [error, setError] = useState<string | null>(null)

	// Refs
	const clientRef = useRef<VoiceWebSocketClient | null>(null)
	const audioContextRef = useRef<AudioContext | null>(null)
	const mediaStreamRef = useRef<MediaStream | null>(null)
	const workletNodeRef = useRef<AudioWorkletNode | null>(null)

	/**
	 * 録音を停止（内部用）
	 */
	const stopRecordingInternal = useCallback(() => {
		// MediaStreamのトラックを停止
		if (mediaStreamRef.current) {
			for (const track of mediaStreamRef.current.getTracks()) {
				track.stop()
			}
			mediaStreamRef.current = null
		}

		// AudioWorkletNodeを切断
		if (workletNodeRef.current) {
			workletNodeRef.current.disconnect()
			workletNodeRef.current = null
		}

		// AudioContextを閉じる
		if (audioContextRef.current) {
			audioContextRef.current.close()
			audioContextRef.current = null
		}

		setIsRecording(false)
		setAudioLevel(0)
	}, [])

	/**
	 * WebSocket接続を開始
	 */
	const connect = useCallback(
		(userId: string, sessionId: string) => {
			// 既存の接続を切断
			if (clientRef.current) {
				clientRef.current.disconnect()
			}

			// 新しいクライアントを作成
			const baseUrl = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000"
			const client = new VoiceWebSocketClient({
				baseUrl,
				userId,
				sessionId,
				onAudioData: (data) => {
					onAudioData?.(data)
				},
				onTranscription: (text, isUser, finished) => {
					onTranscription?.(text, isUser, finished)
				},
				onTurnComplete: () => {
					onTurnComplete?.()
				},
				onInterrupted: () => {
					onInterrupted?.()
				},
				onError: (errorMessage) => {
					setError(errorMessage)
				},
				onConnectionChange: (state) => {
					setConnectionState(state)
				},
				onToolExecution: onToolExecution
					? (toolName, status, result) => {
							onToolExecution(toolName, status, result)
						}
					: undefined,
			})

			clientRef.current = client
			client.connect()
		},
		[onAudioData, onTranscription, onTurnComplete, onInterrupted, onToolExecution],
	)

	/**
	 * WebSocket接続を切断
	 */
	const disconnect = useCallback(() => {
		// 録音を停止
		stopRecordingInternal()

		// WebSocketを切断
		if (clientRef.current) {
			clientRef.current.disconnect()
			clientRef.current = null
		}
	}, [stopRecordingInternal])

	/**
	 * 録音を開始
	 */
	const startRecording = useCallback(async () => {
		// 接続チェック
		if (!clientRef.current?.isConnected) {
			setError("WebSocket未接続")
			return
		}

		try {
			// マイクへのアクセスを要求
			const stream = await navigator.mediaDevices.getUserMedia({
				audio: {
					sampleRate: 16000,
					channelCount: 1,
					echoCancellation: true,
					noiseSuppression: true,
				},
			})
			mediaStreamRef.current = stream

			// AudioContextを作成（16kHz）
			const audioContext = new AudioContext({ sampleRate: 16000 })
			audioContextRef.current = audioContext

			// AudioWorkletモジュールをロード
			await audioContext.audioWorklet.addModule("/worklets/pcm-recorder-processor.js")

			// AudioWorkletNodeを作成
			const workletNode = new AudioWorkletNode(audioContext, "pcm-recorder-processor")
			workletNodeRef.current = workletNode

			// 音声データを受信してWebSocketで送信
			workletNode.port.onmessage = (event: MessageEvent<Float32Array>) => {
				const float32Data = event.data

				// RMS計算で音声レベルを更新
				let sum = 0
				for (let i = 0; i < float32Data.length; i++) {
					sum += float32Data[i] * float32Data[i]
				}
				const rms = Math.sqrt(sum / float32Data.length)
				setAudioLevel(Math.min(1, rms * 5))

				if (clientRef.current?.isConnected) {
					const pcmData = convertFloat32ToPCM16(float32Data)
					clientRef.current.sendAudio(pcmData)
				}
			}

			// マイク入力をWorkletに接続
			const source = audioContext.createMediaStreamSource(stream)
			source.connect(workletNode)
			workletNode.connect(audioContext.destination)

			setIsRecording(true)
		} catch (err) {
			const errorMessage = err instanceof Error ? err.message : "録音開始エラー"
			setError(errorMessage)
		}
	}, [])

	/**
	 * 録音を停止
	 */
	const stopRecording = useCallback(() => {
		stopRecordingInternal()
	}, [stopRecordingInternal])

	/**
	 * テキストメッセージを送信
	 */
	const sendText = useCallback((text: string) => {
		if (clientRef.current?.isConnected) {
			clientRef.current.sendText(text)
		}
	}, [])

	/**
	 * エラーをクリア
	 */
	const clearError = useCallback(() => {
		setError(null)
	}, [])

	return {
		connectionState,
		isRecording,
		audioLevel,
		error,
		connect,
		disconnect,
		startRecording,
		stopRecording,
		sendText,
		clearError,
	}
}
