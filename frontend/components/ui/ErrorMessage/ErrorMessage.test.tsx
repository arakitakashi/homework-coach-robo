import { fireEvent, render, screen } from "@testing-library/react"
import { describe, expect, it, vi } from "vitest"
import { ErrorMessage } from "./ErrorMessage"

describe("ErrorMessage", () => {
	it("renders title and message", () => {
		render(<ErrorMessage title="Error" message="Something went wrong" />)
		expect(screen.getByText("Error")).toBeInTheDocument()
		expect(screen.getByText("Something went wrong")).toBeInTheDocument()
	})

	it("renders retry button when onRetry is provided", () => {
		const handleRetry = vi.fn()
		render(<ErrorMessage title="Error" message="Something went wrong" onRetry={handleRetry} />)
		expect(screen.getByRole("button", { name: /retry/i })).toBeInTheDocument()
	})

	it("does not render retry button when onRetry is not provided", () => {
		render(<ErrorMessage title="Error" message="Something went wrong" />)
		expect(screen.queryByRole("button")).not.toBeInTheDocument()
	})

	it("calls onRetry when retry button is clicked", () => {
		const handleRetry = vi.fn()
		render(<ErrorMessage title="Error" message="Something went wrong" onRetry={handleRetry} />)
		fireEvent.click(screen.getByRole("button", { name: /retry/i }))
		expect(handleRetry).toHaveBeenCalledTimes(1)
	})

	it("has error role for accessibility", () => {
		render(<ErrorMessage title="Error" message="Something went wrong" />)
		expect(screen.getByRole("alert")).toBeInTheDocument()
	})

	it("applies custom retry button text", () => {
		const handleRetry = vi.fn()
		render(
			<ErrorMessage
				title="Error"
				message="Something went wrong"
				onRetry={handleRetry}
				retryText="Try Again"
			/>,
		)
		expect(screen.getByRole("button", { name: "Try Again" })).toBeInTheDocument()
	})
})
