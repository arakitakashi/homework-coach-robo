import { render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"
import type { DialogueTurn } from "@/types"
import { DialogueHistory } from "./DialogueHistory"

const mockTurns: DialogueTurn[] = [
	{
		id: "1",
		speaker: "child",
		text: "3+5は？",
		timestamp: new Date(),
	},
	{
		id: "2",
		speaker: "robot",
		text: "いい質問だね！3+5は何だと思う？",
		timestamp: new Date(),
	},
]

describe("DialogueHistory", () => {
	it("renders dialogue turns", () => {
		render(<DialogueHistory turns={mockTurns} />)
		expect(screen.getByText("3+5は？")).toBeInTheDocument()
		expect(screen.getByText("いい質問だね！3+5は何だと思う？")).toBeInTheDocument()
	})

	it("shows empty state when no turns", () => {
		render(<DialogueHistory turns={[]} />)
		expect(screen.getByText(/対話を始めよう/i)).toBeInTheDocument()
	})

	it("applies different styles for child and robot", () => {
		render(<DialogueHistory turns={mockTurns} />)
		const childBubble = screen.getByText("3+5は？").closest("div")
		const robotBubble = screen.getByText("いい質問だね！3+5は何だと思う？").closest("div")

		expect(childBubble).toHaveClass("bg-blue-100")
		expect(robotBubble).toHaveClass("bg-gray-100")
	})

	it("has accessible region", () => {
		render(<DialogueHistory turns={mockTurns} />)
		expect(screen.getByRole("log")).toBeInTheDocument()
	})

	describe("Phase 2 metadata display", () => {
		it("displays question type when present", () => {
			const turnsWithMetadata: DialogueTurn[] = [
				{
					id: "1",
					speaker: "robot",
					text: "この問題は何を聞いていると思う？",
					timestamp: new Date(),
					questionType: "understanding_check",
				},
			]

			render(<DialogueHistory turns={turnsWithMetadata} />)

			expect(screen.getByLabelText("質問タイプ: 理解確認")).toBeInTheDocument()
		})

		it("displays emotion when present", () => {
			const turnsWithMetadata: DialogueTurn[] = [
				{
					id: "1",
					speaker: "child",
					text: "わからない...",
					timestamp: new Date(),
					emotion: "confused",
				},
			]

			render(<DialogueHistory turns={turnsWithMetadata} />)

			expect(screen.getByLabelText("感情: わからない")).toBeInTheDocument()
		})

		it("displays active agent when present", () => {
			const turnsWithMetadata: DialogueTurn[] = [
				{
					id: "1",
					speaker: "robot",
					text: "一緒に計算してみよう",
					timestamp: new Date(),
					activeAgent: "math_coach",
				},
			]

			render(<DialogueHistory turns={turnsWithMetadata} />)

			expect(screen.getByLabelText("エージェント: 算数")).toBeInTheDocument()
		})

		it("displays response analysis when present", () => {
			const turnsWithMetadata: DialogueTurn[] = [
				{
					id: "1",
					speaker: "child",
					text: "8だと思う",
					timestamp: new Date(),
					responseAnalysis: {
						understandingLevel: 0.9,
						isCorrectDirection: true,
						needsClarification: false,
						keyInsights: [],
					},
				},
			]

			render(<DialogueHistory turns={turnsWithMetadata} />)

			expect(screen.getByLabelText("理解度: 90%")).toBeInTheDocument()
		})

		it("displays tool executions when present", () => {
			const turnsWithMetadata: DialogueTurn[] = [
				{
					id: "1",
					speaker: "robot",
					text: "計算を確認したよ",
					timestamp: new Date(),
					toolExecutions: [
						{
							toolName: "calculate_tool",
							status: "completed",
							timestamp: new Date(),
						},
					],
				},
			]

			render(<DialogueHistory turns={turnsWithMetadata} />)

			expect(screen.getByText("けいさん")).toBeInTheDocument()
		})

		it("displays all Phase 2 metadata together", () => {
			const turnsWithMetadata: DialogueTurn[] = [
				{
					id: "1",
					speaker: "robot",
					text: "ヒントを使って考えてみよう",
					timestamp: new Date(),
					questionType: "hint",
					emotion: "happy",
					activeAgent: "math_coach",
					responseAnalysis: {
						understandingLevel: 0.7,
						isCorrectDirection: true,
						needsClarification: false,
						keyInsights: [],
					},
					toolExecutions: [
						{
							toolName: "manage_hint_tool",
							status: "completed",
							timestamp: new Date(),
						},
					],
				},
			]

			render(<DialogueHistory turns={turnsWithMetadata} />)

			expect(screen.getByLabelText("質問タイプ: ヒント")).toBeInTheDocument()
			expect(screen.getByLabelText("感情: 元気いっぱい")).toBeInTheDocument()
			expect(screen.getByLabelText("エージェント: 算数")).toBeInTheDocument()
			expect(screen.getByLabelText("理解度: 70%")).toBeInTheDocument()
			expect(screen.getByText("ヒント")).toBeInTheDocument()
		})

		it("works without Phase 2 metadata (backward compatibility)", () => {
			const turnsWithoutMetadata: DialogueTurn[] = [
				{
					id: "1",
					speaker: "robot",
					text: "こんにちは",
					timestamp: new Date(),
				},
			]

			render(<DialogueHistory turns={turnsWithoutMetadata} />)

			expect(screen.getByText("こんにちは")).toBeInTheDocument()
			expect(screen.queryByLabelText(/質問タイプ:/)).not.toBeInTheDocument()
			expect(screen.queryByLabelText(/感情:/)).not.toBeInTheDocument()
			expect(screen.queryByLabelText(/エージェント:/)).not.toBeInTheDocument()
		})
	})
})
