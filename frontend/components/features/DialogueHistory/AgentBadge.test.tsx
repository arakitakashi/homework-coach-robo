import { render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"
import { AgentBadge } from "./AgentBadge"

describe("AgentBadge", () => {
	describe("agent types", () => {
		it("should display router agent", () => {
			render(<AgentBadge agent="router" />)

			const badge = screen.getByLabelText("エージェント: ルーター")
			expect(badge).toBeInTheDocument()
			expect(badge).toHaveTextContent("ルーター")
		})

		it("should display math coach agent", () => {
			render(<AgentBadge agent="math_coach" />)

			const badge = screen.getByLabelText("エージェント: 算数")
			expect(badge).toBeInTheDocument()
			expect(badge).toHaveTextContent("算数")
		})

		it("should display japanese coach agent", () => {
			render(<AgentBadge agent="japanese_coach" />)

			const badge = screen.getByLabelText("エージェント: 国語")
			expect(badge).toBeInTheDocument()
			expect(badge).toHaveTextContent("国語")
		})

		it("should display encouragement agent", () => {
			render(<AgentBadge agent="encouragement" />)

			const badge = screen.getByLabelText("エージェント: 励まし")
			expect(badge).toBeInTheDocument()
			expect(badge).toHaveTextContent("励まし")
		})

		it("should display review agent", () => {
			render(<AgentBadge agent="review" />)

			const badge = screen.getByLabelText("エージェント: 振り返り")
			expect(badge).toBeInTheDocument()
			expect(badge).toHaveTextContent("振り返り")
		})
	})

	describe("styling", () => {
		it("should have badge styling", () => {
			render(<AgentBadge agent="math_coach" />)

			const badge = screen.getByLabelText("エージェント: 算数")
			expect(badge).toHaveClass("rounded-full")
			expect(badge).toHaveClass("px-2")
			expect(badge).toHaveClass("py-0.5")
		})

		it("should have blue color scheme", () => {
			render(<AgentBadge agent="math_coach" />)

			const badge = screen.getByLabelText("エージェント: 算数")
			expect(badge).toHaveClass("bg-blue-100")
			expect(badge).toHaveClass("text-blue-700")
		})
	})

	describe("accessibility", () => {
		it("should have aria-label for each agent type", () => {
			const agents = ["router", "math_coach", "japanese_coach", "encouragement", "review"] as const

			for (const agent of agents) {
				const { unmount } = render(<AgentBadge agent={agent} />)
				expect(screen.getByLabelText(/エージェント:/)).toBeInTheDocument()
				unmount()
			}
		})
	})
})
