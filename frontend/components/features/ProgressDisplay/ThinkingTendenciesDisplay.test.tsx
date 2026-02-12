import { render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"
import type { ThinkingTendencies } from "@/types/phase2"
import { ThinkingTendenciesDisplay } from "./ThinkingTendenciesDisplay"

describe("ThinkingTendenciesDisplay", () => {
	const mockTendencies: ThinkingTendencies = {
		persistenceScore: 70,
		independenceScore: 80,
		reflectionQuality: 60,
		hintDependency: 40,
		updatedAt: new Date("2026-02-13T00:00:00Z"),
	}

	it("renders all four tendency bars", () => {
		render(<ThinkingTendenciesDisplay tendencies={mockTendencies} />)

		expect(screen.getByText("粘り強さ")).toBeInTheDocument()
		expect(screen.getByText("自立度")).toBeInTheDocument()
		expect(screen.getByText("振り返り")).toBeInTheDocument()
		expect(screen.getByText("ヒント依存")).toBeInTheDocument()
	})

	it("displays correct scores", () => {
		render(<ThinkingTendenciesDisplay tendencies={mockTendencies} />)

		expect(screen.getByText("70%")).toBeInTheDocument()
		expect(screen.getByText("80%")).toBeInTheDocument()
		expect(screen.getByText("60%")).toBeInTheDocument()
		expect(screen.getByText("40%")).toBeInTheDocument()
	})

	it("has accessible section with heading", () => {
		render(<ThinkingTendenciesDisplay tendencies={mockTendencies} />)

		const section = screen.getByRole("region", { name: "思考の傾向" })
		expect(section).toBeInTheDocument()

		expect(screen.getByText("思考の傾向")).toBeInTheDocument()
	})

	it("renders all progress bars with correct role", () => {
		render(<ThinkingTendenciesDisplay tendencies={mockTendencies} />)

		const progressBars = screen.getAllByRole("progressbar")
		expect(progressBars).toHaveLength(4)
	})

	it("returns null when tendencies is undefined", () => {
		const { container } = render(<ThinkingTendenciesDisplay tendencies={undefined} />)
		expect(container.firstChild).toBeNull()
	})

	describe("tendency bars", () => {
		it("renders persistence score correctly", () => {
			render(<ThinkingTendenciesDisplay tendencies={mockTendencies} />)
			const progressBar = screen.getByLabelText("粘り強さ: 70%")
			expect(progressBar).toHaveAttribute("aria-valuenow", "70")
		})

		it("renders independence score correctly", () => {
			render(<ThinkingTendenciesDisplay tendencies={mockTendencies} />)
			const progressBar = screen.getByLabelText("自立度: 80%")
			expect(progressBar).toHaveAttribute("aria-valuenow", "80")
		})

		it("renders reflection quality correctly", () => {
			render(<ThinkingTendenciesDisplay tendencies={mockTendencies} />)
			const progressBar = screen.getByLabelText("振り返り: 60%")
			expect(progressBar).toHaveAttribute("aria-valuenow", "60")
		})

		it("renders hint dependency correctly", () => {
			render(<ThinkingTendenciesDisplay tendencies={mockTendencies} />)
			const progressBar = screen.getByLabelText("ヒント依存: 40%")
			expect(progressBar).toHaveAttribute("aria-valuenow", "40")
		})
	})
})
