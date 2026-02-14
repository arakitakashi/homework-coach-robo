import { render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"
import { TrendBadge } from "./TrendBadge"

describe("TrendBadge", () => {
	describe("improving trend", () => {
		it("「上がっている」ラベルを表示する", () => {
			render(<TrendBadge trend="improving" />)
			expect(screen.getByText("上がっている")).toBeInTheDocument()
		})

		it("緑色のスタイルが適用される", () => {
			const { container } = render(<TrendBadge trend="improving" />)
			const badge = container.firstElementChild
			expect(badge?.className).toContain("text-green")
		})
	})

	describe("stable trend", () => {
		it("「安定」ラベルを表示する", () => {
			render(<TrendBadge trend="stable" />)
			expect(screen.getByText("安定")).toBeInTheDocument()
		})

		it("青色のスタイルが適用される", () => {
			const { container } = render(<TrendBadge trend="stable" />)
			const badge = container.firstElementChild
			expect(badge?.className).toContain("text-blue")
		})
	})

	describe("declining trend", () => {
		it("「がんばろう」ラベルを表示する", () => {
			render(<TrendBadge trend="declining" />)
			expect(screen.getByText("がんばろう")).toBeInTheDocument()
		})

		it("オレンジ色のスタイルが適用される", () => {
			const { container } = render(<TrendBadge trend="declining" />)
			const badge = container.firstElementChild
			expect(badge?.className).toContain("text-orange")
		})
	})

	describe("アクセシビリティ", () => {
		it("aria-labelがトレンドの説明を含む", () => {
			render(<TrendBadge trend="improving" />)
			expect(screen.getByLabelText("トレンド: 上がっている")).toBeInTheDocument()
		})
	})
})
