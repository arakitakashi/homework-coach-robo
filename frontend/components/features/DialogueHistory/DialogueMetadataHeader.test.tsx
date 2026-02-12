import { render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"
import type { DialogueTurn } from "@/types"
import { DialogueMetadataHeader } from "./DialogueMetadataHeader"

describe("DialogueMetadataHeader", () => {
	const baseTurn: DialogueTurn = {
		id: "turn-1",
		speaker: "robot",
		text: "テスト対話",
		timestamp: new Date(),
	}

	describe("question type display", () => {
		it("should display question type icon when questionType is present", () => {
			const turn: DialogueTurn = {
				...baseTurn,
				questionType: "understanding_check",
			}

			render(<DialogueMetadataHeader turn={turn} />)

			expect(screen.getByLabelText("質問タイプ: 理解確認")).toBeInTheDocument()
		})

		it("should not display question type when questionType is absent", () => {
			render(<DialogueMetadataHeader turn={baseTurn} />)

			expect(screen.queryByLabelText(/質問タイプ:/)).not.toBeInTheDocument()
		})
	})

	describe("emotion display", () => {
		it("should display emotion icon when emotion is present", () => {
			const turn: DialogueTurn = {
				...baseTurn,
				emotion: "happy",
			}

			render(<DialogueMetadataHeader turn={turn} />)

			expect(screen.getByLabelText("感情: 元気いっぱい")).toBeInTheDocument()
		})

		it("should not display emotion when emotion is absent", () => {
			render(<DialogueMetadataHeader turn={baseTurn} />)

			expect(screen.queryByLabelText(/感情:/)).not.toBeInTheDocument()
		})
	})

	describe("agent display", () => {
		it("should display agent badge when activeAgent is present", () => {
			const turn: DialogueTurn = {
				...baseTurn,
				activeAgent: "math_coach",
			}

			render(<DialogueMetadataHeader turn={turn} />)

			expect(screen.getByLabelText("エージェント: 算数")).toBeInTheDocument()
		})

		it("should not display agent when activeAgent is absent", () => {
			render(<DialogueMetadataHeader turn={baseTurn} />)

			expect(screen.queryByLabelText(/エージェント:/)).not.toBeInTheDocument()
		})
	})

	describe("multiple metadata", () => {
		it("should display all metadata when all fields are present", () => {
			const turn: DialogueTurn = {
				...baseTurn,
				questionType: "hint",
				emotion: "confused",
				activeAgent: "encouragement",
			}

			render(<DialogueMetadataHeader turn={turn} />)

			expect(screen.getByLabelText("質問タイプ: ヒント")).toBeInTheDocument()
			expect(screen.getByLabelText("感情: わからない")).toBeInTheDocument()
			expect(screen.getByLabelText("エージェント: 励まし")).toBeInTheDocument()
		})
	})

	describe("layout", () => {
		it("should arrange items horizontally with gap", () => {
			const turn: DialogueTurn = {
				...baseTurn,
				questionType: "thinking_guide",
				emotion: "confident",
			}

			const { container } = render(<DialogueMetadataHeader turn={turn} />)

			const header = container.firstChild as HTMLElement
			expect(header).toHaveClass("flex")
			expect(header).toHaveClass("items-center")
			expect(header).toHaveClass("gap-2")
		})
	})
})
