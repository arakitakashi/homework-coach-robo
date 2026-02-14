/**
 * useCameraCapture フックテスト
 *
 * カメラライフサイクル管理フックのユニットテスト。
 * MediaDevices API、Canvas、VisionClient をモックして各状態遷移を検証。
 */

import { act, renderHook } from "@testing-library/react"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import { useCameraCapture } from "./useCameraCapture"

// VisionClient モック - vi.hoisted() でモック変数を先に定義
const { mockRecognizeImage } = vi.hoisted(() => ({
	mockRecognizeImage: vi.fn(),
}))
vi.mock("@/lib/api/visionClient", () => {
	// コンストラクタとして使えるよう通常の関数で定義
	function MockVisionClient() {
		return { recognizeImage: mockRecognizeImage }
	}
	return { VisionClient: MockVisionClient }
})

// MediaStreamトラックのモック
const mockStop = vi.fn()
const mockStream = {
	getTracks: () => [{ stop: mockStop }],
	getVideoTracks: () => [{ stop: mockStop }],
} as unknown as MediaStream

// getUserMedia モック
const mockGetUserMedia = vi.fn()

// Canvas モック
const mockDrawImage = vi.fn()
const mockToDataURL = vi.fn().mockReturnValue("data:image/jpeg;base64,mockBase64Data")

describe("useCameraCapture", () => {
	beforeEach(() => {
		mockStop.mockClear()
		mockGetUserMedia.mockReset()
		mockRecognizeImage.mockReset()
		mockDrawImage.mockClear()
		mockToDataURL.mockClear().mockReturnValue("data:image/jpeg;base64,mockBase64Data")

		// navigator.mediaDevices モック
		Object.defineProperty(navigator, "mediaDevices", {
			value: { getUserMedia: mockGetUserMedia },
			writable: true,
			configurable: true,
		})

		// HTMLCanvasElement モック
		HTMLCanvasElement.prototype.getContext = vi.fn().mockReturnValue({
			drawImage: mockDrawImage,
		}) as unknown as typeof HTMLCanvasElement.prototype.getContext
		HTMLCanvasElement.prototype.toDataURL = mockToDataURL

		// HTMLVideoElement のサイズモック
		Object.defineProperty(HTMLVideoElement.prototype, "videoWidth", {
			get: () => 640,
			configurable: true,
		})
		Object.defineProperty(HTMLVideoElement.prototype, "videoHeight", {
			get: () => 480,
			configurable: true,
		})
	})

	afterEach(() => {
		// vi.restoreAllMocks() は vi.mock のファクトリ設定を壊すため使用しない
		// 個別の mock は beforeEach で mockReset/mockClear している
	})

	describe("初期状態", () => {
		it("status が initial で開始する", () => {
			const { result } = renderHook(() => useCameraCapture())
			expect(result.current.status).toBe("initial")
		})

		it("error が null で開始する", () => {
			const { result } = renderHook(() => useCameraCapture())
			expect(result.current.error).toBeNull()
		})

		it("capturedImage が null で開始する", () => {
			const { result } = renderHook(() => useCameraCapture())
			expect(result.current.capturedImage).toBeNull()
		})

		it("recognitionResult が null で開始する", () => {
			const { result } = renderHook(() => useCameraCapture())
			expect(result.current.recognitionResult).toBeNull()
		})

		it("videoRef が定義されている", () => {
			const { result } = renderHook(() => useCameraCapture())
			expect(result.current.videoRef).toBeDefined()
		})
	})

	describe("startCamera", () => {
		it("成功時にstatus が active になる", async () => {
			mockGetUserMedia.mockResolvedValue(mockStream)

			const { result } = renderHook(() => useCameraCapture())

			await act(async () => {
				await result.current.startCamera()
			})

			expect(result.current.status).toBe("active")
		})

		it("getUserMedia をビデオ制約付きで呼び出す", async () => {
			mockGetUserMedia.mockResolvedValue(mockStream)

			const { result } = renderHook(() => useCameraCapture())

			await act(async () => {
				await result.current.startCamera()
			})

			expect(mockGetUserMedia).toHaveBeenCalledWith({
				video: { facingMode: "environment" },
				audio: false,
			})
		})

		it("video要素がマウントされているときにstreamを接続する", async () => {
			mockGetUserMedia.mockResolvedValue(mockStream)

			const { result } = renderHook(() => useCameraCapture())

			// videoRef にモックvideo要素を設定（DOMマウント後のシミュレート）
			const mockVideo = document.createElement("video")
			Object.defineProperty(result.current.videoRef, "current", {
				value: mockVideo,
				writable: true,
			})

			await act(async () => {
				await result.current.startCamera()
			})

			// useEffectが実行されてsrcObjectが設定される
			expect(mockVideo.srcObject).toBe(mockStream)
		})

		it("権限拒否時に error を設定する", async () => {
			const permissionError = new DOMException("Permission denied", "NotAllowedError")
			mockGetUserMedia.mockRejectedValue(permissionError)

			const { result } = renderHook(() => useCameraCapture())

			await act(async () => {
				await result.current.startCamera()
			})

			expect(result.current.status).toBe("error")
			expect(result.current.error?.type).toBe("permission_denied")
		})

		it("デバイス未検出時に error を設定する", async () => {
			const notFoundError = new DOMException("Device not found", "NotFoundError")
			mockGetUserMedia.mockRejectedValue(notFoundError)

			const { result } = renderHook(() => useCameraCapture())

			await act(async () => {
				await result.current.startCamera()
			})

			expect(result.current.status).toBe("error")
			expect(result.current.error?.type).toBe("not_available")
		})
	})

	describe("captureImage", () => {
		it("status が preview になる", async () => {
			mockGetUserMedia.mockResolvedValue(mockStream)

			const { result } = renderHook(() => useCameraCapture())

			// videoRef にモックvideo要素を設定
			const mockVideo = document.createElement("video")
			Object.defineProperty(result.current.videoRef, "current", {
				value: mockVideo,
				writable: true,
			})

			await act(async () => {
				await result.current.startCamera()
			})

			act(() => {
				result.current.captureImage()
			})

			expect(result.current.status).toBe("preview")
		})

		it("capturedImage に Base64データが設定される", async () => {
			mockGetUserMedia.mockResolvedValue(mockStream)

			const { result } = renderHook(() => useCameraCapture())

			const mockVideo = document.createElement("video")
			Object.defineProperty(result.current.videoRef, "current", {
				value: mockVideo,
				writable: true,
			})

			await act(async () => {
				await result.current.startCamera()
			})

			act(() => {
				result.current.captureImage()
			})

			expect(result.current.capturedImage).toBe("data:image/jpeg;base64,mockBase64Data")
		})
	})

	describe("retake", () => {
		it("status が active に戻る", async () => {
			mockGetUserMedia.mockResolvedValue(mockStream)

			const { result } = renderHook(() => useCameraCapture())

			await act(async () => {
				await result.current.startCamera()
			})

			act(() => {
				result.current.captureImage()
			})

			await act(async () => {
				await result.current.retake()
			})

			expect(result.current.status).toBe("active")
		})

		it("capturedImage が null にリセットされる", async () => {
			mockGetUserMedia.mockResolvedValue(mockStream)

			const { result } = renderHook(() => useCameraCapture())

			await act(async () => {
				await result.current.startCamera()
			})

			act(() => {
				result.current.captureImage()
			})

			await act(async () => {
				await result.current.retake()
			})

			expect(result.current.capturedImage).toBeNull()
		})
	})

	describe("recognizeImage", () => {
		it("成功時に status が recognized になる", async () => {
			mockGetUserMedia.mockResolvedValue(mockStream)
			mockRecognizeImage.mockResolvedValue({
				recognizedText: "1 + 2 = ?",
				problemType: "math",
				confidence: 0.95,
			})

			const { result } = renderHook(() => useCameraCapture())

			const mockVideo = document.createElement("video")
			Object.defineProperty(result.current.videoRef, "current", {
				value: mockVideo,
				writable: true,
			})

			await act(async () => {
				await result.current.startCamera()
			})
			act(() => {
				result.current.captureImage()
			})
			await act(async () => {
				await result.current.recognizeImage()
			})

			expect(result.current.status).toBe("recognized")
			expect(result.current.recognitionResult).toEqual({
				recognizedText: "1 + 2 = ?",
				problemType: "math",
				confidence: 0.95,
			})
		})

		it("失敗時に status が error になる", async () => {
			mockGetUserMedia.mockResolvedValue(mockStream)
			mockRecognizeImage.mockRejectedValue(new Error("API Error"))

			const { result } = renderHook(() => useCameraCapture())

			const mockVideo = document.createElement("video")
			Object.defineProperty(result.current.videoRef, "current", {
				value: mockVideo,
				writable: true,
			})

			await act(async () => {
				await result.current.startCamera()
			})
			act(() => {
				result.current.captureImage()
			})
			await act(async () => {
				await result.current.recognizeImage()
			})

			expect(result.current.status).toBe("error")
			expect(result.current.error?.type).toBe("recognition_failed")
		})
	})

	describe("handleFileUpload", () => {
		it("ファイル読み込み後に status が preview になる", async () => {
			const { result } = renderHook(() => useCameraCapture())

			const mockFile = new File(["test"], "test.jpg", { type: "image/jpeg" })

			// FileReader モック - 通常の関数（コンストラクタ対応）
			const mockFileReader = {
				readAsDataURL: vi.fn(),
				onload: null as (() => void) | null,
				result: "data:image/jpeg;base64,fileData",
			}
			// biome-ignore lint/complexity/useArrowFunction: コンストラクタとして使うため通常の関数が必要
			globalThis.FileReader = function MockFileReader() {
				return mockFileReader
			} as unknown as typeof FileReader

			await act(async () => {
				result.current.handleFileUpload(mockFile)
				// FileReaderのonloadをシミュレート
				if (mockFileReader.onload) {
					mockFileReader.onload()
				}
			})

			expect(result.current.status).toBe("preview")
			expect(result.current.capturedImage).toBe("data:image/jpeg;base64,fileData")
		})
	})

	describe("reset", () => {
		it("すべての状態が初期値にリセットされる", async () => {
			mockGetUserMedia.mockResolvedValue(mockStream)

			const { result } = renderHook(() => useCameraCapture())

			await act(async () => {
				await result.current.startCamera()
			})

			act(() => {
				result.current.reset()
			})

			expect(result.current.status).toBe("initial")
			expect(result.current.error).toBeNull()
			expect(result.current.capturedImage).toBeNull()
			expect(result.current.recognitionResult).toBeNull()
		})

		it("メディアストリームトラックを停止する", async () => {
			mockGetUserMedia.mockResolvedValue(mockStream)

			const { result } = renderHook(() => useCameraCapture())

			await act(async () => {
				await result.current.startCamera()
			})

			act(() => {
				result.current.reset()
			})

			expect(mockStop).toHaveBeenCalled()
		})
	})

	describe("クリーンアップ", () => {
		it("アンマウント時にメディアストリームトラックを停止する", async () => {
			mockGetUserMedia.mockResolvedValue(mockStream)

			const { result, unmount } = renderHook(() => useCameraCapture())

			await act(async () => {
				await result.current.startCamera()
			})

			unmount()

			expect(mockStop).toHaveBeenCalled()
		})
	})
})
