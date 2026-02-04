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
})
