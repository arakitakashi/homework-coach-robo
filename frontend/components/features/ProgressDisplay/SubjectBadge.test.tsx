import { render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"
import { SubjectBadge } from "./SubjectBadge"

describe("SubjectBadge", () => {
	describe("math subject", () => {
		it("renders math icon and label", () => {
			render(<SubjectBadge subject="math" />)
			expect(screen.getByText("🧮")).toBeInTheDocument()
			expect(screen.getByText("算数")).toBeInTheDocument()
		})

		it("has blue color classes", () => {
			const { container } = render(<SubjectBadge subject="math" />)
			const badge = container.querySelector("div")
			expect(badge?.className).toContain("bg-blue-100")
			expect(badge?.className).toContain("text-blue-600")
		})

		it("has accessible label", () => {
			render(<SubjectBadge subject="math" />)
			expect(screen.getByLabelText("現在の科目: 算数")).toBeInTheDocument()
		})
	})

	describe("japanese subject", () => {
		it("renders japanese icon and label", () => {
			render(<SubjectBadge subject="japanese" />)
			expect(screen.getByText("📖")).toBeInTheDocument()
			expect(screen.getByText("国語")).toBeInTheDocument()
		})

		it("has green color classes", () => {
			const { container } = render(<SubjectBadge subject="japanese" />)
			const badge = container.querySelector("div")
			expect(badge?.className).toContain("bg-green-100")
			expect(badge?.className).toContain("text-green-600")
		})

		it("has accessible label", () => {
			render(<SubjectBadge subject="japanese" />)
			expect(screen.getByLabelText("現在の科目: 国語")).toBeInTheDocument()
		})
	})
})
