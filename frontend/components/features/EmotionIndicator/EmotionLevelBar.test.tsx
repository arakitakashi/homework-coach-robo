import { render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"
import { EmotionLevelBar } from "./EmotionLevelBar"

describe("EmotionLevelBar", () => {
	it("0-3の範囲で低レベルを表示する", () => {
		render(<EmotionLevelBar label="やる気" level={2} maxLevel={10} />)

		const levelText = screen.getByText(/低/)
		expect(levelText).toBeInTheDocument()
	})

	it("4-6の範囲で中レベルを表示する", () => {
		render(<EmotionLevelBar label="やる気" level={5} maxLevel={10} />)

		const levelText = screen.getByText(/中/)
		expect(levelText).toBeInTheDocument()
	})

	it("7-10の範囲で高レベルを表示する", () => {
		render(<EmotionLevelBar label="集中度" level={8} maxLevel={10} />)

		const levelText = screen.getByText(/高/)
		expect(levelText).toBeInTheDocument()
	})

	it("アクセシビリティ属性が設定される", () => {
		render(<EmotionLevelBar label="やる気" level={5} maxLevel={10} />)

		const progressBar = screen.getByRole("progressbar")
		expect(progressBar).toHaveAttribute("aria-label", "やる気")
		expect(progressBar).toHaveAttribute("aria-valuenow", "5")
		expect(progressBar).toHaveAttribute("aria-valuemin", "0")
		expect(progressBar).toHaveAttribute("aria-valuemax", "10")
	})

	it("カスタムラベルが表示される", () => {
		render(<EmotionLevelBar label="エネルギー" level={7} maxLevel={10} />)

		expect(screen.getByText("エネルギー")).toBeInTheDocument()
	})

	it("レベルに応じたバーの塗りつぶしが表示される", () => {
		const { container } = render(<EmotionLevelBar label="やる気" level={6} maxLevel={10} />)

		// バーの塗りつぶし要素を確認
		const fillBar = container.querySelector('[data-testid="level-bar-fill"]')
		expect(fillBar).toBeInTheDocument()
		expect(fillBar).toHaveStyle({ width: "60%" })
	})
})
