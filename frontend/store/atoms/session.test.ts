/**
 * セッション状態管理のJotai atoms テスト
 */

import { createStore } from "jotai"
import { describe, expect, it } from "vitest"
import {
	learningProgressAtom,
	selectedCharacterAtom,
	sessionAtom,
	sessionStatusAtom,
	totalPointsAtom,
} from "./session"

describe("session atoms", () => {
	describe("sessionAtom", () => {
		it("初期値が null である", () => {
			const store = createStore()
			const value = store.get(sessionAtom)
			expect(value).toBeNull()
		})
	})

	describe("sessionStatusAtom", () => {
		it("初期値が 'idle' である", () => {
			const store = createStore()
			const value = store.get(sessionStatusAtom)
			expect(value).toBe("idle")
		})
	})

	describe("selectedCharacterAtom", () => {
		it("初期値が 'robot' である", () => {
			const store = createStore()
			const value = store.get(selectedCharacterAtom)
			expect(value).toBe("robot")
		})
	})

	describe("learningProgressAtom", () => {
		it("初期値がゼロカウントである", () => {
			const store = createStore()
			const value = store.get(learningProgressAtom)
			expect(value).toEqual({
				selfDiscoveryCount: 0,
				hintDiscoveryCount: 0,
				togetherCount: 0,
			})
		})
	})

	describe("totalPointsAtom", () => {
		it("初期値が 0 である", () => {
			const store = createStore()
			const value = store.get(totalPointsAtom)
			expect(value).toBe(0)
		})

		it("学習進捗に応じて計算される", () => {
			const store = createStore()
			store.set(learningProgressAtom, {
				selfDiscoveryCount: 2,
				hintDiscoveryCount: 3,
				togetherCount: 1,
			})
			const value = store.get(totalPointsAtom)
			// 2 * 3 + 3 * 2 + 1 * 1 = 6 + 6 + 1 = 13
			expect(value).toBe(13)
		})
	})
})
