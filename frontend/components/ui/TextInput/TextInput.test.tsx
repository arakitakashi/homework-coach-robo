/**
 * TextInput コンポーネントテスト
 */

import { fireEvent, render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import { TextInput } from "./TextInput"

describe("TextInput", () => {
	const mockOnSubmit = vi.fn()

	beforeEach(() => {
		mockOnSubmit.mockClear()
	})

	describe("レンダリング", () => {
		it("テキスト入力フィールドが表示される", () => {
			render(<TextInput onSubmit={mockOnSubmit} />)

			expect(screen.getByRole("textbox")).toBeInTheDocument()
		})

		it("送信ボタンが表示される", () => {
			render(<TextInput onSubmit={mockOnSubmit} />)

			expect(screen.getByRole("button", { name: /送信|送る/i })).toBeInTheDocument()
		})

		it("プレースホルダーが表示される", () => {
			render(<TextInput onSubmit={mockOnSubmit} placeholder="メッセージを入力" />)

			expect(screen.getByPlaceholderText("メッセージを入力")).toBeInTheDocument()
		})

		it("デフォルトのプレースホルダーが表示される", () => {
			render(<TextInput onSubmit={mockOnSubmit} />)

			expect(screen.getByPlaceholderText("ここにかいてね")).toBeInTheDocument()
		})
	})

	describe("入力と送信", () => {
		it("テキストを入力できる", async () => {
			const user = userEvent.setup()
			render(<TextInput onSubmit={mockOnSubmit} />)

			const input = screen.getByRole("textbox")
			await user.type(input, "こんにちは")

			expect(input).toHaveValue("こんにちは")
		})

		it("送信ボタンクリックでonSubmitが呼ばれる", async () => {
			const user = userEvent.setup()
			render(<TextInput onSubmit={mockOnSubmit} />)

			const input = screen.getByRole("textbox")
			await user.type(input, "テストメッセージ")

			const button = screen.getByRole("button", { name: /送信|送る/i })
			await user.click(button)

			expect(mockOnSubmit).toHaveBeenCalledWith("テストメッセージ")
		})

		it("Enterキーで送信できる", async () => {
			const user = userEvent.setup()
			render(<TextInput onSubmit={mockOnSubmit} />)

			const input = screen.getByRole("textbox")
			await user.type(input, "Enterで送信{enter}")

			expect(mockOnSubmit).toHaveBeenCalledWith("Enterで送信")
		})

		it("送信後に入力がクリアされる", async () => {
			const user = userEvent.setup()
			render(<TextInput onSubmit={mockOnSubmit} />)

			const input = screen.getByRole("textbox")
			await user.type(input, "テスト")

			const button = screen.getByRole("button", { name: /送信|送る/i })
			await user.click(button)

			expect(input).toHaveValue("")
		})

		it("空文字の場合は送信されない", async () => {
			const user = userEvent.setup()
			render(<TextInput onSubmit={mockOnSubmit} />)

			const button = screen.getByRole("button", { name: /送信|送る/i })
			await user.click(button)

			expect(mockOnSubmit).not.toHaveBeenCalled()
		})

		it("空白のみの場合は送信されない", async () => {
			const user = userEvent.setup()
			render(<TextInput onSubmit={mockOnSubmit} />)

			const input = screen.getByRole("textbox")
			await user.type(input, "   ")

			const button = screen.getByRole("button", { name: /送信|送る/i })
			await user.click(button)

			expect(mockOnSubmit).not.toHaveBeenCalled()
		})
	})

	describe("disabled状態", () => {
		it("disabledの場合、入力が無効になる", () => {
			render(<TextInput onSubmit={mockOnSubmit} disabled />)

			expect(screen.getByRole("textbox")).toBeDisabled()
		})

		it("disabledの場合、ボタンが無効になる", () => {
			render(<TextInput onSubmit={mockOnSubmit} disabled />)

			expect(screen.getByRole("button", { name: /送信|送る/i })).toBeDisabled()
		})

		it("disabledの場合、Enterキーで送信できない", async () => {
			const _user = userEvent.setup()
			render(<TextInput onSubmit={mockOnSubmit} disabled />)

			const input = screen.getByRole("textbox")
			// disabledなので入力できないが、念のためフォーカスを試みる
			fireEvent.keyDown(input, { key: "Enter" })

			expect(mockOnSubmit).not.toHaveBeenCalled()
		})
	})

	describe("アクセシビリティ", () => {
		it("入力フィールドにaria-labelがある", () => {
			render(<TextInput onSubmit={mockOnSubmit} />)

			const input = screen.getByRole("textbox")
			expect(input).toHaveAttribute("aria-label")
		})

		it("送信ボタンにaria-labelがある", () => {
			render(<TextInput onSubmit={mockOnSubmit} />)

			const button = screen.getByRole("button")
			expect(button).toHaveAccessibleName()
		})
	})
})
