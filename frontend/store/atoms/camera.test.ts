/**
 * カメラ・画像認識 atoms のテスト
 */

import { createStore } from "jotai"
import { describe, expect, it } from "vitest"
import { cameraRecognitionAtom, cameraStatusAtom, capturedImageAtom, inputModeAtom } from "./camera"

describe("camera atoms", () => {
	describe("inputModeAtom", () => {
		it("初期値はnull", () => {
			const store = createStore()
			const mode = store.get(inputModeAtom)
			expect(mode).toBeNull()
		})

		it("voiceモードに更新できる", () => {
			const store = createStore()
			store.set(inputModeAtom, "voice")
			const mode = store.get(inputModeAtom)
			expect(mode).toBe("voice")
		})

		it("imageモードに更新できる", () => {
			const store = createStore()
			store.set(inputModeAtom, "image")
			const mode = store.get(inputModeAtom)
			expect(mode).toBe("image")
		})

		it("nullに戻せる", () => {
			const store = createStore()
			store.set(inputModeAtom, "voice")
			store.set(inputModeAtom, null)
			const mode = store.get(inputModeAtom)
			expect(mode).toBeNull()
		})
	})

	describe("cameraStatusAtom", () => {
		it("初期値はinitial", () => {
			const store = createStore()
			const status = store.get(cameraStatusAtom)
			expect(status).toBe("initial")
		})
	})

	describe("cameraRecognitionAtom", () => {
		it("初期値はnull", () => {
			const store = createStore()
			const recognition = store.get(cameraRecognitionAtom)
			expect(recognition).toBeNull()
		})

		it("画像認識結果を保存できる", () => {
			const store = createStore()
			const result = {
				recognizedText: "3 + 5 = ?",
				problemType: "math",
				confidence: 0.95,
				extractedExpression: "3 + 5",
			}
			store.set(cameraRecognitionAtom, result)
			const recognition = store.get(cameraRecognitionAtom)
			expect(recognition).toEqual(result)
		})
	})

	describe("capturedImageAtom", () => {
		it("初期値はnull", () => {
			const store = createStore()
			const image = store.get(capturedImageAtom)
			expect(image).toBeNull()
		})

		it("Base64画像データを保存できる", () => {
			const store = createStore()
			const imageData = "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
			store.set(capturedImageAtom, imageData)
			const image = store.get(capturedImageAtom)
			expect(image).toBe(imageData)
		})
	})
})
