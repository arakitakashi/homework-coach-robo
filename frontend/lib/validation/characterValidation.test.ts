import { describe, expect, it } from "vitest"
import { isValidCharacter } from "./characterValidation"

describe("characterValidation", () => {
	describe("isValidCharacter", () => {
		it("有効なキャラクター 'robot' の場合trueを返す", () => {
			expect(isValidCharacter("robot")).toBe(true)
		})

		it("有効なキャラクター 'wizard' の場合trueを返す", () => {
			expect(isValidCharacter("wizard")).toBe(true)
		})

		it("有効なキャラクター 'astronaut' の場合trueを返す", () => {
			expect(isValidCharacter("astronaut")).toBe(true)
		})

		it("有効なキャラクター 'animal' の場合trueを返す", () => {
			expect(isValidCharacter("animal")).toBe(true)
		})

		it("無効なキャラクター 'invalid' の場合falseを返す", () => {
			expect(isValidCharacter("invalid")).toBe(false)
		})

		it("undefinedの場合falseを返す", () => {
			expect(isValidCharacter(undefined)).toBe(false)
		})

		it("空文字列の場合falseを返す", () => {
			expect(isValidCharacter("")).toBe(false)
		})

		it("大文字の場合falseを返す", () => {
			expect(isValidCharacter("ROBOT")).toBe(false)
		})
	})
})
