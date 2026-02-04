import { fireEvent, render, screen } from "@testing-library/react"
import { describe, expect, it, vi } from "vitest"
import { Button } from "./Button"

describe("Button", () => {
	it("renders children correctly", () => {
		render(<Button>Click me</Button>)
		expect(screen.getByRole("button")).toHaveTextContent("Click me")
	})

	it("calls onClick when clicked", () => {
		const handleClick = vi.fn()
		render(<Button onClick={handleClick}>Click me</Button>)
		fireEvent.click(screen.getByRole("button"))
		expect(handleClick).toHaveBeenCalledTimes(1)
	})

	it("applies primary variant styles by default", () => {
		render(<Button>Primary</Button>)
		const button = screen.getByRole("button")
		expect(button).toHaveClass("bg-blue-600")
	})

	it("applies secondary variant styles", () => {
		render(<Button variant="secondary">Secondary</Button>)
		const button = screen.getByRole("button")
		expect(button).toHaveClass("bg-gray-200")
	})

	it("is disabled when disabled prop is true", () => {
		render(<Button disabled>Disabled</Button>)
		expect(screen.getByRole("button")).toBeDisabled()
	})

	it("applies disabled styles when disabled", () => {
		render(<Button disabled>Disabled</Button>)
		const button = screen.getByRole("button")
		expect(button).toHaveClass("opacity-50")
		expect(button).toHaveClass("cursor-not-allowed")
	})

	it("does not call onClick when disabled", () => {
		const handleClick = vi.fn()
		render(
			<Button onClick={handleClick} disabled>
				Disabled
			</Button>,
		)
		fireEvent.click(screen.getByRole("button"))
		expect(handleClick).not.toHaveBeenCalled()
	})

	it("applies large size styles", () => {
		render(<Button size="large">Large</Button>)
		const button = screen.getByRole("button")
		expect(button).toHaveClass("px-6")
		expect(button).toHaveClass("py-3")
	})

	it("has accessible name from children", () => {
		render(<Button>Accessible Button</Button>)
		expect(screen.getByRole("button", { name: "Accessible Button" })).toBeInTheDocument()
	})
})
