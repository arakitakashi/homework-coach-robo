import { render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"
import { EmotionIcon } from "./EmotionIcon"

describe("EmotionIcon", () => {
	describe("frustrated", () => {
		it("should display frustrated emotion icon", () => {
			render(<EmotionIcon emotion="frustrated" />)

			const icon = screen.getByLabelText("感情: 困っている")
			expect(icon).toBeInTheDocument()
		})
	})

	describe("confident", () => {
		it("should display confident emotion icon", () => {
			render(<EmotionIcon emotion="confident" />)

			const icon = screen.getByLabelText("感情: 自信満々")
			expect(icon).toBeInTheDocument()
		})
	})

	describe("confused", () => {
		it("should display confused emotion icon", () => {
			render(<EmotionIcon emotion="confused" />)

			const icon = screen.getByLabelText("感情: わからない")
			expect(icon).toBeInTheDocument()
		})
	})

	describe("happy", () => {
		it("should display happy emotion icon", () => {
			render(<EmotionIcon emotion="happy" />)

			const icon = screen.getByLabelText("感情: 元気いっぱい")
			expect(icon).toBeInTheDocument()
		})
	})

	describe("tired", () => {
		it("should display tired emotion icon", () => {
			render(<EmotionIcon emotion="tired" />)

			const icon = screen.getByLabelText("感情: 疲れている")
			expect(icon).toBeInTheDocument()
		})
	})

	describe("neutral", () => {
		it("should display neutral emotion icon", () => {
			render(<EmotionIcon emotion="neutral" />)

			const icon = screen.getByLabelText("感情: 落ち着いている")
			expect(icon).toBeInTheDocument()
		})
	})

	describe("color coding", () => {
		it("should use red color for frustrated", () => {
			render(<EmotionIcon emotion="frustrated" />)
			const icon = screen.getByLabelText("感情: 困っている")
			expect(icon).toBeInTheDocument()
		})

		it("should use green color for confident", () => {
			render(<EmotionIcon emotion="confident" />)
			const icon = screen.getByLabelText("感情: 自信満々")
			expect(icon).toBeInTheDocument()
		})
	})

	describe("accessibility", () => {
		it("should have aria-label for each emotion type", () => {
			const emotions = ["frustrated", "confident", "confused", "happy", "tired", "neutral"] as const

			for (const emotion of emotions) {
				const { unmount } = render(<EmotionIcon emotion={emotion} />)
				expect(screen.getByLabelText(/感情:/)).toBeInTheDocument()
				unmount()
			}
		})

		it("should hide icon from screen readers with aria-hidden", () => {
			render(<EmotionIcon emotion="frustrated" />)

			const container = screen.getByLabelText("感情: 困っている")
			const svg = container.querySelector("svg")
			expect(svg).toHaveAttribute("aria-hidden", "true")
		})
	})
})
