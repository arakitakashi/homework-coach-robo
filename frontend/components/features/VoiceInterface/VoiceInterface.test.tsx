import { fireEvent, render, screen } from "@testing-library/react"
import { describe, expect, it, vi } from "vitest"
import { VoiceInterface } from "./VoiceInterface"

describe("VoiceInterface", () => {
	const defaultProps = {
		isRecording: false,
		audioLevel: 0,
		isConnected: true,
		isPlaying: false,
		onToggleRecording: vi.fn(),
	}

	it("renders record button", () => {
		render(<VoiceInterface {...defaultProps} />)
		expect(screen.getByRole("button", { name: /録音/i })).toBeInTheDocument()
	})

	it("shows correct status when idle", () => {
		render(<VoiceInterface {...defaultProps} />)
		expect(screen.getByText(/話しかけてね/i)).toBeInTheDocument()
	})

	it("shows recording status when recording", () => {
		render(<VoiceInterface {...defaultProps} isRecording />)
		expect(screen.getByText(/録音中/i)).toBeInTheDocument()
	})

	it("shows playing status when playing audio", () => {
		render(<VoiceInterface {...defaultProps} isPlaying />)
		expect(screen.getByText(/聞いているよ/i)).toBeInTheDocument()
	})

	it("shows disconnected message when not connected", () => {
		render(<VoiceInterface {...defaultProps} isConnected={false} />)
		expect(screen.getByText(/接続中/i)).toBeInTheDocument()
	})

	it("disables record button when not connected", () => {
		render(<VoiceInterface {...defaultProps} isConnected={false} />)
		const button = screen.getByRole("button", { name: /録音/i })
		expect(button).toBeDisabled()
	})

	it("calls onToggleRecording when button is clicked", () => {
		const onToggleRecording = vi.fn()
		render(<VoiceInterface {...defaultProps} onToggleRecording={onToggleRecording} />)

		const button = screen.getByRole("button", { name: /録音/i })
		fireEvent.click(button)

		expect(onToggleRecording).toHaveBeenCalled()
	})

	it("has accessible button with aria-label", () => {
		render(<VoiceInterface {...defaultProps} />)
		const button = screen.getByRole("button", { name: /録音/i })
		expect(button).toHaveAttribute("aria-label")
	})

	it("shows audio level indicator", () => {
		render(<VoiceInterface {...defaultProps} audioLevel={0.5} />)
		// Audio level visualizer should exist
		const visualizer = screen.getByRole("progressbar")
		expect(visualizer).toBeInTheDocument()
		expect(visualizer).toHaveAttribute("aria-valuenow", "50")
	})

	it("button shows stop icon when recording", () => {
		render(<VoiceInterface {...defaultProps} isRecording />)
		const button = screen.getByRole("button", { name: /止める/i })
		expect(button).toHaveAttribute("aria-pressed", "true")
	})
})
