import { render, screen } from "@testing-library/react"
import { createStore, Provider } from "jotai"
import { describe, expect, it } from "vitest"
import { learningProfileAtom } from "@/store/atoms/phase2"
import type { ChildLearningProfile } from "@/types/phase2"
import { LearningProfile } from "./LearningProfile"

/** テスト用の学習プロファイルデータ */
const createMockProfile = (
	overrides: Partial<ChildLearningProfile> = {},
): ChildLearningProfile => ({
	childId: "child-1",
	thinking: {
		persistenceScore: 70,
		independenceScore: 60,
		reflectionQuality: 80,
		hintDependency: 30,
		updatedAt: new Date("2026-02-14"),
	},
	subjects: [
		{
			subject: "算数",
			topic: "かけ算",
			level: 7,
			trend: "improving",
			weakPoints: ["くり上がり"],
			strongPoints: ["たし算"],
			assessedAt: new Date("2026-02-14"),
		},
		{
			subject: "国語",
			topic: "漢字",
			level: 5,
			trend: "stable",
			weakPoints: [],
			strongPoints: ["ひらがな"],
			assessedAt: new Date("2026-02-14"),
		},
	],
	totalSessions: 10,
	totalProblemsSolved: 25,
	createdAt: new Date("2026-01-01"),
	updatedAt: new Date("2026-02-14"),
	...overrides,
})

describe("LearningProfile", () => {
	describe("null state", () => {
		it("learningProfileAtom が null の場合、何も表示しない", () => {
			const store = createStore()
			store.set(learningProfileAtom, null)

			const { container } = render(
				<Provider store={store}>
					<LearningProfile />
				</Provider>,
			)

			expect(container.firstChild).toBeNull()
		})
	})

	describe("ProfileSummary 表示", () => {
		it("セッション数と問題解決数を表示する", () => {
			const store = createStore()
			store.set(learningProfileAtom, createMockProfile())

			render(
				<Provider store={store}>
					<LearningProfile />
				</Provider>,
			)

			expect(screen.getByText("10")).toBeInTheDocument()
			expect(screen.getByText("回のセッション")).toBeInTheDocument()
			expect(screen.getByText("25")).toBeInTheDocument()
			expect(screen.getByText("問クリア")).toBeInTheDocument()
		})
	})

	describe("ThinkingTendenciesDisplay 表示", () => {
		it("思考の傾向セクションを表示する", () => {
			const store = createStore()
			store.set(learningProfileAtom, createMockProfile())

			render(
				<Provider store={store}>
					<LearningProfile />
				</Provider>,
			)

			expect(screen.getByLabelText("思考の傾向")).toBeInTheDocument()
			expect(screen.getByText("粘り強さ")).toBeInTheDocument()
		})
	})

	describe("SubjectCard リスト表示", () => {
		it("教科別理解度を表示する", () => {
			const store = createStore()
			store.set(learningProfileAtom, createMockProfile())

			render(
				<Provider store={store}>
					<LearningProfile />
				</Provider>,
			)

			expect(screen.getByText("算数")).toBeInTheDocument()
			expect(screen.getByText("かけ算")).toBeInTheDocument()
			expect(screen.getByText("国語")).toBeInTheDocument()
			expect(screen.getByText("漢字")).toBeInTheDocument()
		})

		it("subjects が空の場合「まだデータがありません」と表示する", () => {
			const store = createStore()
			store.set(learningProfileAtom, createMockProfile({ subjects: [] }))

			render(
				<Provider store={store}>
					<LearningProfile />
				</Provider>,
			)

			expect(screen.getByText("まだデータがありません")).toBeInTheDocument()
		})
	})

	describe("アクセシビリティ", () => {
		it("学習プロファイル全体にaria-labelがある", () => {
			const store = createStore()
			store.set(learningProfileAtom, createMockProfile())

			render(
				<Provider store={store}>
					<LearningProfile />
				</Provider>,
			)

			expect(screen.getByLabelText("学習プロファイル")).toBeInTheDocument()
		})
	})
})
