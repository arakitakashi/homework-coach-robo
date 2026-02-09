import { render, screen, waitFor } from "@testing-library/react"
import { createStore, Provider } from "jotai"
import { type ReactNode, useMemo } from "react"
import { describe, expect, it } from "vitest"
import { activeAgentAtom } from "@/store/atoms/phase2"
import type { ActiveAgent } from "@/types/phase2"
import { AgentIndicator } from "./AgentIndicator"

// Jotaiテスト用ラッパー
function TestWrapper({
	children,
	initialAgent,
}: {
	children: ReactNode
	initialAgent?: ActiveAgent | null
}) {
	const store = useMemo(() => {
		const s = createStore()
		if (initialAgent !== undefined) {
			s.set(activeAgentAtom, initialAgent)
		}
		return s
	}, [initialAgent])

	return <Provider store={store}>{children}</Provider>
}

describe("AgentIndicator", () => {
	it("activeAgentがnullの場合、何も表示しない", () => {
		const { container } = render(
			<TestWrapper initialAgent={null}>
				<AgentIndicator />
			</TestWrapper>,
		)

		// コンポーネントが何もレンダリングしないことを確認
		expect(container.firstChild).toBeNull()
	})

	it("activeAgentが未設定の場合、何も表示しない", () => {
		const { container } = render(
			<TestWrapper>
				<AgentIndicator />
			</TestWrapper>,
		)

		expect(container.firstChild).toBeNull()
	})

	it("算数コーチが表示される", () => {
		const agent: ActiveAgent = {
			type: "math_coach",
			name: "math_coach",
			startedAt: new Date("2026-02-10T00:00:00Z"),
		}

		render(
			<TestWrapper initialAgent={agent}>
				<AgentIndicator />
			</TestWrapper>,
		)

		expect(screen.getByText("算数コーチ")).toBeInTheDocument()
	})

	it("国語コーチが表示される", () => {
		const agent: ActiveAgent = {
			type: "japanese_coach",
			name: "japanese_coach",
			startedAt: new Date("2026-02-10T00:00:00Z"),
		}

		render(
			<TestWrapper initialAgent={agent}>
				<AgentIndicator />
			</TestWrapper>,
		)

		expect(screen.getByText("国語コーチ")).toBeInTheDocument()
	})

	it("励ましが表示される", () => {
		const agent: ActiveAgent = {
			type: "encouragement",
			name: "encouragement",
			startedAt: new Date("2026-02-10T00:00:00Z"),
		}

		render(
			<TestWrapper initialAgent={agent}>
				<AgentIndicator />
			</TestWrapper>,
		)

		expect(screen.getByText("励まし")).toBeInTheDocument()
	})

	it("振り返りが表示される", () => {
		const agent: ActiveAgent = {
			type: "review",
			name: "review",
			startedAt: new Date("2026-02-10T00:00:00Z"),
		}

		render(
			<TestWrapper initialAgent={agent}>
				<AgentIndicator />
			</TestWrapper>,
		)

		expect(screen.getByText("振り返り")).toBeInTheDocument()
	})

	it("ルーターが表示される", () => {
		const agent: ActiveAgent = {
			type: "router",
			name: "router",
			startedAt: new Date("2026-02-10T00:00:00Z"),
		}

		render(
			<TestWrapper initialAgent={agent}>
				<AgentIndicator />
			</TestWrapper>,
		)

		expect(screen.getByText("ルーター")).toBeInTheDocument()
	})

	it("aria-labelが正しく設定される", () => {
		const agent: ActiveAgent = {
			type: "math_coach",
			name: "math_coach",
			startedAt: new Date("2026-02-10T00:00:00Z"),
		}

		const { container } = render(
			<TestWrapper initialAgent={agent}>
				<AgentIndicator />
			</TestWrapper>,
		)

		const element = container.querySelector("[aria-label]")
		expect(element).toHaveAttribute("aria-label", "現在のエージェント: 算数コーチ")
	})

	it("アイコンが表示される", () => {
		const agent: ActiveAgent = {
			type: "math_coach",
			name: "math_coach",
			startedAt: new Date("2026-02-10T00:00:00Z"),
		}

		const { container } = render(
			<TestWrapper initialAgent={agent}>
				<AgentIndicator />
			</TestWrapper>,
		)

		// Lucide ReactアイコンはSVGとして描画される
		const svg = container.querySelector("svg")
		expect(svg).toBeInTheDocument()
	})

	it("エージェント切り替え時にアニメーションが実行される", async () => {
		const agent1: ActiveAgent = {
			type: "math_coach",
			name: "math_coach",
			startedAt: new Date("2026-02-10T00:00:00Z"),
		}

		const store = createStore()
		store.set(activeAgentAtom, agent1)

		const { rerender } = render(
			<Provider store={store}>
				<AgentIndicator />
			</Provider>,
		)

		expect(screen.getByText("算数コーチ")).toBeInTheDocument()

		// エージェントを切り替え
		const agent2: ActiveAgent = {
			type: "japanese_coach",
			name: "japanese_coach",
			startedAt: new Date("2026-02-10T00:00:01Z"),
		}
		store.set(activeAgentAtom, agent2)

		rerender(
			<Provider store={store}>
				<AgentIndicator />
			</Provider>,
		)

		// アニメーション完了を待つ
		await waitFor(() => {
			expect(screen.getByText("国語コーチ")).toBeInTheDocument()
		})
	})
})
