import { useCallback, useRef, useState } from "react"
import { DEFAULT_AUDIO_CONFIG, type RecordingState } from "@/types"

interface UseVoiceRecorderOptions {
	onAudioData?: (data: ArrayBuffer) => void
	sampleRate?: number
}

interface UseVoiceRecorderReturn {
	recordingState: RecordingState
	audioLevel: number
	error: Error | null
	startRecording: () => Promise<void>
	stopRecording: () => void
}

export function useVoiceRecorder(options: UseVoiceRecorderOptions = {}): UseVoiceRecorderReturn {
	const { onAudioData, sampleRate = DEFAULT_AUDIO_CONFIG.sampleRate } = options
	const [recordingState, setRecordingState] = useState<RecordingState>("idle")
	const [audioLevel, setAudioLevel] = useState(0)
	const [error, setError] = useState<Error | null>(null)

	const streamRef = useRef<MediaStream | null>(null)
	const audioContextRef = useRef<AudioContext | null>(null)
	const analyserRef = useRef<AnalyserNode | null>(null)
	const animationFrameRef = useRef<number | null>(null)
	const processorRef = useRef<ScriptProcessorNode | null>(null)

	const monitorAudioLevel = useCallback(() => {
		if (!analyserRef.current) return

		const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount)
		analyserRef.current.getByteFrequencyData(dataArray)

		// Calculate average level
		const sum = dataArray.reduce((acc, val) => acc + val, 0)
		const average = sum / dataArray.length
		const normalizedLevel = Math.min(average / 128, 1)
		setAudioLevel(normalizedLevel)

		animationFrameRef.current = requestAnimationFrame(monitorAudioLevel)
	}, [])

	const startRecording = useCallback(async () => {
		try {
			setError(null)
			const stream = await navigator.mediaDevices.getUserMedia({
				audio: {
					sampleRate,
					channelCount: DEFAULT_AUDIO_CONFIG.channelCount,
					echoCancellation: DEFAULT_AUDIO_CONFIG.echoCancellation,
					noiseSuppression: DEFAULT_AUDIO_CONFIG.noiseSuppression,
				},
			})

			streamRef.current = stream

			// Set up AudioContext for level monitoring and processing
			const audioContext = new AudioContext({ sampleRate })
			audioContextRef.current = audioContext

			const source = audioContext.createMediaStreamSource(stream)
			const analyser = audioContext.createAnalyser()
			analyser.fftSize = 256
			analyserRef.current = analyser

			source.connect(analyser)

			// Set up ScriptProcessor for audio data (deprecated but widely supported)
			const processor = audioContext.createScriptProcessor(4096, 1, 1)
			processorRef.current = processor

			processor.onaudioprocess = (event) => {
				if (onAudioData) {
					const inputData = event.inputBuffer.getChannelData(0)
					// Convert Float32Array to Int16Array (PCM 16-bit)
					const pcmData = new Int16Array(inputData.length)
					for (let i = 0; i < inputData.length; i++) {
						const s = Math.max(-1, Math.min(1, inputData[i]))
						pcmData[i] = s < 0 ? s * 0x8000 : s * 0x7fff
					}
					onAudioData(pcmData.buffer)
				}
			}

			source.connect(processor)
			processor.connect(audioContext.destination)

			setRecordingState("recording")
			monitorAudioLevel()
		} catch (err) {
			setError(err instanceof Error ? err : new Error("Failed to start recording"))
			setRecordingState("idle")
			throw err
		}
	}, [sampleRate, onAudioData, monitorAudioLevel])

	const stopRecording = useCallback(() => {
		if (animationFrameRef.current) {
			cancelAnimationFrame(animationFrameRef.current)
			animationFrameRef.current = null
		}

		if (processorRef.current) {
			processorRef.current.disconnect()
			processorRef.current = null
		}

		if (streamRef.current) {
			for (const track of streamRef.current.getTracks()) {
				track.stop()
			}
			streamRef.current = null
		}

		if (audioContextRef.current) {
			audioContextRef.current.close()
			audioContextRef.current = null
		}

		analyserRef.current = null
		setRecordingState("idle")
		setAudioLevel(0)
	}, [])

	return {
		recordingState,
		audioLevel,
		error,
		startRecording,
		stopRecording,
	}
}
