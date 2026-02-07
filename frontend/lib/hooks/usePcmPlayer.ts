/**
 * usePcmPlayer フック
 *
 * AudioWorkletベースのPCMストリーミング再生フック。
 * Gemini Live APIからのPCM 16-bit音声データを24kHzで再生する。
 */

import { useCallback, useRef, useState } from "react"

/** フックの戻り値 */
export interface UsePcmPlayerReturn {
	/** 再生中フラグ */
	isPlaying: boolean
	/** PCMデータを再生バッファに追加 */
	feedAudio: (pcmData: ArrayBuffer) => void
	/** 再生を停止しバッファをクリア */
	stop: () => void
	/** AudioContextとWorkletを初期化 */
	initialize: () => Promise<void>
	/** リソースを解放 */
	cleanup: () => void
}

/** 再生停止判定のタイムアウト（ms） */
const PLAYBACK_TIMEOUT_MS = 300

/**
 * PCMストリーミング再生フック
 *
 * AudioContext(24kHz) + pcm-player-processor.js AudioWorkletを使用して
 * ストリーミングPCMデータをリアルタイム再生する。
 */
export function usePcmPlayer(): UsePcmPlayerReturn {
	const [isPlaying, setIsPlaying] = useState(false)

	const audioContextRef = useRef<AudioContext | null>(null)
	const workletNodeRef = useRef<AudioWorkletNode | null>(null)
	const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null)

	const initialize = useCallback(async () => {
		// 二重初期化を防止
		if (audioContextRef.current) {
			return
		}

		const audioContext = new AudioContext({ sampleRate: 24000 })
		audioContextRef.current = audioContext

		await audioContext.audioWorklet.addModule("/worklets/pcm-player-processor.js")

		const workletNode = new AudioWorkletNode(audioContext, "pcm-player-processor")
		workletNode.connect(audioContext.destination)
		workletNodeRef.current = workletNode
	}, [])

	const feedAudio = useCallback((pcmData: ArrayBuffer) => {
		if (!workletNodeRef.current) {
			return
		}

		workletNodeRef.current.port.postMessage(pcmData)
		setIsPlaying(true)

		// 既存のタイムアウトをクリア
		if (timeoutRef.current) {
			clearTimeout(timeoutRef.current)
		}

		// 300ms間データが来なければ再生停止と判定
		timeoutRef.current = setTimeout(() => {
			setIsPlaying(false)
			timeoutRef.current = null
		}, PLAYBACK_TIMEOUT_MS)
	}, [])

	const stop = useCallback(() => {
		if (timeoutRef.current) {
			clearTimeout(timeoutRef.current)
			timeoutRef.current = null
		}

		if (workletNodeRef.current) {
			workletNodeRef.current.port.postMessage({ command: "endOfAudio" })
		}

		setIsPlaying(false)
	}, [])

	const cleanup = useCallback(() => {
		if (timeoutRef.current) {
			clearTimeout(timeoutRef.current)
			timeoutRef.current = null
		}

		if (workletNodeRef.current) {
			workletNodeRef.current.disconnect()
			workletNodeRef.current = null
		}

		if (audioContextRef.current) {
			audioContextRef.current.close()
			audioContextRef.current = null
		}

		setIsPlaying(false)
	}, [])

	return {
		isPlaying,
		feedAudio,
		stop,
		initialize,
		cleanup,
	}
}
