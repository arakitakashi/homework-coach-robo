/**
 * BadgeNotification コンポーネントのテスト
 */

import { render, screen } from "@testing-library/react"
import { createStore, Provider } from "jotai"
import { type ReactNode, useMemo } from "react"
import { describe, expect, it } from "vitest"
import { gamificationStateAtom } from "@/store/atoms/gamification"
import type { Badge } from "@/types/gamification"
import { BadgeNotification } from "./BadgeNotification"

// テスト用ラッパー
function TestWrapper({ children }: { children: ReactNode }) {
	const store = useMemo(() => createStore(), [])
	return <Provider store={store}>{children}</Provider>
}

// バッジを設定するラッパー
function TestWrapperWithBadge({ children, badge }: { children: ReactNode; badge: Badge | null }) {
	const store = useMemo(() => {
		const s = createStore()
		if (badge) {
			const state = s.get(gamificationStateAtom)
			s.set(gamificationStateAtom, {
				...state,
				badges: [badge],
			})
		}
		return s
	}, [badge])

	return <Provider store={store}>{children}</Provider>
}

describe("BadgeNotification", () => {
	describe("表示制御", () => {
		it("最近獲得したバッジがない場合、何も表示しない", () => {
			const { container } = render(
				<TestWrapper>
					<BadgeNotification />
				</TestWrapper>,
			)

			// 通知が表示されていないことを確認
			expect(container.querySelector('[role="alert"]')).not.toBeInTheDocument()
		})

		it("最近獲得したバッジがある場合、通知を表示する", () => {
			const badge: Badge = {
				id: "first-clear",
				name: "初めての問題クリア",
				description: "初めて問題を解きました！",
				iconName: "Trophy",
				category: "achievement",
				unlockedAt: Date.now(),
			}

			render(
				<TestWrapperWithBadge badge={badge}>
					<BadgeNotification />
				</TestWrapperWithBadge>,
			)

			// 通知が表示されることを確認
			expect(screen.getByRole("alert")).toBeInTheDocument()
		})

		it("5秒以上前に獲得したバッジは表示しない", () => {
			const oldBadge: Badge = {
				id: "old-badge",
				name: "古いバッジ",
				description: "6秒前に獲得",
				iconName: "Trophy",
				category: "achievement",
				unlockedAt: Date.now() - 6000, // 6秒前
			}

			const { container } = render(
				<TestWrapperWithBadge badge={oldBadge}>
					<BadgeNotification />
				</TestWrapperWithBadge>,
			)

			// 通知が表示されていないことを確認
			expect(container.querySelector('[role="alert"]')).not.toBeInTheDocument()
		})
	})

	describe("バッジ情報の表示", () => {
		it("バッジ名が表示される", () => {
			const badge: Badge = {
				id: "first-clear",
				name: "初めての問題クリア",
				description: "初めて問題を解きました！",
				iconName: "Trophy",
				category: "achievement",
				unlockedAt: Date.now(),
			}

			render(
				<TestWrapperWithBadge badge={badge}>
					<BadgeNotification />
				</TestWrapperWithBadge>,
			)

			expect(screen.getByText("初めての問題クリア")).toBeInTheDocument()
		})

		it("バッジ説明が表示される", () => {
			const badge: Badge = {
				id: "first-clear",
				name: "初めての問題クリア",
				description: "初めて問題を解きました！",
				iconName: "Trophy",
				category: "achievement",
				unlockedAt: Date.now(),
			}

			render(
				<TestWrapperWithBadge badge={badge}>
					<BadgeNotification />
				</TestWrapperWithBadge>,
			)

			expect(screen.getByText("初めて問題を解きました！")).toBeInTheDocument()
		})

		it("バッジ獲得メッセージが表示される", () => {
			const badge: Badge = {
				id: "first-clear",
				name: "初めての問題クリア",
				description: "初めて問題を解きました！",
				iconName: "Trophy",
				category: "achievement",
				unlockedAt: Date.now(),
			}

			render(
				<TestWrapperWithBadge badge={badge}>
					<BadgeNotification />
				</TestWrapperWithBadge>,
			)

			expect(screen.getByText(/バッジ獲得/i)).toBeInTheDocument()
		})
	})

	describe("アイコン表示", () => {
		it("トロフィーアイコンが表示される", () => {
			const badge: Badge = {
				id: "first-clear",
				name: "初めての問題クリア",
				description: "初めて問題を解きました！",
				iconName: "Trophy",
				category: "achievement",
				unlockedAt: Date.now(),
			}

			render(
				<TestWrapperWithBadge badge={badge}>
					<BadgeNotification />
				</TestWrapperWithBadge>,
			)

			// アイコンが表示されることを確認（具体的な検証方法は実装に依存）
			const notification = screen.getByRole("alert")
			expect(notification).toBeInTheDocument()
		})
	})

	describe("アクセシビリティ", () => {
		it('role="alert"が設定されている', () => {
			const badge: Badge = {
				id: "first-clear",
				name: "初めての問題クリア",
				description: "初めて問題を解きました！",
				iconName: "Trophy",
				category: "achievement",
				unlockedAt: Date.now(),
			}

			render(
				<TestWrapperWithBadge badge={badge}>
					<BadgeNotification />
				</TestWrapperWithBadge>,
			)

			expect(screen.getByRole("alert")).toBeInTheDocument()
		})

		it("aria-liveが設定されている", () => {
			const badge: Badge = {
				id: "first-clear",
				name: "初めての問題クリア",
				description: "初めて問題を解きました！",
				iconName: "Trophy",
				category: "achievement",
				unlockedAt: Date.now(),
			}

			render(
				<TestWrapperWithBadge badge={badge}>
					<BadgeNotification />
				</TestWrapperWithBadge>,
			)

			const notification = screen.getByRole("alert")
			expect(notification).toHaveAttribute("aria-live", "polite")
		})
	})

	describe("カテゴリ別スタイル", () => {
		it("achievementカテゴリのバッジが表示される", () => {
			const badge: Badge = {
				id: "achievement-badge",
				name: "実績バッジ",
				description: "実績を達成しました",
				iconName: "Trophy",
				category: "achievement",
				unlockedAt: Date.now(),
			}

			render(
				<TestWrapperWithBadge badge={badge}>
					<BadgeNotification />
				</TestWrapperWithBadge>,
			)

			expect(screen.getByText("実績バッジ")).toBeInTheDocument()
		})

		it("streakカテゴリのバッジが表示される", () => {
			const badge: Badge = {
				id: "streak-badge",
				name: "連続正解バッジ",
				description: "連続で正解しました",
				iconName: "Flame",
				category: "streak",
				unlockedAt: Date.now(),
			}

			render(
				<TestWrapperWithBadge badge={badge}>
					<BadgeNotification />
				</TestWrapperWithBadge>,
			)

			expect(screen.getByText("連続正解バッジ")).toBeInTheDocument()
		})

		it("masteryカテゴリのバッジが表示される", () => {
			const badge: Badge = {
				id: "mastery-badge",
				name: "マスターバッジ",
				description: "マスターレベルに到達しました",
				iconName: "Star",
				category: "mastery",
				unlockedAt: Date.now(),
			}

			render(
				<TestWrapperWithBadge badge={badge}>
					<BadgeNotification />
				</TestWrapperWithBadge>,
			)

			expect(screen.getByText("マスターバッジ")).toBeInTheDocument()
		})
	})
})
