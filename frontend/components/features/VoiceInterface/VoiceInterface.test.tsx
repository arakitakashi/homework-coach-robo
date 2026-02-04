import { render, screen } from "@testing-library/react"
import { describe, expect, it, vi } from "vitest"
import { VoiceInterface } from "./VoiceInterface"

// Mock the hooks
vi.mock("@/lib/hooks", () => ({
	useVoiceRecorder: () => ({
		recordingState: "idle",
		audioLevel: 0,
		error: null,
		startRecording: vi.fn(),
		stopRecording: vi.fn(),
	}),
	useAudioPlayer: () => ({
		isPlaying: false,
		play: vi.fn(),
		stop: vi.fn(),
	}),
}))

describe("VoiceInterface", () => {
	it("renders record button", () => {
		render(<VoiceInterface onAudioData={vi.fn()} isConnected />)
		expect(screen.getByRole("button", { name: /録音/i })).toBeInTheDocument()
	})

	it("shows correct status when idle", () => {
		render(<VoiceInterface onAudioData={vi.fn()} isConnected />)
		expect(screen.getByText(/話しかけてね/i)).toBeInTheDocument()
	})

	it("shows disconnected message when not connected", () => {
		render(<VoiceInterface onAudioData={vi.fn()} isConnected={false} />)
		expect(screen.getByText(/接続中/i)).toBeInTheDocument()
	})

	it("disables record button when not connected", () => {
		render(<VoiceInterface onAudioData={vi.fn()} isConnected={false} />)
		const button = screen.getByRole("button", { name: /録音/i })
		expect(button).toBeDisabled()
	})

	it("has accessible button with aria-label", () => {
		render(<VoiceInterface onAudioData={vi.fn()} isConnected />)
		const button = screen.getByRole("button", { name: /録音/i })
		expect(button).toHaveAttribute("aria-label")
	})
})
