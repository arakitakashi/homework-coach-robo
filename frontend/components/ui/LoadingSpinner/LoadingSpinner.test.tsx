import { render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"
import { LoadingSpinner } from "./LoadingSpinner"

describe("LoadingSpinner", () => {
	it("renders spinner with default size", () => {
		render(<LoadingSpinner />)
		const spinner = screen.getByRole("status")
		expect(spinner).toBeInTheDocument()
		expect(spinner).toHaveClass("w-8")
		expect(spinner).toHaveClass("h-8")
	})

	it("renders spinner with small size", () => {
		render(<LoadingSpinner size="small" />)
		const spinner = screen.getByRole("status")
		expect(spinner).toHaveClass("w-5")
		expect(spinner).toHaveClass("h-5")
	})

	it("renders spinner with large size", () => {
		render(<LoadingSpinner size="large" />)
		const spinner = screen.getByRole("status")
		expect(spinner).toHaveClass("w-12")
		expect(spinner).toHaveClass("h-12")
	})

	it("has accessible label", () => {
		render(<LoadingSpinner />)
		expect(screen.getByRole("status")).toHaveAttribute("aria-label", "Loading")
	})

	it("applies custom aria-label", () => {
		render(<LoadingSpinner aria-label="Processing" />)
		expect(screen.getByRole("status")).toHaveAttribute("aria-label", "Processing")
	})
})
