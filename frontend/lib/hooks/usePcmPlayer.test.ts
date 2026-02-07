/**
 * usePcmPlayer フックテスト
 *
 * AudioWorkletベースのPCMストリーミング再生フックのテスト
 */

import { act, renderHook } from "@testing-library/react"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import { usePcmPlayer } from "./usePcmPlayer"

// AudioWorkletNode モック
const mockWorkletPort = {
	postMessage: vi.fn(),
	onmessage: null as ((event: MessageEvent) => void) | null,
}

const mockWorkletNodeConnect = vi.fn()
const mockWorkletNodeDisconnect = vi.fn()

class MockAudioWorkletNode {
	port = {
		postMessage: mockWorkletPort.postMessage,
		onmessage: mockWorkletPort.onmessage,
	}
	connect = mockWorkletNodeConnect
	disconnect = mockWorkletNodeDisconnect
}

// AudioContext モック
const mockAddModule = vi.fn().mockResolvedValue(undefined)
const mockClose = vi.fn().mockResolvedValue(undefined)

class MockAudioContext {
	sampleRate = 24000
	state = "running"
	audioWorklet = {
		addModule: mockAddModule,
	}
	destination = {}
	close = mockClose
}

globalThis.AudioContext = MockAudioContext as unknown as typeof AudioContext
globalThis.AudioWorkletNode = MockAudioWorkletNode as unknown as typeof AudioWorkletNode

describe("usePcmPlayer", () => {
	beforeEach(() => {
		vi.clearAllMocks()
		vi.useFakeTimers()
	})

	afterEach(() => {
		vi.useRealTimers()
		vi.restoreAllMocks()
	})

	describe("初期状態", () => {
		it("isPlayingがfalseで初期化される", () => {
			const { result } = renderHook(() => usePcmPlayer())
			expect(result.current.isPlaying).toBe(false)
		})

		it("必要な関数が返される", () => {
			const { result } = renderHook(() => usePcmPlayer())
			expect(typeof result.current.feedAudio).toBe("function")
			expect(typeof result.current.stop).toBe("function")
			expect(typeof result.current.initialize).toBe("function")
			expect(typeof result.current.cleanup).toBe("function")
		})
	})

	describe("initialize", () => {
		it("AudioContextとWorkletNodeを作成する", async () => {
			const { result } = renderHook(() => usePcmPlayer())

			await act(async () => {
				await result.current.initialize()
			})

			expect(mockAddModule).toHaveBeenCalledWith("/worklets/pcm-player-processor.js")
			expect(mockWorkletNodeConnect).toHaveBeenCalled()
		})

		it("二重初期化しない", async () => {
			const { result } = renderHook(() => usePcmPlayer())

			await act(async () => {
				await result.current.initialize()
			})
			await act(async () => {
				await result.current.initialize()
			})

			// addModuleは1回のみ呼ばれる
			expect(mockAddModule).toHaveBeenCalledTimes(1)
		})
	})

	describe("feedAudio", () => {
		it("初期化後にworklet portへデータを送信する", async () => {
			const { result } = renderHook(() => usePcmPlayer())

			await act(async () => {
				await result.current.initialize()
			})

			const pcmData = new ArrayBuffer(1024)

			act(() => {
				result.current.feedAudio(pcmData)
			})

			expect(mockWorkletPort.postMessage).toHaveBeenCalledWith(pcmData)
		})

		it("feedAudio後にisPlayingがtrueになる", async () => {
			const { result } = renderHook(() => usePcmPlayer())

			await act(async () => {
				await result.current.initialize()
			})

			act(() => {
				result.current.feedAudio(new ArrayBuffer(1024))
			})

			expect(result.current.isPlaying).toBe(true)
		})

		it("300ms後にisPlayingがfalseになる", async () => {
			const { result } = renderHook(() => usePcmPlayer())

			await act(async () => {
				await result.current.initialize()
			})

			act(() => {
				result.current.feedAudio(new ArrayBuffer(1024))
			})

			expect(result.current.isPlaying).toBe(true)

			act(() => {
				vi.advanceTimersByTime(300)
			})

			expect(result.current.isPlaying).toBe(false)
		})

		it("連続feedAudioでタイムアウトがリセットされる", async () => {
			const { result } = renderHook(() => usePcmPlayer())

			await act(async () => {
				await result.current.initialize()
			})

			act(() => {
				result.current.feedAudio(new ArrayBuffer(1024))
			})

			// 200ms後に再度feed
			act(() => {
				vi.advanceTimersByTime(200)
			})

			act(() => {
				result.current.feedAudio(new ArrayBuffer(1024))
			})

			// 最初のfeedから300ms経過してもまだplaying
			act(() => {
				vi.advanceTimersByTime(200)
			})

			expect(result.current.isPlaying).toBe(true)

			// 2回目のfeedから300ms経過でfalse
			act(() => {
				vi.advanceTimersByTime(100)
			})

			expect(result.current.isPlaying).toBe(false)
		})

		it("初期化前はpostMessageを呼ばない", () => {
			const { result } = renderHook(() => usePcmPlayer())

			act(() => {
				result.current.feedAudio(new ArrayBuffer(1024))
			})

			expect(mockWorkletPort.postMessage).not.toHaveBeenCalled()
		})
	})

	describe("stop", () => {
		it("endOfAudioコマンドを送信する", async () => {
			const { result } = renderHook(() => usePcmPlayer())

			await act(async () => {
				await result.current.initialize()
			})

			act(() => {
				result.current.feedAudio(new ArrayBuffer(1024))
			})

			act(() => {
				result.current.stop()
			})

			expect(mockWorkletPort.postMessage).toHaveBeenCalledWith({ command: "endOfAudio" })
		})

		it("isPlayingをfalseにする", async () => {
			const { result } = renderHook(() => usePcmPlayer())

			await act(async () => {
				await result.current.initialize()
			})

			act(() => {
				result.current.feedAudio(new ArrayBuffer(1024))
			})

			expect(result.current.isPlaying).toBe(true)

			act(() => {
				result.current.stop()
			})

			expect(result.current.isPlaying).toBe(false)
		})
	})

	describe("cleanup", () => {
		it("AudioContextを閉じる", async () => {
			const { result } = renderHook(() => usePcmPlayer())

			await act(async () => {
				await result.current.initialize()
			})

			act(() => {
				result.current.cleanup()
			})

			expect(mockClose).toHaveBeenCalled()
		})

		it("WorkletNodeを切断する", async () => {
			const { result } = renderHook(() => usePcmPlayer())

			await act(async () => {
				await result.current.initialize()
			})

			act(() => {
				result.current.cleanup()
			})

			expect(mockWorkletNodeDisconnect).toHaveBeenCalled()
		})

		it("cleanup後にfeedAudioが無視される", async () => {
			const { result } = renderHook(() => usePcmPlayer())

			await act(async () => {
				await result.current.initialize()
			})

			act(() => {
				result.current.cleanup()
			})

			mockWorkletPort.postMessage.mockClear()

			act(() => {
				result.current.feedAudio(new ArrayBuffer(1024))
			})

			expect(mockWorkletPort.postMessage).not.toHaveBeenCalled()
		})
	})
})
