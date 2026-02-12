import { render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"
import type { DialogueTurn } from "@/types"
import { DialogueMetadataFooter } from "./DialogueMetadataFooter"

describe("DialogueMetadataFooter", () => {
	const baseTurn: DialogueTurn = {
		id: "turn-1",
		speaker: "child",
		text: "テスト対話",
		timestamp: new Date(),
	}

	describe("response analysis display", () => {
		it("should display understanding indicator when responseAnalysis is present", () => {
			const turn: DialogueTurn = {
				...baseTurn,
				responseAnalysis: {
					understandingLevel: 0.75,
					isCorrectDirection: true,
					needsClarification: false,
					keyInsights: [],
				},
			}

			render(<DialogueMetadataFooter turn={turn} />)

			expect(screen.getByLabelText("理解度: 75%")).toBeInTheDocument()
		})

		it("should not display understanding indicator when responseAnalysis is absent", () => {
			render(<DialogueMetadataFooter turn={baseTurn} />)

			expect(screen.queryByLabelText(/理解度:/)).not.toBeInTheDocument()
		})
	})

	describe("tool executions display", () => {
		it("should display tool badges when toolExecutions is present", () => {
			const turn: DialogueTurn = {
				...baseTurn,
				toolExecutions: [
					{
						toolName: "calculate_tool",
						status: "completed",
						timestamp: new Date(),
					},
				],
			}

			render(<DialogueMetadataFooter turn={turn} />)

			expect(screen.getByText("けいさん")).toBeInTheDocument()
		})

		it("should not display tool badges when toolExecutions is empty", () => {
			const turn: DialogueTurn = {
				...baseTurn,
				toolExecutions: [],
			}

			render(<DialogueMetadataFooter turn={turn} />)

			expect(screen.queryByText("けいさん")).not.toBeInTheDocument()
		})

		it("should not display tool badges when toolExecutions is absent", () => {
			render(<DialogueMetadataFooter turn={baseTurn} />)

			expect(screen.queryByText("けいさん")).not.toBeInTheDocument()
		})
	})

	describe("multiple metadata", () => {
		it("should display both responseAnalysis and toolExecutions when both are present", () => {
			const turn: DialogueTurn = {
				...baseTurn,
				responseAnalysis: {
					understandingLevel: 0.6,
					isCorrectDirection: false,
					needsClarification: true,
					keyInsights: [],
				},
				toolExecutions: [
					{
						toolName: "manage_hint_tool",
						status: "completed",
						timestamp: new Date(),
					},
					{
						toolName: "record_progress_tool",
						status: "running",
						timestamp: new Date("2024-01-01T12:01:00"),
					},
				],
			}

			render(<DialogueMetadataFooter turn={turn} />)

			expect(screen.getByLabelText("理解度: 60%")).toBeInTheDocument()
			expect(screen.getByText("ヒント")).toBeInTheDocument()
			expect(screen.getByText("きろく")).toBeInTheDocument()
		})
	})

	describe("layout", () => {
		it("should arrange items horizontally with gap", () => {
			const turn: DialogueTurn = {
				...baseTurn,
				responseAnalysis: {
					understandingLevel: 0.8,
					isCorrectDirection: true,
					needsClarification: false,
					keyInsights: [],
				},
			}

			const { container } = render(<DialogueMetadataFooter turn={turn} />)

			const footer = container.firstChild as HTMLElement
			expect(footer).toHaveClass("flex")
			expect(footer).toHaveClass("items-center")
			expect(footer).toHaveClass("gap-2")
		})
	})
})
