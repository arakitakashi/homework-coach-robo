import { render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"
import type { ToolExecution } from "@/types"
import { ToolExecutionBadges } from "./ToolExecutionBadges"

describe("ToolExecutionBadges", () => {
	describe("tool name display", () => {
		it("should display calculate tool label", () => {
			const executions: ToolExecution[] = [
				{
					toolName: "calculate_tool",
					status: "completed",
					timestamp: new Date(),
				},
			]

			render(<ToolExecutionBadges executions={executions} />)

			expect(screen.getByText("けいさん")).toBeInTheDocument()
		})

		it("should display manage hint tool label", () => {
			const executions: ToolExecution[] = [
				{
					toolName: "manage_hint_tool",
					status: "completed",
					timestamp: new Date(),
				},
			]

			render(<ToolExecutionBadges executions={executions} />)

			expect(screen.getByText("ヒント")).toBeInTheDocument()
		})

		it("should display record progress tool label", () => {
			const executions: ToolExecution[] = [
				{
					toolName: "record_progress_tool",
					status: "completed",
					timestamp: new Date(),
				},
			]

			render(<ToolExecutionBadges executions={executions} />)

			expect(screen.getByText("きろく")).toBeInTheDocument()
		})

		it("should display check curriculum tool label", () => {
			const executions: ToolExecution[] = [
				{
					toolName: "check_curriculum_tool",
					status: "completed",
					timestamp: new Date(),
				},
			]

			render(<ToolExecutionBadges executions={executions} />)

			expect(screen.getByText("きょうかしょ")).toBeInTheDocument()
		})

		it("should display analyze image tool label", () => {
			const executions: ToolExecution[] = [
				{
					toolName: "analyze_image_tool",
					status: "completed",
					timestamp: new Date(),
				},
			]

			render(<ToolExecutionBadges executions={executions} />)

			expect(screen.getByText("しゃしん")).toBeInTheDocument()
		})
	})

	describe("status icons", () => {
		it("should show check icon for completed status", () => {
			const executions: ToolExecution[] = [
				{
					toolName: "calculate_tool",
					status: "completed",
					timestamp: new Date(),
				},
			]

			const { container } = render(<ToolExecutionBadges executions={executions} />)

			// CheckCircle icon が描画されているか確認
			const svg = container.querySelector("svg")
			expect(svg).toBeInTheDocument()
		})

		it("should show X icon for error status", () => {
			const executions: ToolExecution[] = [
				{
					toolName: "calculate_tool",
					status: "error",
					timestamp: new Date(),
				},
			]

			const { container } = render(<ToolExecutionBadges executions={executions} />)

			const svg = container.querySelector("svg")
			expect(svg).toBeInTheDocument()
		})

		it("should show loading icon for pending status", () => {
			const executions: ToolExecution[] = [
				{
					toolName: "calculate_tool",
					status: "pending",
					timestamp: new Date(),
				},
			]

			const { container } = render(<ToolExecutionBadges executions={executions} />)

			const svg = container.querySelector("svg")
			expect(svg).toBeInTheDocument()
		})

		it("should show loading icon for running status", () => {
			const executions: ToolExecution[] = [
				{
					toolName: "calculate_tool",
					status: "running",
					timestamp: new Date(),
				},
			]

			const { container } = render(<ToolExecutionBadges executions={executions} />)

			const svg = container.querySelector("svg")
			expect(svg).toBeInTheDocument()
		})
	})

	describe("multiple tools", () => {
		it("should display multiple tool badges", () => {
			const executions: ToolExecution[] = [
				{
					toolName: "calculate_tool",
					status: "completed",
					timestamp: new Date(),
				},
				{
					toolName: "manage_hint_tool",
					status: "completed",
					timestamp: new Date("2024-01-01T12:01:00"),
				},
				{
					toolName: "record_progress_tool",
					status: "running",
					timestamp: new Date("2024-01-01T12:02:00"),
				},
			]

			render(<ToolExecutionBadges executions={executions} />)

			expect(screen.getByText("けいさん")).toBeInTheDocument()
			expect(screen.getByText("ヒント")).toBeInTheDocument()
			expect(screen.getByText("きろく")).toBeInTheDocument()
		})
	})

	describe("empty executions", () => {
		it("should render without errors for empty array", () => {
			render(<ToolExecutionBadges executions={[]} />)

			// 空配列でもエラーなく描画される
			const container = screen.queryByRole("list")
			expect(container).not.toBeInTheDocument()
		})
	})
})
