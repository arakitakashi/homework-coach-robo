import { render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"
import NotFoundPage from "./not-found"

describe("NotFoundPage", () => {
	it("404タイトルが表示される", () => {
		render(<NotFoundPage />)
		expect(screen.getByRole("heading", { name: /404/i })).toBeInTheDocument()
	})

	it("日本語のメッセージが表示される", () => {
		render(<NotFoundPage />)
		expect(screen.getByText("このページは みつからないよ")).toBeInTheDocument()
	})

	it("トップページへのリンクが表示される", () => {
		render(<NotFoundPage />)
		const link = screen.getByRole("link", { name: /トップページにもどる/i })
		expect(link).toBeInTheDocument()
		expect(link).toHaveAttribute("href", "/")
	})

	it("キャラクター画像が表示される", () => {
		render(<NotFoundPage />)
		// キャラクター画像の代わりにemojiを使用しているため、テキストで確認
		expect(screen.getByText("🤖")).toBeInTheDocument()
	})
})
