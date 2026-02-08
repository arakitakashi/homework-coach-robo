/**
 * ToolExecutionDisplay コンポーネントテスト
 */

import { render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"
import type { ToolExecution } from "@/types"
import { ToolExecutionDisplay } from "./ToolExecutionDisplay"

const createExecution = (overrides: Partial<ToolExecution> = {}): ToolExecution => ({
	toolName: "calculate_tool",
	status: "running",
	timestamp: new Date(),
	...overrides,
})

describe("ToolExecutionDisplay", () => {
	describe("非表示", () => {
		it("実行中ツールが無い場合は何も表示しない", () => {
			const { container } = render(<ToolExecutionDisplay executions={[]} isRunning={false} />)
			expect(container.firstChild).toBeNull()
		})
	})

	describe("ローディング表示", () => {
		it("running ステータスでローディング表示とツール日本語名を表示する", () => {
			render(
				<ToolExecutionDisplay
					executions={[createExecution({ status: "running" })]}
					isRunning={true}
				/>,
			)

			expect(screen.getByText("けいさん")).toBeInTheDocument()
			expect(screen.getByRole("status", { name: "ツールじっこうちゅう" })).toBeInTheDocument()
		})

		it("pending ステータスでもローディング表示する", () => {
			render(
				<ToolExecutionDisplay
					executions={[createExecution({ toolName: "manage_hint_tool", status: "pending" })]}
					isRunning={true}
				/>,
			)

			expect(screen.getByText("ヒント")).toBeInTheDocument()
		})
	})

	describe("ツール名の日本語マッピング", () => {
		it.each([
			["calculate_tool", "けいさん"],
			["manage_hint_tool", "ヒント"],
			["record_progress_tool", "きろく"],
			["check_curriculum_tool", "きょうかしょ"],
			["analyze_image_tool", "しゃしん"],
		] as const)("%s は「%s」と表示される", (toolName, expectedLabel) => {
			render(
				<ToolExecutionDisplay
					executions={[createExecution({ toolName, status: "running" })]}
					isRunning={true}
				/>,
			)

			expect(screen.getByText(expectedLabel)).toBeInTheDocument()
		})
	})

	describe("完了表示", () => {
		it("completed ステータスで完了表示する", () => {
			render(
				<ToolExecutionDisplay
					executions={[createExecution({ status: "completed" })]}
					isRunning={false}
				/>,
			)

			expect(screen.getByText("けいさん")).toBeInTheDocument()
			// 完了マーク（✓）が表示される
			expect(screen.getByTestId("tool-status-completed")).toBeInTheDocument()
		})
	})

	describe("エラー表示", () => {
		it("error ステータスでエラー表示する", () => {
			render(
				<ToolExecutionDisplay
					executions={[createExecution({ status: "error", error: "計算に失敗しました" })]}
					isRunning={false}
				/>,
			)

			expect(screen.getByText("けいさん")).toBeInTheDocument()
			expect(screen.getByTestId("tool-status-error")).toBeInTheDocument()
		})
	})

	describe("複数ツール", () => {
		it("複数ツールを同時に表示する", () => {
			render(
				<ToolExecutionDisplay
					executions={[
						createExecution({ toolName: "calculate_tool", status: "completed" }),
						createExecution({
							toolName: "record_progress_tool",
							status: "running",
						}),
					]}
					isRunning={true}
				/>,
			)

			expect(screen.getByText("けいさん")).toBeInTheDocument()
			expect(screen.getByText("きろく")).toBeInTheDocument()
		})
	})

	describe("アクセシビリティ", () => {
		it("role=status と aria-live=polite が設定されている", () => {
			render(
				<ToolExecutionDisplay
					executions={[createExecution({ status: "running" })]}
					isRunning={true}
				/>,
			)

			const statusElement = screen.getByRole("status", { name: "ツールじっこうちゅう" })
			expect(statusElement).toHaveAttribute("aria-live", "polite")
		})

		it("aria-label にツール実行状態の説明がある", () => {
			render(
				<ToolExecutionDisplay
					executions={[createExecution({ status: "running" })]}
					isRunning={true}
				/>,
			)

			const statusElement = screen.getByRole("status", { name: "ツールじっこうちゅう" })
			expect(statusElement).toHaveAttribute("aria-label", "ツールじっこうちゅう")
		})
	})
})
