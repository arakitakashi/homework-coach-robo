import { render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"
import { ProfileSummary } from "./ProfileSummary"

describe("ProfileSummary", () => {
	describe("セッション数の表示", () => {
		it("セッション数を表示する", () => {
			render(<ProfileSummary totalSessions={5} totalProblemsSolved={12} />)
			expect(screen.getByText("5")).toBeInTheDocument()
			expect(screen.getByText("回のセッション")).toBeInTheDocument()
		})

		it("セッション数が0の場合でも表示する", () => {
			render(<ProfileSummary totalSessions={0} totalProblemsSolved={3} />)
			expect(screen.getAllByText("0")).toHaveLength(1)
		})
	})

	describe("解決問題数の表示", () => {
		it("解決した問題数を表示する", () => {
			render(<ProfileSummary totalSessions={3} totalProblemsSolved={8} />)
			expect(screen.getByText("8")).toBeInTheDocument()
			expect(screen.getByText("問クリア")).toBeInTheDocument()
		})
	})

	describe("アクセシビリティ", () => {
		it("学習サマリーのaria-labelを持つ", () => {
			render(<ProfileSummary totalSessions={5} totalProblemsSolved={12} />)
			expect(screen.getByLabelText("学習サマリー")).toBeInTheDocument()
		})
	})
})
