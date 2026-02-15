/**
 * ProblemSelector コンポーネントテスト
 *
 * 問題一覧表示、問題選択、撮り直しボタンの動作を検証する。
 */

import { fireEvent, render, screen } from "@testing-library/react"
import { beforeEach, describe, expect, it, vi } from "vitest"
import type { ProblemState } from "@/store/atoms/multiProblem"
import { ProblemSelector } from "./ProblemSelector"

const mockProblems: ProblemState[] = [
	{
		id: "p1",
		problem: { text: "1 + 2 = ?", type: "arithmetic", difficulty: 1 },
		status: "pending",
	},
	{
		id: "p2",
		problem: { text: "5 - 3 = ?", type: "arithmetic", difficulty: 1 },
		status: "completed",
	},
	{
		id: "p3",
		problem: {
			text: "つぎのかんじをよみましょう: 山",
			type: "kanji",
			difficulty: 1,
		},
		status: "in_progress",
	},
]

describe("ProblemSelector", () => {
	const mockOnProblemSelect = vi.fn()
	const mockOnRetake = vi.fn()

	beforeEach(() => {
		mockOnProblemSelect.mockClear()
		mockOnRetake.mockClear()
	})

	describe("問題一覧表示", () => {
		it("ヘッダーに問題数が表示される", () => {
			render(<ProblemSelector problems={mockProblems} onProblemSelect={mockOnProblemSelect} />)
			expect(screen.getByText(/もんだいが 3 こ みつかったよ/)).toBeInTheDocument()
		})

		it("全問題のテキストが表示される", () => {
			render(<ProblemSelector problems={mockProblems} onProblemSelect={mockOnProblemSelect} />)
			expect(screen.getByText("1 + 2 = ?")).toBeInTheDocument()
			expect(screen.getByText("5 - 3 = ?")).toBeInTheDocument()
			expect(screen.getByText("つぎのかんじをよみましょう: 山")).toBeInTheDocument()
		})

		it("問題番号が表示される", () => {
			render(<ProblemSelector problems={mockProblems} onProblemSelect={mockOnProblemSelect} />)
			expect(screen.getByText("1")).toBeInTheDocument()
			expect(screen.getByText("2")).toBeInTheDocument()
			expect(screen.getByText("3")).toBeInTheDocument()
		})
	})

	describe("ステータス表示", () => {
		it("完了済み問題にチェックマークが表示される", () => {
			render(<ProblemSelector problems={mockProblems} onProblemSelect={mockOnProblemSelect} />)
			// p2 は completed なのでチェックマーク表示
			const completedItem = screen.getByTestId("problem-item-p2")
			expect(completedItem).toHaveTextContent("✓")
		})
	})

	describe("問題選択", () => {
		it("問題をクリックするとonProblemSelectが呼ばれる", () => {
			render(<ProblemSelector problems={mockProblems} onProblemSelect={mockOnProblemSelect} />)
			fireEvent.click(screen.getByText("1 + 2 = ?"))
			expect(mockOnProblemSelect).toHaveBeenCalledWith(0)
		})

		it("2番目の問題をクリックするとインデックス1でonProblemSelectが呼ばれる", () => {
			render(<ProblemSelector problems={mockProblems} onProblemSelect={mockOnProblemSelect} />)
			fireEvent.click(screen.getByText("5 - 3 = ?"))
			expect(mockOnProblemSelect).toHaveBeenCalledWith(1)
		})
	})

	describe("撮り直しボタン", () => {
		it("onRetakeが渡された場合、とりなおすボタンが表示される", () => {
			render(
				<ProblemSelector
					problems={mockProblems}
					onProblemSelect={mockOnProblemSelect}
					onRetake={mockOnRetake}
				/>,
			)
			expect(screen.getByRole("button", { name: /とりなおす/ })).toBeInTheDocument()
		})

		it("onRetakeが渡されない場合、とりなおすボタンが表示されない", () => {
			render(<ProblemSelector problems={mockProblems} onProblemSelect={mockOnProblemSelect} />)
			expect(screen.queryByRole("button", { name: /とりなおす/ })).not.toBeInTheDocument()
		})

		it("とりなおすボタンをクリックするとonRetakeが呼ばれる", () => {
			render(
				<ProblemSelector
					problems={mockProblems}
					onProblemSelect={mockOnProblemSelect}
					onRetake={mockOnRetake}
				/>,
			)
			fireEvent.click(screen.getByRole("button", { name: /とりなおす/ }))
			expect(mockOnRetake).toHaveBeenCalledOnce()
		})
	})

	describe("1問のみの場合", () => {
		it("1問の場合もリストが表示される", () => {
			const singleProblem: ProblemState[] = [
				{
					id: "p1",
					problem: { text: "1 + 1 = ?", type: "arithmetic", difficulty: 1 },
					status: "pending",
				},
			]
			render(<ProblemSelector problems={singleProblem} onProblemSelect={mockOnProblemSelect} />)
			expect(screen.getByText(/もんだいが 1 こ みつかったよ/)).toBeInTheDocument()
			expect(screen.getByText("1 + 1 = ?")).toBeInTheDocument()
		})
	})

	describe("アクセシビリティ", () => {
		it("問題リストにrole=listが設定されている", () => {
			render(<ProblemSelector problems={mockProblems} onProblemSelect={mockOnProblemSelect} />)
			expect(screen.getByRole("list")).toBeInTheDocument()
		})

		it("各問題項目にrole=listitemが設定されている", () => {
			render(<ProblemSelector problems={mockProblems} onProblemSelect={mockOnProblemSelect} />)
			const items = screen.getAllByRole("listitem")
			expect(items).toHaveLength(3)
		})
	})
})
