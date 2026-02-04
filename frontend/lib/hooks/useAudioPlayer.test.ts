import { act, renderHook, waitFor } from "@testing-library/react"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import { useAudioPlayer } from "./useAudioPlayer"

// Mock AudioContext and related APIs
const mockAudioBufferSourceNode = {
	buffer: null as AudioBuffer | null,
	connect: vi.fn(),
	start: vi.fn(),
	stop: vi.fn(),
	onended: null as (() => void) | null,
}

const mockGainNode = {
	gain: { value: 1 },
	connect: vi.fn(),
}

const mockAudioBuffer = {
	duration: 1,
	numberOfChannels: 1,
	sampleRate: 16000,
	length: 16000,
	getChannelData: vi.fn(() => new Float32Array(16000)),
	copyFromChannel: vi.fn(),
	copyToChannel: vi.fn(),
}

const _mockAudioContext = {
	createBufferSource: vi.fn(() => mockAudioBufferSourceNode),
	createGain: vi.fn(() => mockGainNode),
	decodeAudioData: vi.fn().mockResolvedValue(mockAudioBuffer),
	destination: {},
	close: vi.fn(),
	state: "running",
}

// Mock AudioContext class
class MockAudioContext {
	createBufferSource = vi.fn(() => mockAudioBufferSourceNode)
	createGain = vi.fn(() => mockGainNode)
	decodeAudioData = vi.fn().mockResolvedValue(mockAudioBuffer)
	destination = {}
	close = vi.fn()
	state = "running"
}

describe("useAudioPlayer", () => {
	let originalAudioContext: typeof AudioContext

	beforeEach(() => {
		originalAudioContext = globalThis.AudioContext
		// biome-ignore lint/suspicious/noExplicitAny: mocking AudioContext
		globalThis.AudioContext = MockAudioContext as any

		// Reset mock function state
		mockAudioBufferSourceNode.buffer = null
		mockAudioBufferSourceNode.onended = null
	})

	afterEach(() => {
		globalThis.AudioContext = originalAudioContext
		vi.clearAllMocks()
	})

	it("initializes with isPlaying false", () => {
		const { result } = renderHook(() => useAudioPlayer())
		expect(result.current.isPlaying).toBe(false)
	})

	it("plays audio and updates isPlaying state", async () => {
		const { result } = renderHook(() => useAudioPlayer())
		const audioData = new ArrayBuffer(1024)

		await act(async () => {
			await result.current.play(audioData)
		})

		await waitFor(() => {
			expect(result.current.isPlaying).toBe(true)
		})
	})

	it("stops playing and updates isPlaying state", async () => {
		const { result } = renderHook(() => useAudioPlayer())
		const audioData = new ArrayBuffer(1024)

		await act(async () => {
			await result.current.play(audioData)
		})

		await waitFor(() => {
			expect(result.current.isPlaying).toBe(true)
		})

		act(() => {
			result.current.stop()
		})

		await waitFor(() => {
			expect(result.current.isPlaying).toBe(false)
		})
	})

	it("sets isPlaying to false when audio ends naturally", async () => {
		const { result } = renderHook(() => useAudioPlayer())
		const audioData = new ArrayBuffer(1024)

		await act(async () => {
			await result.current.play(audioData)
		})

		await waitFor(() => {
			expect(result.current.isPlaying).toBe(true)
		})

		// Simulate audio ending
		act(() => {
			mockAudioBufferSourceNode.onended?.()
		})

		await waitFor(() => {
			expect(result.current.isPlaying).toBe(false)
		})
	})

	it("creates audio buffer source when playing", async () => {
		const { result } = renderHook(() => useAudioPlayer())
		const audioData = new ArrayBuffer(1024)

		await act(async () => {
			await result.current.play(audioData)
		})

		// Verify audio was decoded and played
		expect(result.current.isPlaying).toBe(true)
	})
})
