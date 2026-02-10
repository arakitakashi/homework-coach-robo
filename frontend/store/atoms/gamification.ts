/**
 * ゲーミフィケーション要素の状態管理（Jotai）
 */

import { atom } from "jotai"
import type { Badge, GamificationState, PointEvent } from "@/types/gamification"

/**
 * ゲーミフィケーション状態のatom
 */
export const gamificationStateAtom = atom<GamificationState>({
	totalPoints: 0,
	sessionPoints: 0,
	level: 1,
	badges: [],
	currentChapter: {
		id: "ch1",
		title: "冒険の始まり",
		description: "ロボと一緒に最初の問題に挑戦しよう！",
		requiredPoints: 10,
		completed: false,
	},
	pointHistory: [],
})

/**
 * ポイント追加アクション（write-only atom）
 */
export const addPointsAtom = atom(null, (get, set, event: PointEvent) => {
	const state = get(gamificationStateAtom)
	const newTotalPoints = state.totalPoints + event.points
	const newSessionPoints = state.sessionPoints + event.points

	// レベル計算: 50ポイントごとにレベルアップ
	const newLevel = Math.floor(newTotalPoints / 50) + 1

	set(gamificationStateAtom, {
		...state,
		totalPoints: newTotalPoints,
		sessionPoints: newSessionPoints,
		level: newLevel,
		pointHistory: [...state.pointHistory, event],
	})
})

/**
 * バッジ獲得アクション（write-only atom）
 */
export const unlockBadgeAtom = atom(null, (get, set, badge: Badge) => {
	const state = get(gamificationStateAtom)

	// 既に獲得済みかチェック
	const alreadyUnlocked = state.badges.some((b) => b.id === badge.id)

	if (!alreadyUnlocked) {
		set(gamificationStateAtom, {
			...state,
			badges: [...state.badges, { ...badge, unlockedAt: Date.now() }],
		})
	}
})

/**
 * 最近獲得したバッジ（5秒以内）を取得するatom
 */
export const recentBadgeAtom = atom<Badge | null>((get) => {
	const state = get(gamificationStateAtom)
	const now = Date.now()

	// 5秒以内に獲得したバッジを取得
	const recent = state.badges
		.filter((b) => b.unlockedAt && now - b.unlockedAt < 5000)
		.sort((a, b) => (b.unlockedAt || 0) - (a.unlockedAt || 0))[0]

	return recent || null
})
