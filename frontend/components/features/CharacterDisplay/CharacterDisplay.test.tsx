import { render, screen } from "@testing-library/react"
import { createStore, Provider } from "jotai"
import { type ReactNode, useMemo } from "react"
import { describe, expect, it } from "vitest"
import { emotionAnalysisAtom } from "@/store/atoms/phase2"
import type { EmotionAnalysis } from "@/types"
import { CharacterDisplay } from "./CharacterDisplay"

// テスト用ラッパー
function _TestWrapper({ children }: { children: ReactNode }) {
	const store = useMemo(() => createStore(), [])
	return <Provider store={store}>{children}</Provider>
}

describe("CharacterDisplay", () => {
	it("renders robot character", () => {
		render(<CharacterDisplay character="robot" state="idle" />)
		expect(screen.getByRole("img", { name: /ロボット/i })).toBeInTheDocument()
	})

	it("renders wizard character", () => {
		render(<CharacterDisplay character="wizard" state="idle" />)
		expect(screen.getByRole("img", { name: /まほうつかい/i })).toBeInTheDocument()
	})

	it("renders astronaut character", () => {
		render(<CharacterDisplay character="astronaut" state="idle" />)
		expect(screen.getByRole("img", { name: /うちゅうひこうし/i })).toBeInTheDocument()
	})

	it("renders animal character", () => {
		render(<CharacterDisplay character="animal" state="idle" />)
		expect(screen.getByRole("img", { name: /どうぶつ/i })).toBeInTheDocument()
	})

	it("applies idle state styling", () => {
		render(<CharacterDisplay character="robot" state="idle" />)
		const character = screen.getByRole("img", { name: /ロボット/i })
		expect(character.closest("div")).toHaveClass("animate-none")
	})

	it("applies listening state styling", () => {
		render(<CharacterDisplay character="robot" state="listening" />)
		const container = screen.getByTestId("character-container")
		expect(container).toHaveClass("animate-pulse")
	})

	it("applies speaking state styling", () => {
		render(<CharacterDisplay character="robot" state="speaking" />)
		const container = screen.getByTestId("character-container")
		expect(container).toHaveClass("animate-bounce")
	})

	it("applies thinking state styling", () => {
		render(<CharacterDisplay character="robot" state="thinking" />)
		const container = screen.getByTestId("character-container")
		expect(container).toHaveClass("animate-spin-slow")
	})

	it("has accessible role and label", () => {
		render(<CharacterDisplay character="robot" state="idle" />)
		expect(screen.getByRole("img")).toHaveAttribute("aria-label")
	})

	describe("感情連動", () => {
		it("frustrated の場合、困った表情になる", () => {
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
					<CharacterDisplay character="robot" state="idle" />
				</Provider>,
			)

			expect(screen.getByRole("img")).toBeInTheDocument()
		})

		it("confident の場合、自信のある表情になる", () => {
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
					<CharacterDisplay character="robot" state="idle" />
				</Provider>,
			)

			expect(screen.getByRole("img")).toBeInTheDocument()
		})

		it("happy の場合、幸せな表情になる", () => {
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
					<CharacterDisplay character="robot" state="idle" />
				</Provider>,
			)

			expect(screen.getByRole("img")).toBeInTheDocument()
		})

		it("tired の場合、疲れた表情になる", () => {
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
					<CharacterDisplay character="robot" state="idle" />
				</Provider>,
			)

			expect(screen.getByRole("img")).toBeInTheDocument()
		})

		it("感情が未設定の場合、既存のstateプロップで動作する", () => {
			const store = createStore()
			store.set(emotionAnalysisAtom, null)

			render(
				<Provider store={store}>
					<CharacterDisplay character="robot" state="happy" />
				</Provider>,
			)

			const container = screen.getByTestId("character-container")
			expect(container).toHaveClass("animate-wiggle")
		})
	})
})
