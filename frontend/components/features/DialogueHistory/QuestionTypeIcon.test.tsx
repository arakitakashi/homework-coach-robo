import { render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"
import { QuestionTypeIcon } from "./QuestionTypeIcon"

describe("QuestionTypeIcon", () => {
	describe("understanding_check", () => {
		it("should display understanding check icon", () => {
			render(<QuestionTypeIcon type="understanding_check" />)

			const icon = screen.getByLabelText("質問タイプ: 理解確認")
			expect(icon).toBeInTheDocument()
		})

		it("should have green color for understanding check", () => {
			render(<QuestionTypeIcon type="understanding_check" />)

			const icon = screen.getByLabelText("質問タイプ: 理解確認")
			expect(icon).toBeInTheDocument()
			// Lucide icon は SVG として描画される
			const svg = icon.querySelector("svg")
			expect(svg).toBeInTheDocument()
		})
	})

	describe("thinking_guide", () => {
		it("should display thinking guide icon", () => {
			render(<QuestionTypeIcon type="thinking_guide" />)

			const icon = screen.getByLabelText("質問タイプ: 思考誘導")
			expect(icon).toBeInTheDocument()
		})

		it("should have yellow color for thinking guide", () => {
			render(<QuestionTypeIcon type="thinking_guide" />)

			const icon = screen.getByLabelText("質問タイプ: 思考誘導")
			expect(icon).toBeInTheDocument()
		})
	})

	describe("hint", () => {
		it("should display hint icon", () => {
			render(<QuestionTypeIcon type="hint" />)

			const icon = screen.getByLabelText("質問タイプ: ヒント")
			expect(icon).toBeInTheDocument()
		})

		it("should have blue color for hint", () => {
			render(<QuestionTypeIcon type="hint" />)

			const icon = screen.getByLabelText("質問タイプ: ヒント")
			expect(icon).toBeInTheDocument()
		})
	})

	describe("accessibility", () => {
		it("should have aria-label for each question type", () => {
			const { rerender } = render(<QuestionTypeIcon type="understanding_check" />)
			expect(screen.getByLabelText(/質問タイプ:/)).toBeInTheDocument()

			rerender(<QuestionTypeIcon type="thinking_guide" />)
			expect(screen.getByLabelText(/質問タイプ:/)).toBeInTheDocument()

			rerender(<QuestionTypeIcon type="hint" />)
			expect(screen.getByLabelText(/質問タイプ:/)).toBeInTheDocument()
		})

		it("should hide icon from screen readers with aria-hidden", () => {
			render(<QuestionTypeIcon type="understanding_check" />)

			const container = screen.getByLabelText("質問タイプ: 理解確認")
			const svg = container.querySelector("svg")
			expect(svg).toHaveAttribute("aria-hidden", "true")
		})
	})
})
