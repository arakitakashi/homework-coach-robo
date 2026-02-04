import { render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"
import { HintIndicator } from "./HintIndicator"

describe("HintIndicator", () => {
	it("renders three hint levels", () => {
		render(<HintIndicator currentLevel={0} />)
		const hints = screen.getAllByRole("img")
		expect(hints).toHaveLength(3)
	})

	it("shows all closed when level is 0", () => {
		render(<HintIndicator currentLevel={0} />)
		const hints = screen.getAllByTestId("hint-box")
		for (const hint of hints) {
			expect(hint).toHaveAttribute("data-open", "false")
		}
	})

	it("shows first hint open when level is 1", () => {
		render(<HintIndicator currentLevel={1} />)
		const hints = screen.getAllByTestId("hint-box")
		expect(hints[0]).toHaveAttribute("data-open", "true")
		expect(hints[1]).toHaveAttribute("data-open", "false")
		expect(hints[2]).toHaveAttribute("data-open", "false")
	})

	it("shows two hints open when level is 2", () => {
		render(<HintIndicator currentLevel={2} />)
		const hints = screen.getAllByTestId("hint-box")
		expect(hints[0]).toHaveAttribute("data-open", "true")
		expect(hints[1]).toHaveAttribute("data-open", "true")
		expect(hints[2]).toHaveAttribute("data-open", "false")
	})

	it("shows all hints open when level is 3", () => {
		render(<HintIndicator currentLevel={3} />)
		const hints = screen.getAllByTestId("hint-box")
		for (const hint of hints) {
			expect(hint).toHaveAttribute("data-open", "true")
		}
	})

	it("has accessible labels", () => {
		render(<HintIndicator currentLevel={0} />)
		// グループにヒントレベルのラベルがある
		expect(screen.getByRole("group", { name: /ヒントレベル/i })).toBeInTheDocument()
		// 各ヒントにもラベルがある
		const hints = screen.getAllByRole("img")
		expect(hints).toHaveLength(3)
		expect(hints[0]).toHaveAccessibleName(/ヒント1/i)
	})
})
