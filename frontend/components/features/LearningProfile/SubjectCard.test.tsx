import { render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"
import type { SubjectUnderstanding } from "@/types/phase2"
import { SubjectCard } from "./SubjectCard"

/** テスト用のSubjectUnderstandingデータ */
const createMockUnderstanding = (
	overrides: Partial<SubjectUnderstanding> = {},
): SubjectUnderstanding => ({
	subject: "算数",
	topic: "かけ算",
	level: 7,
	trend: "improving",
	weakPoints: ["くり上がり"],
	strongPoints: ["たし算", "ひき算"],
	assessedAt: new Date("2026-02-14"),
	...overrides,
})

describe("SubjectCard", () => {
	describe("基本表示", () => {
		it("教科名を表示する", () => {
			render(<SubjectCard understanding={createMockUnderstanding()} />)
			expect(screen.getByText("算数")).toBeInTheDocument()
		})

		it("トピック名を表示する", () => {
			render(<SubjectCard understanding={createMockUnderstanding()} />)
			expect(screen.getByText("かけ算")).toBeInTheDocument()
		})
	})

	describe("習熟度レベルバー", () => {
		it("レベル値を表示する", () => {
			render(<SubjectCard understanding={createMockUnderstanding({ level: 7 })} />)
			expect(screen.getByText("7")).toBeInTheDocument()
			expect(screen.getByText("/ 10")).toBeInTheDocument()
		})

		it("progressbarのaria属性が正しい", () => {
			render(<SubjectCard understanding={createMockUnderstanding({ level: 5 })} />)
			const progressBar = screen.getByRole("progressbar")
			expect(progressBar).toHaveAttribute("aria-valuenow", "5")
			expect(progressBar).toHaveAttribute("aria-valuemin", "0")
			expect(progressBar).toHaveAttribute("aria-valuemax", "10")
		})
	})

	describe("トレンドバッジ", () => {
		it("improvingトレンドを表示する", () => {
			render(<SubjectCard understanding={createMockUnderstanding({ trend: "improving" })} />)
			expect(screen.getByText("上がっている")).toBeInTheDocument()
		})

		it("stableトレンドを表示する", () => {
			render(<SubjectCard understanding={createMockUnderstanding({ trend: "stable" })} />)
			expect(screen.getByText("安定")).toBeInTheDocument()
		})

		it("decliningトレンドを表示する", () => {
			render(<SubjectCard understanding={createMockUnderstanding({ trend: "declining" })} />)
			expect(screen.getByText("がんばろう")).toBeInTheDocument()
		})
	})

	describe("得意な点", () => {
		it("得意な点を緑タグで表示する", () => {
			render(
				<SubjectCard
					understanding={createMockUnderstanding({ strongPoints: ["たし算", "ひき算"] })}
				/>,
			)
			expect(screen.getByText("たし算")).toBeInTheDocument()
			expect(screen.getByText("ひき算")).toBeInTheDocument()
		})

		it("得意な点が空の場合はセクションを表示しない", () => {
			render(<SubjectCard understanding={createMockUnderstanding({ strongPoints: [] })} />)
			expect(screen.queryByText("とくいなところ")).not.toBeInTheDocument()
		})
	})

	describe("苦手な点", () => {
		it("苦手な点をオレンジタグで表示する", () => {
			render(
				<SubjectCard understanding={createMockUnderstanding({ weakPoints: ["くり上がり"] })} />,
			)
			expect(screen.getByText("くり上がり")).toBeInTheDocument()
		})

		it("苦手な点が空の場合はセクションを表示しない", () => {
			render(<SubjectCard understanding={createMockUnderstanding({ weakPoints: [] })} />)
			expect(screen.queryByText("がんばるところ")).not.toBeInTheDocument()
		})
	})

	describe("アクセシビリティ", () => {
		it("教科カードにaria-labelがある", () => {
			render(<SubjectCard understanding={createMockUnderstanding()} />)
			expect(screen.getByLabelText("算数 - かけ算")).toBeInTheDocument()
		})
	})
})
