import { render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"
import { Card } from "./Card"

describe("Card", () => {
	it("renders children correctly", () => {
		render(<Card>Card content</Card>)
		expect(screen.getByText("Card content")).toBeInTheDocument()
	})

	it("applies default styles", () => {
		render(<Card>Content</Card>)
		const card = screen.getByText("Content").closest("div")
		expect(card).toHaveClass("bg-white")
		expect(card).toHaveClass("rounded-xl")
		expect(card).toHaveClass("shadow-md")
	})

	it("applies additional className", () => {
		render(<Card className="custom-class">Content</Card>)
		const card = screen.getByText("Content").closest("div")
		expect(card).toHaveClass("custom-class")
	})

	it("renders with padding variant", () => {
		render(<Card padding="large">Content</Card>)
		const card = screen.getByText("Content").closest("div")
		expect(card).toHaveClass("p-6")
	})
})
