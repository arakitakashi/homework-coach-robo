import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"

// ホームページコンポーネントをテスト用にインポート
// 実際のページはServer Componentなので、Client Component版を作成してテスト
import { HomeContent } from "../../src/app/HomeContent"

// useRouterをモック
const mockPush = vi.fn()
vi.mock("next/navigation", () => ({
	useRouter: () => ({
		push: mockPush,
	}),
}))

describe("HomeContent", () => {
	beforeEach(() => {
		mockPush.mockClear()
	})

	it("renders welcome message", () => {
		render(<HomeContent />)
		expect(screen.getByText(/宿題コーチロボット/i)).toBeInTheDocument()
	})

	it("renders start button", () => {
		render(<HomeContent />)
		expect(screen.getByRole("button", { name: /はじめる/i })).toBeInTheDocument()
	})

	it("renders character selection", () => {
		render(<HomeContent />)
		expect(screen.getByText(/キャラクターを選んでね/i)).toBeInTheDocument()
	})

	it("shows robot character option", () => {
		render(<HomeContent />)
		expect(screen.getByRole("button", { name: /ロボット/i })).toBeInTheDocument()
	})

	it("navigates to session when start button clicked", async () => {
		const user = userEvent.setup()
		render(<HomeContent />)

		const startButton = screen.getByRole("button", { name: /はじめる/i })
		await user.click(startButton)

		expect(mockPush).toHaveBeenCalledWith(expect.stringContaining("/session"))
	})

	it("allows character selection", async () => {
		const user = userEvent.setup()
		render(<HomeContent />)

		const robotButton = screen.getByRole("button", { name: /ロボット/i })
		await user.click(robotButton)

		// 選択されたキャラクターが強調表示される
		expect(robotButton).toHaveAttribute("aria-pressed", "true")
	})

	it("has child-friendly design (large buttons)", () => {
		render(<HomeContent />)
		const startButton = screen.getByRole("button", { name: /はじめる/i })
		// ボタンには大きなサイズのクラスがある
		expect(startButton).toHaveClass("text-xl")
	})

	it("is accessible", () => {
		render(<HomeContent />)
		// メインコンテンツ領域がある
		expect(screen.getByRole("main")).toBeInTheDocument()
	})
})
