import { render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"
import type { ResponseAnalysis } from "@/types"
import { UnderstandingIndicator } from "./UnderstandingIndicator"

describe("UnderstandingIndicator", () => {
	describe("understanding level display", () => {
		it("should display understanding percentage", () => {
			const analysis: ResponseAnalysis = {
				understandingLevel: 0.8,
				isCorrectDirection: true,
				needsClarification: false,
				keyInsights: [],
			}

			render(<UnderstandingIndicator analysis={analysis} />)

			const indicator = screen.getByLabelText("理解度: 80%")
			expect(indicator).toBeInTheDocument()
			expect(screen.getByText("80%")).toBeInTheDocument()
		})

		it("should calculate percentage from decimal", () => {
			const analysis: ResponseAnalysis = {
				understandingLevel: 0.5,
				isCorrectDirection: true,
				needsClarification: false,
				keyInsights: [],
			}

			render(<UnderstandingIndicator analysis={analysis} />)

			expect(screen.getByText("50%")).toBeInTheDocument()
		})

		it("should round percentage to nearest integer", () => {
			const analysis: ResponseAnalysis = {
				understandingLevel: 0.756,
				isCorrectDirection: true,
				needsClarification: false,
				keyInsights: [],
			}

			render(<UnderstandingIndicator analysis={analysis} />)

			expect(screen.getByText("76%")).toBeInTheDocument()
		})
	})

	describe("direction indicator", () => {
		it("should show green color for correct direction", () => {
			const analysis: ResponseAnalysis = {
				understandingLevel: 0.8,
				isCorrectDirection: true,
				needsClarification: false,
				keyInsights: [],
			}

			const { container } = render(<UnderstandingIndicator analysis={analysis} />)

			const progressBar = container.querySelector(".bg-green-500")
			expect(progressBar).toBeInTheDocument()
		})

		it("should show yellow color for incorrect direction", () => {
			const analysis: ResponseAnalysis = {
				understandingLevel: 0.6,
				isCorrectDirection: false,
				needsClarification: false,
				keyInsights: [],
			}

			const { container } = render(<UnderstandingIndicator analysis={analysis} />)

			const progressBar = container.querySelector(".bg-yellow-500")
			expect(progressBar).toBeInTheDocument()
		})
	})

	describe("clarification flag", () => {
		it("should show question mark when clarification is needed", () => {
			const analysis: ResponseAnalysis = {
				understandingLevel: 0.5,
				isCorrectDirection: true,
				needsClarification: true,
				keyInsights: [],
			}

			render(<UnderstandingIndicator analysis={analysis} />)

			const clarificationFlag = screen.getByLabelText("明確化が必要")
			expect(clarificationFlag).toBeInTheDocument()
			expect(clarificationFlag).toHaveTextContent("?")
		})

		it("should not show question mark when clarification is not needed", () => {
			const analysis: ResponseAnalysis = {
				understandingLevel: 0.8,
				isCorrectDirection: true,
				needsClarification: false,
				keyInsights: [],
			}

			render(<UnderstandingIndicator analysis={analysis} />)

			const clarificationFlag = screen.queryByLabelText("明確化が必要")
			expect(clarificationFlag).not.toBeInTheDocument()
		})
	})

	describe("progress bar width", () => {
		it("should set progress bar width based on understanding level", () => {
			const analysis: ResponseAnalysis = {
				understandingLevel: 0.75,
				isCorrectDirection: true,
				needsClarification: false,
				keyInsights: [],
			}

			const { container } = render(<UnderstandingIndicator analysis={analysis} />)

			const progressBar = container.querySelector("[style*='width']")
			expect(progressBar).toHaveStyle({ width: "75%" })
		})

		it("should handle 0% understanding level", () => {
			const analysis: ResponseAnalysis = {
				understandingLevel: 0,
				isCorrectDirection: false,
				needsClarification: true,
				keyInsights: [],
			}

			const { container } = render(<UnderstandingIndicator analysis={analysis} />)

			expect(screen.getByText("0%")).toBeInTheDocument()
			const progressBar = container.querySelector("[style*='width']")
			expect(progressBar).toHaveStyle({ width: "0%" })
		})

		it("should handle 100% understanding level", () => {
			const analysis: ResponseAnalysis = {
				understandingLevel: 1.0,
				isCorrectDirection: true,
				needsClarification: false,
				keyInsights: [],
			}

			const { container } = render(<UnderstandingIndicator analysis={analysis} />)

			expect(screen.getByText("100%")).toBeInTheDocument()
			const progressBar = container.querySelector("[style*='width']")
			expect(progressBar).toHaveStyle({ width: "100%" })
		})
	})

	describe("accessibility", () => {
		it("should have aria-label with percentage", () => {
			const analysis: ResponseAnalysis = {
				understandingLevel: 0.65,
				isCorrectDirection: true,
				needsClarification: false,
				keyInsights: [],
			}

			render(<UnderstandingIndicator analysis={analysis} />)

			expect(screen.getByLabelText("理解度: 65%")).toBeInTheDocument()
		})
	})
})
