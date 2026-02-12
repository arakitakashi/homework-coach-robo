import { render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"
import { TendencyBar } from "./TendencyBar"

describe("TendencyBar", () => {
	describe("score rendering", () => {
		it("renders score 0", () => {
			render(<TendencyBar label="粘り強さ" score={0} />)
			expect(screen.getByText("粘り強さ")).toBeInTheDocument()
			expect(screen.getByText("0%")).toBeInTheDocument()
		})

		it("renders score 50", () => {
			render(<TendencyBar label="自立度" score={50} />)
			expect(screen.getByText("自立度")).toBeInTheDocument()
			expect(screen.getByText("50%")).toBeInTheDocument()
		})

		it("renders score 100", () => {
			render(<TendencyBar label="振り返り" score={100} />)
			expect(screen.getByText("振り返り")).toBeInTheDocument()
			expect(screen.getByText("100%")).toBeInTheDocument()
		})
	})

	describe("score normalization", () => {
		it("normalizes score below 0 to 0", () => {
			render(<TendencyBar label="テスト" score={-10} />)
			const progressBar = screen.getByRole("progressbar")
			expect(progressBar).toHaveAttribute("aria-valuenow", "0")
		})

		it("normalizes score above 100 to 100", () => {
			render(<TendencyBar label="テスト" score={150} />)
			const progressBar = screen.getByRole("progressbar")
			expect(progressBar).toHaveAttribute("aria-valuenow", "100")
		})
	})

	describe("invert option", () => {
		it("uses default color when invert is false", () => {
			const { container } = render(<TendencyBar label="テスト" score={80} invert={false} />)
			const progressFill = container.querySelector("[data-testid='progress-fill']")
			expect(progressFill?.className).toContain("bg-blue-500")
		})

		it("uses inverted color when invert is true", () => {
			const { container } = render(<TendencyBar label="ヒント依存" score={40} invert={true} />)
			const progressFill = container.querySelector("[data-testid='progress-fill']")
			expect(progressFill?.className).toContain("bg-orange-500")
		})
	})

	describe("accessibility", () => {
		it("has progressbar role", () => {
			render(<TendencyBar label="粘り強さ" score={70} />)
			const progressBar = screen.getByRole("progressbar")
			expect(progressBar).toBeInTheDocument()
		})

		it("has correct aria attributes", () => {
			render(<TendencyBar label="自立度" score={80} />)
			const progressBar = screen.getByRole("progressbar")
			expect(progressBar).toHaveAttribute("aria-valuenow", "80")
			expect(progressBar).toHaveAttribute("aria-valuemin", "0")
			expect(progressBar).toHaveAttribute("aria-valuemax", "100")
			expect(progressBar).toHaveAttribute("aria-label", "自立度: 80%")
		})
	})

	describe("progress bar width", () => {
		it("sets correct width style for score 0", () => {
			const { container } = render(<TendencyBar label="テスト" score={0} />)
			const progressFill = container.querySelector("[data-testid='progress-fill']") as HTMLElement
			expect(progressFill?.style.width).toBe("0%")
		})

		it("sets correct width style for score 50", () => {
			const { container } = render(<TendencyBar label="テスト" score={50} />)
			const progressFill = container.querySelector("[data-testid='progress-fill']") as HTMLElement
			expect(progressFill?.style.width).toBe("50%")
		})

		it("sets correct width style for score 100", () => {
			const { container } = render(<TendencyBar label="テスト" score={100} />)
			const progressFill = container.querySelector("[data-testid='progress-fill']") as HTMLElement
			expect(progressFill?.style.width).toBe("100%")
		})
	})
})
