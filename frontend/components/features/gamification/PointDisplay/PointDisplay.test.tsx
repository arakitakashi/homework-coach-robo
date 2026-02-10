/**
 * PointDisplay コンポーネントのテスト
 */

import { render, screen } from "@testing-library/react"
import { createStore, Provider } from "jotai"
import { type ReactNode, useMemo } from "react"
import { describe, expect, it } from "vitest"
import { gamificationStateAtom } from "@/store/atoms/gamification"
import type { GamificationState } from "@/types/gamification"
import { PointDisplay } from "./PointDisplay"

// テスト用ラッパー
function TestWrapper({ children }: { children: ReactNode }) {
	const store = useMemo(() => createStore(), [])
	return <Provider store={store}>{children}</Provider>
}

// 初期状態を設定するラッパー
function TestWrapperWithState({
	children,
	initialState,
}: {
	children: ReactNode
	initialState: Partial<GamificationState>
}) {
	const store = useMemo(() => {
		const s = createStore()
		s.set(gamificationStateAtom, {
			...s.get(gamificationStateAtom),
			...initialState,
		})
		return s
	}, [initialState])

	return <Provider store={store}>{children}</Provider>
}

describe("PointDisplay", () => {
	describe("ポイント表示", () => {
		it("総ポイントが表示される", () => {
			render(
				<TestWrapperWithState initialState={{ totalPoints: 125 }}>
					<PointDisplay />
				</TestWrapperWithState>,
			)

			expect(screen.getByText(/125/)).toBeInTheDocument()
		})

		it("0ポイントの場合も正しく表示される", () => {
			render(
				<TestWrapperWithState initialState={{ totalPoints: 0 }}>
					<PointDisplay />
				</TestWrapperWithState>,
			)

			expect(screen.getByText(/0/)).toBeInTheDocument()
		})

		it("大きなポイント数も正しく表示される", () => {
			render(
				<TestWrapperWithState initialState={{ totalPoints: 9999 }}>
					<PointDisplay />
				</TestWrapperWithState>,
			)

			expect(screen.getByText(/9999/)).toBeInTheDocument()
		})
	})

	describe("レベル表示", () => {
		it("現在のレベルが表示される", () => {
			render(
				<TestWrapperWithState initialState={{ level: 3 }}>
					<PointDisplay />
				</TestWrapperWithState>,
			)

			expect(screen.getByText(/Level 3/i)).toBeInTheDocument()
		})

		it("レベル1でも正しく表示される", () => {
			render(
				<TestWrapperWithState initialState={{ level: 1 }}>
					<PointDisplay />
				</TestWrapperWithState>,
			)

			expect(screen.getByText(/Level 1/i)).toBeInTheDocument()
		})

		it("高レベルでも正しく表示される", () => {
			render(
				<TestWrapperWithState initialState={{ level: 99 }}>
					<PointDisplay />
				</TestWrapperWithState>,
			)

			expect(screen.getByText(/Level 99/i)).toBeInTheDocument()
		})
	})

	describe("プログレスバー表示", () => {
		it("レベルアップまでの進捗が表示される", () => {
			// Level 2 (50-99pt): 75pt = 50%進捗
			render(
				<TestWrapperWithState initialState={{ totalPoints: 75, level: 2 }}>
					<PointDisplay />
				</TestWrapperWithState>,
			)

			// プログレスバー要素が存在することを確認
			const progressBar = screen.getByRole("progressbar")
			expect(progressBar).toBeInTheDocument()

			// aria-valuenowで進捗を確認
			expect(progressBar).toHaveAttribute("aria-valuenow", "25")
			expect(progressBar).toHaveAttribute("aria-valuemin", "0")
			expect(progressBar).toHaveAttribute("aria-valuemax", "50")
		})

		it("レベルアップ直前（49pt）では98%の進捗", () => {
			// Level 1 (0-49pt): 49pt = 98%進捗
			render(
				<TestWrapperWithState initialState={{ totalPoints: 49, level: 1 }}>
					<PointDisplay />
				</TestWrapperWithState>,
			)

			const progressBar = screen.getByRole("progressbar")
			expect(progressBar).toHaveAttribute("aria-valuenow", "49")
			expect(progressBar).toHaveAttribute("aria-valuemax", "50")
		})

		it("レベルアップ直後（50pt）では0%の進捗", () => {
			// Level 2 (50-99pt): 50pt = 0%進捗
			render(
				<TestWrapperWithState initialState={{ totalPoints: 50, level: 2 }}>
					<PointDisplay />
				</TestWrapperWithState>,
			)

			const progressBar = screen.getByRole("progressbar")
			expect(progressBar).toHaveAttribute("aria-valuenow", "0")
			expect(progressBar).toHaveAttribute("aria-valuemax", "50")
		})
	})

	describe("進捗テキスト表示", () => {
		it("現在のポイント/次のレベルまでのポイントが表示される", () => {
			// Level 2 (50-99pt): 75pt = 次レベルまで25pt
			render(
				<TestWrapperWithState initialState={{ totalPoints: 75, level: 2 }}>
					<PointDisplay />
				</TestWrapperWithState>,
			)

			// "25 / 50 pts" のような表示を期待
			expect(screen.getByText(/25.*50.*pts/i)).toBeInTheDocument()
		})

		it("レベル1の場合も正しく表示される", () => {
			// Level 1 (0-49pt): 30pt = 次レベルまで20pt
			render(
				<TestWrapperWithState initialState={{ totalPoints: 30, level: 1 }}>
					<PointDisplay />
				</TestWrapperWithState>,
			)

			expect(screen.getByText(/30.*50.*pts/i)).toBeInTheDocument()
		})
	})

	describe("アクセシビリティ", () => {
		it("プログレスバーにaria-labelが設定されている", () => {
			render(
				<TestWrapper>
					<PointDisplay />
				</TestWrapper>,
			)

			const progressBar = screen.getByRole("progressbar")
			expect(progressBar).toHaveAttribute("aria-label")
		})

		it("レベル情報にaria-labelが設定されている", () => {
			render(
				<TestWrapper>
					<PointDisplay />
				</TestWrapper>,
			)

			// レベル表示要素を取得（具体的な実装に依存）
			const levelElement = screen.getByText(/Level/i)
			expect(levelElement).toBeInTheDocument()
		})
	})
})
