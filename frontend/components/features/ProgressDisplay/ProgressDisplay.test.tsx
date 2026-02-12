import { render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"
import type { ThinkingTendencies } from "@/types/phase2"
import { ProgressDisplay } from "./ProgressDisplay"

describe("ProgressDisplay", () => {
	describe("existing functionality", () => {
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

	describe("Phase 2 extensions", () => {
		describe("SubjectDisplay integration", () => {
			it("renders subject and topic when provided", () => {
				render(
					<ProgressDisplay
						selfDiscoveryCount={1}
						hintDiscoveryCount={1}
						togetherCount={1}
						currentSubject="math"
						currentTopic="足し算の筆算"
					/>,
				)
				expect(screen.getByText("算数")).toBeInTheDocument()
				expect(screen.getByText("足し算の筆算")).toBeInTheDocument()
			})

			it("does not render SubjectDisplay when both subject and topic are undefined", () => {
				render(
					<ProgressDisplay
						selfDiscoveryCount={1}
						hintDiscoveryCount={1}
						togetherCount={1}
						currentSubject={undefined}
						currentTopic={undefined}
					/>,
				)
				expect(screen.queryByText("算数")).not.toBeInTheDocument()
				expect(screen.queryByText("国語")).not.toBeInTheDocument()
			})
		})

		describe("ThinkingTendenciesDisplay integration", () => {
			const mockTendencies: ThinkingTendencies = {
				persistenceScore: 70,
				independenceScore: 80,
				reflectionQuality: 60,
				hintDependency: 40,
				updatedAt: new Date("2026-02-13T00:00:00Z"),
			}

			it("renders thinking tendencies when provided", () => {
				render(
					<ProgressDisplay
						selfDiscoveryCount={1}
						hintDiscoveryCount={1}
						togetherCount={1}
						thinkingTendencies={mockTendencies}
					/>,
				)
				expect(screen.getByText("思考の傾向")).toBeInTheDocument()
				expect(screen.getByText("粘り強さ")).toBeInTheDocument()
				expect(screen.getByText("自立度")).toBeInTheDocument()
			})

			it("does not render ThinkingTendenciesDisplay when tendencies is undefined", () => {
				render(
					<ProgressDisplay
						selfDiscoveryCount={1}
						hintDiscoveryCount={1}
						togetherCount={1}
						thinkingTendencies={undefined}
					/>,
				)
				expect(screen.queryByText("思考の傾向")).not.toBeInTheDocument()
			})
		})

		describe("full integration", () => {
			const mockTendencies: ThinkingTendencies = {
				persistenceScore: 85,
				independenceScore: 90,
				reflectionQuality: 75,
				hintDependency: 30,
				updatedAt: new Date("2026-02-13T00:00:00Z"),
			}

			it("renders all components when all fields are provided", () => {
				render(
					<ProgressDisplay
						selfDiscoveryCount={3}
						hintDiscoveryCount={2}
						togetherCount={1}
						currentSubject="japanese"
						currentTopic="漢字の読み書き"
						thinkingTendencies={mockTendencies}
					/>,
				)

				// 既存の進捗表示
				expect(screen.getByText("3")).toBeInTheDocument()
				expect(screen.getByText(/14/)).toBeInTheDocument()

				// 教科・トピック表示
				expect(screen.getByText("国語")).toBeInTheDocument()
				expect(screen.getByText("漢字の読み書き")).toBeInTheDocument()

				// 思考の傾向表示
				expect(screen.getByText("思考の傾向")).toBeInTheDocument()
				expect(screen.getByText("85%")).toBeInTheDocument()
				expect(screen.getByText("90%")).toBeInTheDocument()
			})

			it("renders only existing progress when Phase 2 fields are not provided", () => {
				render(
					<ProgressDisplay
						selfDiscoveryCount={2}
						hintDiscoveryCount={1}
						togetherCount={0}
						currentSubject={undefined}
						currentTopic={undefined}
						thinkingTendencies={undefined}
					/>,
				)

				// 既存の進捗表示のみ
				expect(screen.getByText("2")).toBeInTheDocument()
				expect(screen.getByText(/8/)).toBeInTheDocument()

				// Phase 2の表示はない
				expect(screen.queryByText("算数")).not.toBeInTheDocument()
				expect(screen.queryByText("国語")).not.toBeInTheDocument()
				expect(screen.queryByText("思考の傾向")).not.toBeInTheDocument()
			})
		})
	})
})
