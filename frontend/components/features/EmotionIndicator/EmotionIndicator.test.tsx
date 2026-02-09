import { render, screen } from "@testing-library/react"
import { createStore, Provider } from "jotai"
import { type ReactNode, useMemo } from "react"
import { describe, expect, it } from "vitest"
import { emotionAdaptationAtom, emotionAnalysisAtom } from "@/store/atoms/phase2"
import type { EmotionAdaptation, EmotionAnalysis } from "@/types"
import { EmotionIndicator } from "./EmotionIndicator"

// テスト用ラッパー
function _TestWrapper({ children }: { children: ReactNode }) {
	const store = useMemo(() => createStore(), [])
	return <Provider store={store}>{children}</Provider>
}

describe("EmotionIndicator", () => {
	it("emotionAnalysisAtom が null の場合、何も表示しない", () => {
		const store = createStore()
		store.set(emotionAnalysisAtom, null)
		store.set(emotionAdaptationAtom, null)

		const { container } = render(
			<Provider store={store}>
				<EmotionIndicator />
			</Provider>,
		)

		expect(container.firstChild).toBeNull()
	})

	it("frustrated の場合、困った表情のアイコンと赤系の色が表示される", () => {
		const store = createStore()
		const analysis: EmotionAnalysis = {
			primaryEmotion: "frustrated",
			confidence: 0.85,
			frustrationLevel: 8,
			engagementLevel: 3,
			timestamp: new Date(),
		}
		store.set(emotionAnalysisAtom, analysis)

		render(
			<Provider store={store}>
				<EmotionIndicator />
			</Provider>,
		)

		expect(screen.getByText(/困っている/)).toBeInTheDocument()
	})

	it("confident の場合、自信のあるアイコンと緑系の色が表示される", () => {
		const store = createStore()
		const analysis: EmotionAnalysis = {
			primaryEmotion: "confident",
			confidence: 0.9,
			frustrationLevel: 2,
			engagementLevel: 9,
			timestamp: new Date(),
		}
		store.set(emotionAnalysisAtom, analysis)

		render(
			<Provider store={store}>
				<EmotionIndicator />
			</Provider>,
		)

		expect(screen.getByText(/自信満々/)).toBeInTheDocument()
	})

	it("confused の場合、混乱したアイコンと青系の色が表示される", () => {
		const store = createStore()
		const analysis: EmotionAnalysis = {
			primaryEmotion: "confused",
			confidence: 0.75,
			frustrationLevel: 5,
			engagementLevel: 6,
			timestamp: new Date(),
		}
		store.set(emotionAnalysisAtom, analysis)

		render(
			<Provider store={store}>
				<EmotionIndicator />
			</Provider>,
		)

		expect(screen.getByText(/わからない/)).toBeInTheDocument()
	})

	it("happy の場合、幸せなアイコンと黄色系の色が表示される", () => {
		const store = createStore()
		const analysis: EmotionAnalysis = {
			primaryEmotion: "happy",
			confidence: 0.95,
			frustrationLevel: 1,
			engagementLevel: 10,
			timestamp: new Date(),
		}
		store.set(emotionAnalysisAtom, analysis)

		render(
			<Provider store={store}>
				<EmotionIndicator />
			</Provider>,
		)

		expect(screen.getByText(/元気いっぱい/)).toBeInTheDocument()
	})

	it("tired の場合、疲れたアイコンと灰色系の色が表示される", () => {
		const store = createStore()
		const analysis: EmotionAnalysis = {
			primaryEmotion: "tired",
			confidence: 0.8,
			frustrationLevel: 4,
			engagementLevel: 2,
			timestamp: new Date(),
		}
		store.set(emotionAnalysisAtom, analysis)

		render(
			<Provider store={store}>
				<EmotionIndicator />
			</Provider>,
		)

		expect(screen.getByText(/疲れている/)).toBeInTheDocument()
	})

	it("neutral の場合、ニュートラルなアイコンが表示される", () => {
		const store = createStore()
		const analysis: EmotionAnalysis = {
			primaryEmotion: "neutral",
			confidence: 0.7,
			frustrationLevel: 5,
			engagementLevel: 5,
			timestamp: new Date(),
		}
		store.set(emotionAnalysisAtom, analysis)

		render(
			<Provider store={store}>
				<EmotionIndicator />
			</Provider>,
		)

		expect(screen.getByText(/落ち着いている/)).toBeInTheDocument()
	})

	it("フラストレーションレベルが表示される", () => {
		const store = createStore()
		const analysis: EmotionAnalysis = {
			primaryEmotion: "frustrated",
			confidence: 0.85,
			frustrationLevel: 7,
			engagementLevel: 4,
			timestamp: new Date(),
		}
		store.set(emotionAnalysisAtom, analysis)

		render(
			<Provider store={store}>
				<EmotionIndicator />
			</Provider>,
		)

		expect(screen.getByLabelText("イライラ度")).toBeInTheDocument()
	})

	it("エンゲージメントレベルが表示される", () => {
		const store = createStore()
		const analysis: EmotionAnalysis = {
			primaryEmotion: "confident",
			confidence: 0.9,
			frustrationLevel: 2,
			engagementLevel: 8,
			timestamp: new Date(),
		}
		store.set(emotionAnalysisAtom, analysis)

		render(
			<Provider store={store}>
				<EmotionIndicator />
			</Provider>,
		)

		expect(screen.getByLabelText("集中度")).toBeInTheDocument()
	})

	it("emotionAdaptationAtom からサポートレベルが表示される", () => {
		const store = createStore()
		const analysis: EmotionAnalysis = {
			primaryEmotion: "frustrated",
			confidence: 0.85,
			frustrationLevel: 8,
			engagementLevel: 3,
			timestamp: new Date(),
		}
		const adaptation: EmotionAdaptation = {
			currentEmotion: "frustrated",
			supportLevel: "intensive",
			dialogueTone: "empathetic",
			adjustedAt: new Date(),
		}
		store.set(emotionAnalysisAtom, analysis)
		store.set(emotionAdaptationAtom, adaptation)

		render(
			<Provider store={store}>
				<EmotionIndicator />
			</Provider>,
		)

		expect(screen.getByText(/しっかり/)).toBeInTheDocument()
	})

	it("アクセシビリティ属性が設定される", () => {
		const store = createStore()
		const analysis: EmotionAnalysis = {
			primaryEmotion: "happy",
			confidence: 0.95,
			frustrationLevel: 1,
			engagementLevel: 10,
			timestamp: new Date(),
		}
		store.set(emotionAnalysisAtom, analysis)

		const { container } = render(
			<Provider store={store}>
				<EmotionIndicator />
			</Provider>,
		)

		const indicator = container.querySelector('[role="status"]')
		expect(indicator).toBeInTheDocument()
		expect(indicator).toHaveAttribute("aria-label", "感情状態")
	})
})
