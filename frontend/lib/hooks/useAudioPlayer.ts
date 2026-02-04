import { useCallback, useRef, useState } from "react"

interface UseAudioPlayerReturn {
	isPlaying: boolean
	play: (audioData: ArrayBuffer) => Promise<void>
	stop: () => void
}

export function useAudioPlayer(): UseAudioPlayerReturn {
	const [isPlaying, setIsPlaying] = useState(false)
	const audioContextRef = useRef<AudioContext | null>(null)
	const sourceNodeRef = useRef<AudioBufferSourceNode | null>(null)

	const getAudioContext = useCallback(() => {
		if (!audioContextRef.current) {
			audioContextRef.current = new AudioContext()
		}
		return audioContextRef.current
	}, [])

	const play = useCallback(
		async (audioData: ArrayBuffer) => {
			try {
				const audioContext = getAudioContext()
				const audioBuffer = await audioContext.decodeAudioData(audioData.slice(0))

				// Stop any currently playing audio
				if (sourceNodeRef.current) {
					sourceNodeRef.current.stop()
					sourceNodeRef.current = null
				}

				const source = audioContext.createBufferSource()
				source.buffer = audioBuffer

				const gainNode = audioContext.createGain()
				gainNode.gain.value = 1

				source.connect(gainNode)
				gainNode.connect(audioContext.destination)

				source.onended = () => {
					setIsPlaying(false)
					sourceNodeRef.current = null
				}

				sourceNodeRef.current = source
				source.start(0)
				setIsPlaying(true)
			} catch (error) {
				console.error("Failed to play audio:", error)
				setIsPlaying(false)
				throw error
			}
		},
		[getAudioContext],
	)

	const stop = useCallback(() => {
		if (sourceNodeRef.current) {
			try {
				sourceNodeRef.current.stop()
			} catch {
				// Ignore errors if already stopped
			}
			sourceNodeRef.current = null
		}
		setIsPlaying(false)
	}, [])

	return {
		isPlaying,
		play,
		stop,
	}
}
