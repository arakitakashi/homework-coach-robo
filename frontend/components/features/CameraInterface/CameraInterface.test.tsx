/**
 * CameraInterface コンポーネントテスト
 *
 * 6状態（initial/active/preview/processing/recognized/error）の
 * UIレンダリングとインタラクションを検証する。
 * useCameraCaptureフックをモックして各状態を直接テストする。
 */

import { fireEvent, render, screen } from "@testing-library/react"
import { beforeEach, describe, expect, it, vi } from "vitest"
import { CameraInterface } from "./CameraInterface"
import type { UseCameraCaptureReturn } from "./useCameraCapture"

// useCameraCapture フックのモック
const mockStartCamera = vi.fn()
const mockCaptureImage = vi.fn()
const mockRetake = vi.fn()
const mockRecognizeImage = vi.fn()
const mockReset = vi.fn()
const mockHandleFileUpload = vi.fn()

const defaultMockReturn: UseCameraCaptureReturn = {
	status: "initial",
	error: null,
	capturedImage: null,
	recognitionResult: null,
	startCamera: mockStartCamera,
	captureImage: mockCaptureImage,
	retake: mockRetake,
	recognizeImage: mockRecognizeImage,
	reset: mockReset,
	handleFileUpload: mockHandleFileUpload,
	videoRef: { current: null },
}

let mockHookReturn = { ...defaultMockReturn }

vi.mock("./useCameraCapture", () => ({
	useCameraCapture: () => mockHookReturn,
}))

describe("CameraInterface", () => {
	beforeEach(() => {
		mockStartCamera.mockClear()
		mockCaptureImage.mockClear()
		mockRetake.mockClear()
		mockRecognizeImage.mockClear()
		mockReset.mockClear()
		mockHandleFileUpload.mockClear()
		mockHookReturn = { ...defaultMockReturn }
	})

	describe("initial 状態", () => {
		it("カメラ起動ボタンが表示される", () => {
			render(<CameraInterface />)
			expect(screen.getByRole("button", { name: /カメラをつかう/i })).toBeInTheDocument()
		})

		it("ファイルアップロードの入力が表示される", () => {
			render(<CameraInterface />)
			expect(screen.getByLabelText(/しゃしんをえらぶ/i)).toBeInTheDocument()
		})

		it("カメラ起動ボタンをクリックすると startCamera が呼ばれる", () => {
			render(<CameraInterface />)
			fireEvent.click(screen.getByRole("button", { name: /カメラをつかう/i }))
			expect(mockStartCamera).toHaveBeenCalledOnce()
		})

		it("ファイル選択すると handleFileUpload が呼ばれる", () => {
			render(<CameraInterface />)
			const input = screen.getByLabelText(/しゃしんをえらぶ/i)
			const file = new File(["test"], "test.jpg", { type: "image/jpeg" })
			fireEvent.change(input, { target: { files: [file] } })
			expect(mockHandleFileUpload).toHaveBeenCalledWith(file)
		})
	})

	describe("active 状態", () => {
		beforeEach(() => {
			mockHookReturn = { ...defaultMockReturn, status: "active" }
		})

		it("撮影ボタンが表示される", () => {
			render(<CameraInterface />)
			expect(screen.getByRole("button", { name: /しゃしんをとる/i })).toBeInTheDocument()
		})

		it("撮影ボタンをクリックすると captureImage が呼ばれる", () => {
			render(<CameraInterface />)
			fireEvent.click(screen.getByRole("button", { name: /しゃしんをとる/i }))
			expect(mockCaptureImage).toHaveBeenCalledOnce()
		})
	})

	describe("preview 状態", () => {
		beforeEach(() => {
			mockHookReturn = {
				...defaultMockReturn,
				status: "preview",
				capturedImage: "data:image/jpeg;base64,test",
			}
		})

		it("プレビュー画像が表示される", () => {
			render(<CameraInterface />)
			const img = screen.getByRole("img", { name: /さつえいしたしゃしん/i })
			expect(img).toBeInTheDocument()
			expect(img).toHaveAttribute("src", "data:image/jpeg;base64,test")
		})

		it("撮り直すボタンが表示される", () => {
			render(<CameraInterface />)
			expect(screen.getByRole("button", { name: /とりなおす/i })).toBeInTheDocument()
		})

		it("認識するボタンが表示される", () => {
			render(<CameraInterface />)
			expect(screen.getByRole("button", { name: /もんだいをよみとる/i })).toBeInTheDocument()
		})

		it("撮り直すボタンをクリックすると retake が呼ばれる", () => {
			render(<CameraInterface />)
			fireEvent.click(screen.getByRole("button", { name: /とりなおす/i }))
			expect(mockRetake).toHaveBeenCalledOnce()
		})

		it("認識するボタンをクリックすると recognizeImage が呼ばれる", () => {
			render(<CameraInterface />)
			fireEvent.click(screen.getByRole("button", { name: /もんだいをよみとる/i }))
			expect(mockRecognizeImage).toHaveBeenCalledOnce()
		})
	})

	describe("processing 状態", () => {
		beforeEach(() => {
			mockHookReturn = { ...defaultMockReturn, status: "processing" }
		})

		it("処理中メッセージが表示される", () => {
			render(<CameraInterface />)
			expect(screen.getByText(/よみとりちゅう/i)).toBeInTheDocument()
		})
	})

	describe("recognized 状態", () => {
		beforeEach(() => {
			mockHookReturn = {
				...defaultMockReturn,
				status: "recognized",
				recognitionResult: {
					recognizedText: "1 + 2 = ?",
					problemType: "math",
					confidence: 0.95,
				},
			}
		})

		it("認識結果の問題文が表示される", () => {
			render(<CameraInterface />)
			expect(screen.getByText("1 + 2 = ?")).toBeInTheDocument()
		})

		it("撮り直すボタンが表示される", () => {
			render(<CameraInterface />)
			expect(screen.getByRole("button", { name: /とりなおす/i })).toBeInTheDocument()
		})

		it("onProblemRecognized コールバックが呼ばれる", () => {
			const mockCallback = vi.fn()
			render(<CameraInterface onProblemRecognized={mockCallback} />)

			// コンポーネントが recognized 状態でレンダリングされた際にコールバック確認
			// コールバックは「このもんだいでべんきょうする」ボタン経由で呼ばれる
			const confirmButton = screen.getByRole("button", { name: /このもんだいでべんきょうする/i })
			fireEvent.click(confirmButton)

			expect(mockCallback).toHaveBeenCalledWith("1 + 2 = ?", {
				recognizedText: "1 + 2 = ?",
				problemType: "math",
				confidence: 0.95,
			})
		})
	})

	describe("error 状態", () => {
		beforeEach(() => {
			mockHookReturn = {
				...defaultMockReturn,
				status: "error",
				error: {
					type: "permission_denied",
					message: "カメラがつかえないよ。せってい をかくにんしてね",
				},
			}
		})

		it("エラーメッセージが表示される", () => {
			render(<CameraInterface />)
			expect(
				screen.getByText("カメラがつかえないよ。せってい をかくにんしてね"),
			).toBeInTheDocument()
		})

		it("ファイルアップロードのフォールバックが表示される", () => {
			render(<CameraInterface />)
			expect(screen.getByLabelText(/しゃしんをえらぶ/i)).toBeInTheDocument()
		})

		it("やりなおすボタンが表示される", () => {
			render(<CameraInterface />)
			expect(screen.getByRole("button", { name: /やりなおす/i })).toBeInTheDocument()
		})

		it("やりなおすボタンをクリックすると reset が呼ばれる", () => {
			render(<CameraInterface />)
			fireEvent.click(screen.getByRole("button", { name: /やりなおす/i }))
			expect(mockReset).toHaveBeenCalledOnce()
		})
	})

	describe("アクセシビリティ", () => {
		it("カメラ起動ボタンに aria-label がある", () => {
			render(<CameraInterface />)
			const button = screen.getByRole("button", { name: /カメラをつかう/i })
			expect(button).toBeInTheDocument()
		})

		it("ファイル入力にラベルが紐づいている", () => {
			render(<CameraInterface />)
			const input = screen.getByLabelText(/しゃしんをえらぶ/i)
			expect(input).toHaveAttribute("type", "file")
			expect(input).toHaveAttribute("accept", "image/*")
		})
	})
})
