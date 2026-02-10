/**
 * StoryProgress コンポーネントのテスト
 */

import { render, screen } from "@testing-library/react"
import { createStore, Provider } from "jotai"
import { type ReactNode, useMemo } from "react"
import { describe, expect, it } from "vitest"
import { gamificationStateAtom } from "@/store/atoms/gamification"
import type { StoryChapter } from "@/types/gamification"
import { StoryProgress } from "./StoryProgress"

// テスト用ラッパー
function _TestWrapper({ children }: { children: ReactNode }) {
	const store = useMemo(() => createStore(), [])
	return <Provider store={store}>{children}</Provider>
}

// チャプター情報を設定するラッパー
function TestWrapperWithChapter({
	children,
	chapter,
	totalPoints,
}: {
	children: ReactNode
	chapter: StoryChapter
	totalPoints: number
}) {
	const store = useMemo(() => {
		const s = createStore()
		const state = s.get(gamificationStateAtom)
		s.set(gamificationStateAtom, {
			...state,
			currentChapter: chapter,
			totalPoints,
		})
		return s
	}, [chapter, totalPoints])

	return <Provider store={store}>{children}</Provider>
}

describe("StoryProgress", () => {
	describe("チャプター情報の表示", () => {
		it("チャプタータイトルが表示される", () => {
			const chapter: StoryChapter = {
				id: "ch1",
				title: "冒険の始まり",
				description: "ロボと一緒に最初の問題に挑戦しよう！",
				requiredPoints: 10,
				completed: false,
			}

			render(
				<TestWrapperWithChapter chapter={chapter} totalPoints={5}>
					<StoryProgress />
				</TestWrapperWithChapter>,
			)

			expect(screen.getByText(/冒険の始まり/)).toBeInTheDocument()
		})

		it("チャプター説明が表示される", () => {
			const chapter: StoryChapter = {
				id: "ch1",
				title: "冒険の始まり",
				description: "ロボと一緒に最初の問題に挑戦しよう！",
				requiredPoints: 10,
				completed: false,
			}

			render(
				<TestWrapperWithChapter chapter={chapter} totalPoints={5}>
					<StoryProgress />
				</TestWrapperWithChapter>,
			)

			expect(screen.getByText("ロボと一緒に最初の問題に挑戦しよう！")).toBeInTheDocument()
		})

		it("チャプター番号が表示される", () => {
			const chapter: StoryChapter = {
				id: "ch1",
				title: "冒険の始まり",
				description: "ロボと一緒に最初の問題に挑戦しよう！",
				requiredPoints: 10,
				completed: false,
			}

			render(
				<TestWrapperWithChapter chapter={chapter} totalPoints={5}>
					<StoryProgress />
				</TestWrapperWithChapter>,
			)

			expect(screen.getByText(/Chapter 1/i)).toBeInTheDocument()
		})
	})

	describe("進行度プログレスバーの表示", () => {
		it("進行度が正しく表示される", () => {
			const chapter: StoryChapter = {
				id: "ch1",
				title: "冒険の始まり",
				description: "ロボと一緒に最初の問題に挑戦しよう！",
				requiredPoints: 10,
				completed: false,
			}

			render(
				<TestWrapperWithChapter chapter={chapter} totalPoints={5}>
					<StoryProgress />
				</TestWrapperWithChapter>,
			)

			const progressBar = screen.getByRole("progressbar")
			expect(progressBar).toBeInTheDocument()
			expect(progressBar).toHaveAttribute("aria-valuenow", "5")
			expect(progressBar).toHaveAttribute("aria-valuemax", "10")
		})

		it("完了直前（9/10）の進行度が表示される", () => {
			const chapter: StoryChapter = {
				id: "ch1",
				title: "冒険の始まり",
				description: "ロボと一緒に最初の問題に挑戦しよう！",
				requiredPoints: 10,
				completed: false,
			}

			render(
				<TestWrapperWithChapter chapter={chapter} totalPoints={9}>
					<StoryProgress />
				</TestWrapperWithChapter>,
			)

			const progressBar = screen.getByRole("progressbar")
			expect(progressBar).toHaveAttribute("aria-valuenow", "9")
			expect(progressBar).toHaveAttribute("aria-valuemax", "10")
		})

		it("完了後（10/10）の進行度が表示される", () => {
			const chapter: StoryChapter = {
				id: "ch1",
				title: "冒険の始まり",
				description: "ロボと一緒に最初の問題に挑戦しよう！",
				requiredPoints: 10,
				completed: true,
			}

			render(
				<TestWrapperWithChapter chapter={chapter} totalPoints={10}>
					<StoryProgress />
				</TestWrapperWithChapter>,
			)

			const progressBar = screen.getByRole("progressbar")
			expect(progressBar).toHaveAttribute("aria-valuenow", "10")
			expect(progressBar).toHaveAttribute("aria-valuemax", "10")
		})
	})

	describe("進捗テキストの表示", () => {
		it("現在のポイント/必要なポイントが表示される", () => {
			const chapter: StoryChapter = {
				id: "ch1",
				title: "冒険の始まり",
				description: "ロボと一緒に最初の問題に挑戦しよう！",
				requiredPoints: 10,
				completed: false,
			}

			render(
				<TestWrapperWithChapter chapter={chapter} totalPoints={5}>
					<StoryProgress />
				</TestWrapperWithChapter>,
			)

			expect(screen.getByText(/5.*10.*pts/i)).toBeInTheDocument()
		})

		it("0ポイントの場合も正しく表示される", () => {
			const chapter: StoryChapter = {
				id: "ch1",
				title: "冒険の始まり",
				description: "ロボと一緒に最初の問題に挑戦しよう！",
				requiredPoints: 10,
				completed: false,
			}

			render(
				<TestWrapperWithChapter chapter={chapter} totalPoints={0}>
					<StoryProgress />
				</TestWrapperWithChapter>,
			)

			expect(screen.getByText(/0.*10.*pts/i)).toBeInTheDocument()
		})
	})

	describe("チャプター完了状態の表示", () => {
		it("未完了のチャプターには完了マークが表示されない", () => {
			const chapter: StoryChapter = {
				id: "ch1",
				title: "冒険の始まり",
				description: "ロボと一緒に最初の問題に挑戦しよう！",
				requiredPoints: 10,
				completed: false,
			}

			render(
				<TestWrapperWithChapter chapter={chapter} totalPoints={5}>
					<StoryProgress />
				</TestWrapperWithChapter>,
			)

			expect(screen.queryByText(/完了/i)).not.toBeInTheDocument()
		})

		it("完了したチャプターには完了マークが表示される", () => {
			const chapter: StoryChapter = {
				id: "ch1",
				title: "冒険の始まり",
				description: "ロボと一緒に最初の問題に挑戦しよう！",
				requiredPoints: 10,
				completed: true,
			}

			render(
				<TestWrapperWithChapter chapter={chapter} totalPoints={15}>
					<StoryProgress />
				</TestWrapperWithChapter>,
			)

			expect(screen.getByText(/完了/i)).toBeInTheDocument()
		})
	})

	describe("アクセシビリティ", () => {
		it("プログレスバーにaria-labelが設定されている", () => {
			const chapter: StoryChapter = {
				id: "ch1",
				title: "冒険の始まり",
				description: "ロボと一緒に最初の問題に挑戦しよう！",
				requiredPoints: 10,
				completed: false,
			}

			render(
				<TestWrapperWithChapter chapter={chapter} totalPoints={5}>
					<StoryProgress />
				</TestWrapperWithChapter>,
			)

			const progressBar = screen.getByRole("progressbar")
			expect(progressBar).toHaveAttribute("aria-label")
		})

		it("チャプター情報にセクションroleが設定されている", () => {
			const chapter: StoryChapter = {
				id: "ch1",
				title: "冒険の始まり",
				description: "ロボと一緒に最初の問題に挑戦しよう！",
				requiredPoints: 10,
				completed: false,
			}

			render(
				<TestWrapperWithChapter chapter={chapter} totalPoints={5}>
					<StoryProgress />
				</TestWrapperWithChapter>,
			)

			expect(screen.getByRole("region")).toBeInTheDocument()
		})
	})

	describe("異なるチャプターの表示", () => {
		it("Chapter 2が正しく表示される", () => {
			const chapter: StoryChapter = {
				id: "ch2",
				title: "新たな挑戦",
				description: "次のステージに進もう！",
				requiredPoints: 20,
				completed: false,
			}

			render(
				<TestWrapperWithChapter chapter={chapter} totalPoints={15}>
					<StoryProgress />
				</TestWrapperWithChapter>,
			)

			expect(screen.getByText(/Chapter 2/i)).toBeInTheDocument()
			expect(screen.getByText(/新たな挑戦/)).toBeInTheDocument()
		})

		it("高いチャプター番号も正しく表示される", () => {
			const chapter: StoryChapter = {
				id: "ch10",
				title: "最終章",
				description: "ついに最後の挑戦だ！",
				requiredPoints: 100,
				completed: false,
			}

			render(
				<TestWrapperWithChapter chapter={chapter} totalPoints={90}>
					<StoryProgress />
				</TestWrapperWithChapter>,
			)

			expect(screen.getByText(/Chapter 10/i)).toBeInTheDocument()
		})
	})
})
