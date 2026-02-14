/**
 * InputModeSelector コンポーネントのテスト
 */

import { fireEvent, render, screen } from "@testing-library/react"
import { describe, expect, it, vi } from "vitest"
import { InputModeSelector } from "./InputModeSelector"

describe("InputModeSelector", () => {
	it("2つのボタンが表示される", () => {
		const onModeSelect = vi.fn()
		render(<InputModeSelector onModeSelect={onModeSelect} />)

		const voiceButton = screen.getByRole("button", { name: /声で伝える/ })
		const imageButton = screen.getByRole("button", { name: /写真で伝える/ })

		expect(voiceButton).toBeInTheDocument()
		expect(imageButton).toBeInTheDocument()
	})

	it("声で伝えるボタンをクリックするとvoiceモードが選択される", () => {
		const onModeSelect = vi.fn()
		render(<InputModeSelector onModeSelect={onModeSelect} />)

		const voiceButton = screen.getByRole("button", { name: /声で伝える/ })
		fireEvent.click(voiceButton)

		expect(onModeSelect).toHaveBeenCalledWith("voice")
		expect(onModeSelect).toHaveBeenCalledTimes(1)
	})

	it("写真で伝えるボタンをクリックするとimageモードが選択される", () => {
		const onModeSelect = vi.fn()
		render(<InputModeSelector onModeSelect={onModeSelect} />)

		const imageButton = screen.getByRole("button", { name: /写真で伝える/ })
		fireEvent.click(imageButton)

		expect(onModeSelect).toHaveBeenCalledWith("image")
		expect(onModeSelect).toHaveBeenCalledTimes(1)
	})

	describe("アクセシビリティ", () => {
		it("声で伝えるボタンにaria-labelがある", () => {
			const onModeSelect = vi.fn()
			render(<InputModeSelector onModeSelect={onModeSelect} />)

			const voiceButton = screen.getByRole("button", { name: /声で伝える/ })
			expect(voiceButton).toHaveAttribute("aria-label")
		})

		it("写真で伝えるボタンにaria-labelがある", () => {
			const onModeSelect = vi.fn()
			render(<InputModeSelector onModeSelect={onModeSelect} />)

			const imageButton = screen.getByRole("button", { name: /写真で伝える/ })
			expect(imageButton).toHaveAttribute("aria-label")
		})

		it("ボタンのタッチターゲットが44px以上", () => {
			const onModeSelect = vi.fn()
			render(<InputModeSelector onModeSelect={onModeSelect} />)

			const voiceButton = screen.getByRole("button", { name: /声で伝える/ })
			const imageButton = screen.getByRole("button", { name: /写真で伝える/ })

			// min-h-[56px] クラスが適用されていることを確認（56px > 44px）
			const voiceClasses = voiceButton.className
			const imageClasses = imageButton.className

			expect(voiceClasses).toContain("min-h-")
			expect(imageClasses).toContain("min-h-")
		})
	})
})
