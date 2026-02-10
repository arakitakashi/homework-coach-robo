/**
 * ゲーミフィケーション atomsのテスト
 */

import { createStore } from "jotai"
import { describe, expect, it } from "vitest"
import type { Badge, PointEvent } from "@/types/gamification"
import {
	addPointsAtom,
	gamificationStateAtom,
	recentBadgeAtom,
	unlockBadgeAtom,
} from "./gamification"

describe("gamification atoms", () => {
	describe("gamificationStateAtom", () => {
		it("初期値が正しく設定されている", () => {
			const store = createStore()
			const state = store.get(gamificationStateAtom)

			expect(state.totalPoints).toBe(0)
			expect(state.sessionPoints).toBe(0)
			expect(state.level).toBe(1)
			expect(state.badges).toEqual([])
			expect(state.currentChapter.id).toBe("ch1")
			expect(state.pointHistory).toEqual([])
		})
	})

	describe("addPointsAtom", () => {
		it("ポイントを加算できる", () => {
			const store = createStore()

			const event: PointEvent = {
				points: 3,
				reason: "self_discovery",
				timestamp: Date.now(),
				problemId: "problem-1",
			}

			store.set(addPointsAtom, event)
			const state = store.get(gamificationStateAtom)

			expect(state.totalPoints).toBe(3)
			expect(state.sessionPoints).toBe(3)
			expect(state.pointHistory).toHaveLength(1)
			expect(state.pointHistory[0]).toEqual(event)
		})

		it("複数回のポイント加算が累積される", () => {
			const store = createStore()

			const event1: PointEvent = {
				points: 3,
				reason: "self_discovery",
				timestamp: Date.now(),
			}

			const event2: PointEvent = {
				points: 2,
				reason: "hint_discovery",
				timestamp: Date.now(),
			}

			store.set(addPointsAtom, event1)
			store.set(addPointsAtom, event2)

			const state = store.get(gamificationStateAtom)

			expect(state.totalPoints).toBe(5)
			expect(state.sessionPoints).toBe(5)
			expect(state.pointHistory).toHaveLength(2)
		})

		it("50ポイントごとにレベルアップする", () => {
			const store = createStore()

			// 0pt → Level 1
			expect(store.get(gamificationStateAtom).level).toBe(1)

			// 50pt → Level 2
			store.set(addPointsAtom, {
				points: 50,
				reason: "bonus_streak",
				timestamp: Date.now(),
			})
			expect(store.get(gamificationStateAtom).level).toBe(2)

			// 100pt (total) → Level 3
			store.set(addPointsAtom, {
				points: 50,
				reason: "bonus_streak",
				timestamp: Date.now(),
			})
			expect(store.get(gamificationStateAtom).level).toBe(3)
		})

		it("49ポイントではレベルアップしない", () => {
			const store = createStore()

			store.set(addPointsAtom, {
				points: 49,
				reason: "collaborative",
				timestamp: Date.now(),
			})

			expect(store.get(gamificationStateAtom).level).toBe(1)
		})
	})

	describe("unlockBadgeAtom", () => {
		it("バッジを獲得できる", () => {
			const store = createStore()

			const badge: Badge = {
				id: "first-clear",
				name: "初めての問題クリア",
				description: "初めて問題を解きました！",
				iconName: "Trophy",
				category: "achievement",
			}

			store.set(unlockBadgeAtom, badge)
			const state = store.get(gamificationStateAtom)

			expect(state.badges).toHaveLength(1)
			expect(state.badges[0].id).toBe("first-clear")
			expect(state.badges[0].unlockedAt).toBeDefined()
		})

		it("同じバッジは重複して獲得できない", () => {
			const store = createStore()

			const badge: Badge = {
				id: "first-clear",
				name: "初めての問題クリア",
				description: "初めて問題を解きました！",
				iconName: "Trophy",
				category: "achievement",
			}

			store.set(unlockBadgeAtom, badge)
			store.set(unlockBadgeAtom, badge) // 2回目

			const state = store.get(gamificationStateAtom)

			expect(state.badges).toHaveLength(1)
		})

		it("複数の異なるバッジを獲得できる", () => {
			const store = createStore()

			const badge1: Badge = {
				id: "first-clear",
				name: "初めての問題クリア",
				description: "初めて問題を解きました！",
				iconName: "Trophy",
				category: "achievement",
			}

			const badge2: Badge = {
				id: "streak-10",
				name: "10問連続正解",
				description: "10問連続で正解しました！",
				iconName: "Flame",
				category: "streak",
			}

			store.set(unlockBadgeAtom, badge1)
			store.set(unlockBadgeAtom, badge2)

			const state = store.get(gamificationStateAtom)

			expect(state.badges).toHaveLength(2)
		})
	})

	describe("recentBadgeAtom", () => {
		it("5秒以内に獲得したバッジを返す", () => {
			const store = createStore()

			const badge: Badge = {
				id: "first-clear",
				name: "初めての問題クリア",
				description: "初めて問題を解きました！",
				iconName: "Trophy",
				category: "achievement",
			}

			store.set(unlockBadgeAtom, badge)

			const recent = store.get(recentBadgeAtom)

			expect(recent).not.toBeNull()
			expect(recent?.id).toBe("first-clear")
		})

		it("5秒以上前に獲得したバッジは返さない", () => {
			const store = createStore()

			// 6秒前に獲得したバッジを手動で設定
			const oldBadge: Badge = {
				id: "old-badge",
				name: "古いバッジ",
				description: "6秒前に獲得",
				iconName: "Trophy",
				category: "achievement",
				unlockedAt: Date.now() - 6000,
			}

			store.set(gamificationStateAtom, {
				...store.get(gamificationStateAtom),
				badges: [oldBadge],
			})

			const recent = store.get(recentBadgeAtom)

			expect(recent).toBeNull()
		})

		it("複数のバッジがある場合、最新のものを返す", () => {
			const store = createStore()

			const now = Date.now()

			// 手動でunlockedAtを設定して時間差を作る
			const badge1: Badge = {
				id: "badge-1",
				name: "バッジ1",
				description: "最初のバッジ",
				iconName: "Trophy",
				category: "achievement",
				unlockedAt: now - 1000, // 1秒前
			}

			const badge2: Badge = {
				id: "badge-2",
				name: "バッジ2",
				description: "2つ目のバッジ",
				iconName: "Flame",
				category: "streak",
				unlockedAt: now, // 現在
			}

			// 手動でstateを設定
			store.set(gamificationStateAtom, {
				...store.get(gamificationStateAtom),
				badges: [badge1, badge2],
			})

			const recent = store.get(recentBadgeAtom)

			expect(recent?.id).toBe("badge-2")
		})
	})
})
