import { render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"
import { ProgressDisplay } from "./ProgressDisplay"

describe("ProgressDisplay", () => {
	it("renders progress counts", () => {
		render(<ProgressDisplay selfDiscoveryCount={3} hintDiscoveryCount={2} togetherCount={1} />)
		expect(screen.getByText("3")).toBeInTheDocument()
		expect(screen.getByText("2")).toBeInTheDocument()
		expect(screen.getByText("1")).toBeInTheDocument()
	})

	it("shows total points", () => {
		// 3 * 3 + 2 * 2 + 1 * 1 = 9 + 4 + 1 = 14
		render(<ProgressDisplay selfDiscoveryCount={3} hintDiscoveryCount={2} togetherCount={1} />)
		expect(screen.getByText(/14/)).toBeInTheDocument()
	})

	it("shows zero counts correctly", () => {
		render(<ProgressDisplay selfDiscoveryCount={0} hintDiscoveryCount={0} togetherCount={0} />)
		// 合計ポイントの0と3つのカウンターの0で計4つの0がある
		expect(screen.getAllByText("0")).toHaveLength(4)
		expect(screen.getByText(/ポイント/i)).toBeInTheDocument()
	})

	it("has descriptive labels", () => {
		render(<ProgressDisplay selfDiscoveryCount={1} hintDiscoveryCount={1} togetherCount={1} />)
		expect(screen.getByText(/自分で/i)).toBeInTheDocument()
		expect(screen.getByText(/ヒントで/i)).toBeInTheDocument()
		expect(screen.getByText(/一緒に/i)).toBeInTheDocument()
	})
})
