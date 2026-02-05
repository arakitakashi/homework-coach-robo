"use client"

import { type FormEvent, type KeyboardEvent, useCallback, useState } from "react"

/** TextInputのprops */
export interface TextInputProps {
	/** 送信時のコールバック */
	onSubmit: (text: string) => void
	/** 無効化 */
	disabled?: boolean
	/** プレースホルダー */
	placeholder?: string
}

/**
 * テキスト入力コンポーネント
 *
 * 小学校低学年向けのシンプルなテキスト入力UI。
 * 送信ボタンまたはEnterキーでメッセージを送信できる。
 */
export function TextInput({
	onSubmit,
	disabled = false,
	placeholder = "ここにかいてね",
}: TextInputProps) {
	const [value, setValue] = useState("")

	const handleSubmit = useCallback(
		(e?: FormEvent) => {
			e?.preventDefault()

			const trimmedValue = value.trim()
			if (!trimmedValue || disabled) {
				return
			}

			onSubmit(trimmedValue)
			setValue("")
		},
		[value, disabled, onSubmit],
	)

	const handleKeyDown = useCallback(
		(e: KeyboardEvent<HTMLInputElement>) => {
			if (e.key === "Enter" && !disabled) {
				e.preventDefault()
				handleSubmit()
			}
		},
		[disabled, handleSubmit],
	)

	return (
		<form onSubmit={handleSubmit} className="flex w-full gap-2">
			<input
				type="text"
				value={value}
				onChange={(e) => setValue(e.target.value)}
				onKeyDown={handleKeyDown}
				disabled={disabled}
				placeholder={placeholder}
				aria-label="メッセージ入力"
				className={`
					flex-1 rounded-xl border-2 border-gray-200 px-4 py-3
					text-lg transition-colors
					placeholder:text-gray-400
					focus:border-blue-400 focus:outline-none
					disabled:cursor-not-allowed disabled:bg-gray-100 disabled:text-gray-500
				`}
			/>
			<button
				type="submit"
				disabled={disabled || !value.trim()}
				aria-label="送信"
				className={`
					rounded-xl bg-blue-500 px-6 py-3
					text-lg font-bold text-white
					transition-colors
					hover:bg-blue-600
					focus:outline-none focus:ring-4 focus:ring-blue-300
					disabled:cursor-not-allowed disabled:bg-gray-300
				`}
			>
				送る
			</button>
		</form>
	)
}
