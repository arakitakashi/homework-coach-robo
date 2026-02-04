import { act, renderHook, waitFor } from "@testing-library/react"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import { useVoiceRecorder } from "./useVoiceRecorder"

// Mock MediaStream and MediaRecorder
const mockMediaStream = {
	getTracks: () => [{ stop: vi.fn() }],
}

// Mock AudioContext class
class MockAudioContext {
	createMediaStreamSource = vi.fn(() => ({
		connect: vi.fn(),
	}))
	createAnalyser = vi.fn(() => ({
		fftSize: 256,
		frequencyBinCount: 128,
		getByteFrequencyData: vi.fn((array: Uint8Array) => {
			for (let i = 0; i < array.length; i++) {
				array[i] = 50
			}
		}),
	}))
	createScriptProcessor = vi.fn(() => ({
		connect: vi.fn(),
		disconnect: vi.fn(),
		onaudioprocess: null,
	}))
	destination = {}
	close = vi.fn()
}

describe("useVoiceRecorder", () => {
	let originalGetUserMedia: typeof navigator.mediaDevices.getUserMedia
	let originalAudioContext: typeof AudioContext

	beforeEach(() => {
		originalGetUserMedia = navigator.mediaDevices?.getUserMedia
		originalAudioContext = globalThis.AudioContext

		// Mock getUserMedia
		Object.defineProperty(navigator, "mediaDevices", {
			value: {
				getUserMedia: vi.fn().mockResolvedValue(mockMediaStream),
			},
			writable: true,
		})

		// Mock AudioContext
		// biome-ignore lint/suspicious/noExplicitAny: mocking AudioContext
		globalThis.AudioContext = MockAudioContext as any
	})

	afterEach(() => {
		if (originalGetUserMedia) {
			Object.defineProperty(navigator, "mediaDevices", {
				value: { getUserMedia: originalGetUserMedia },
				writable: true,
			})
		}
		if (originalAudioContext) {
			globalThis.AudioContext = originalAudioContext
		}
		vi.clearAllMocks()
	})

	it("initializes with idle recording state", () => {
		const { result } = renderHook(() => useVoiceRecorder())
		expect(result.current.recordingState).toBe("idle")
		expect(result.current.audioLevel).toBe(0)
	})

	it("starts recording and updates state", async () => {
		const { result } = renderHook(() => useVoiceRecorder())

		await act(async () => {
			await result.current.startRecording()
		})

		await waitFor(() => {
			expect(result.current.recordingState).toBe("recording")
		})
	})

	it("stops recording and updates state", async () => {
		const { result } = renderHook(() => useVoiceRecorder())

		await act(async () => {
			await result.current.startRecording()
		})

		await waitFor(() => {
			expect(result.current.recordingState).toBe("recording")
		})

		act(() => {
			result.current.stopRecording()
		})

		await waitFor(() => {
			expect(result.current.recordingState).toBe("idle")
		})
	})

	it("handles permission denied error", async () => {
		const error = new Error("Permission denied")
		vi.mocked(navigator.mediaDevices.getUserMedia).mockRejectedValueOnce(error)

		const { result } = renderHook(() => useVoiceRecorder())

		await act(async () => {
			try {
				await result.current.startRecording()
			} catch {
				// Expected error
			}
		})

		expect(result.current.error).toBeTruthy()
		expect(result.current.recordingState).toBe("idle")
	})

	it("requests microphone with correct audio constraints", async () => {
		const { result } = renderHook(() => useVoiceRecorder())

		await act(async () => {
			await result.current.startRecording()
		})

		expect(navigator.mediaDevices.getUserMedia).toHaveBeenCalledWith({
			audio: expect.objectContaining({
				sampleRate: 16000,
				channelCount: 1,
				echoCancellation: true,
				noiseSuppression: true,
			}),
		})
	})
})
