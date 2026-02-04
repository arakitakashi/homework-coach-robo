import { render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"
import { CharacterDisplay } from "./CharacterDisplay"

describe("CharacterDisplay", () => {
	it("renders robot character", () => {
		render(<CharacterDisplay character="robot" state="idle" />)
		expect(screen.getByRole("img", { name: /ロボット/i })).toBeInTheDocument()
	})

	it("applies idle state styling", () => {
		render(<CharacterDisplay character="robot" state="idle" />)
		const character = screen.getByRole("img", { name: /ロボット/i })
		expect(character.closest("div")).toHaveClass("animate-none")
	})

	it("applies listening state styling", () => {
		render(<CharacterDisplay character="robot" state="listening" />)
		const container = screen.getByTestId("character-container")
		expect(container).toHaveClass("animate-pulse")
	})

	it("applies speaking state styling", () => {
		render(<CharacterDisplay character="robot" state="speaking" />)
		const container = screen.getByTestId("character-container")
		expect(container).toHaveClass("animate-bounce")
	})

	it("applies thinking state styling", () => {
		render(<CharacterDisplay character="robot" state="thinking" />)
		const container = screen.getByTestId("character-container")
		expect(container).toHaveClass("animate-spin-slow")
	})

	it("has accessible role and label", () => {
		render(<CharacterDisplay character="robot" state="idle" />)
		expect(screen.getByRole("img")).toHaveAttribute("aria-label")
	})
})
