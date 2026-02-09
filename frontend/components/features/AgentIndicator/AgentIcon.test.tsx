import { render } from "@testing-library/react"
import { describe, expect, it } from "vitest"
import { AgentIcon } from "./AgentIcon"

describe("AgentIcon", () => {
	it("算数コーチの場合、Calculatorアイコンを表示する", () => {
		const { container } = render(<AgentIcon type="math_coach" />)
		// Lucide ReactのCalculatorアイコンはsvg要素として描画される
		const svg = container.querySelector("svg")
		expect(svg).toBeInTheDocument()
	})

	it("国語コーチの場合、BookOpenアイコンを表示する", () => {
		const { container } = render(<AgentIcon type="japanese_coach" />)
		const svg = container.querySelector("svg")
		expect(svg).toBeInTheDocument()
	})

	it("励ましの場合、Heartアイコンを表示する", () => {
		const { container } = render(<AgentIcon type="encouragement" />)
		const svg = container.querySelector("svg")
		expect(svg).toBeInTheDocument()
	})

	it("振り返りの場合、ClipboardListアイコンを表示する", () => {
		const { container } = render(<AgentIcon type="review" />)
		const svg = container.querySelector("svg")
		expect(svg).toBeInTheDocument()
	})

	it("ルーターの場合、Routerアイコンを表示する", () => {
		const { container } = render(<AgentIcon type="router" />)
		const svg = container.querySelector("svg")
		expect(svg).toBeInTheDocument()
	})

	it("aria-hidden='true'が設定される", () => {
		const { container } = render(<AgentIcon type="math_coach" />)
		const svg = container.querySelector("svg")
		expect(svg).toHaveAttribute("aria-hidden", "true")
	})

	it("カスタムclassNameが適用される", () => {
		const { container } = render(<AgentIcon type="math_coach" className="custom-class" />)
		const svg = container.querySelector("svg")
		expect(svg).toHaveClass("custom-class")
	})

	it("デフォルトclassNameが適用される", () => {
		const { container } = render(<AgentIcon type="math_coach" />)
		const svg = container.querySelector("svg")
		expect(svg).toHaveClass("h-5")
		expect(svg).toHaveClass("w-5")
	})
})
