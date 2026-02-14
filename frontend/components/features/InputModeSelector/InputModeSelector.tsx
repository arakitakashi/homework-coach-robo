/**
 * InputModeSelector コンポーネント
 *
 * セッション開始時に入力モード（音声 or 画像）を選択するUIコンポーネント。
 * ターゲットユーザーは小学校低学年のため、大きなボタン・やさしい日本語で構成。
 */

"use client"

/** InputModeSelector のprops */
export interface InputModeSelectorProps {
	/** モード選択時のコールバック */
	onModeSelect: (mode: "voice" | "image") => void
}

/**
 * 入力モード選択コンポーネント
 *
 * セッション開始時に音声入力か画像アップロードかを選択する。
 */
export function InputModeSelector({ onModeSelect }: InputModeSelectorProps) {
	return (
		<div className="flex flex-col items-center gap-6 p-6">
			<p className="text-xl font-bold text-gray-700">どうやってつたえる？</p>

			<div className="flex flex-col gap-4">
				{/* 🎤 声で伝える */}
				<button
					type="button"
					aria-label="声で伝える"
					className="min-h-[56px] min-w-[240px] rounded-2xl bg-blue-500 px-8 py-4 text-xl font-bold text-white shadow-lg hover:bg-blue-600 active:bg-blue-700"
					onClick={() => onModeSelect("voice")}
				>
					🎤 声で伝える
				</button>

				{/* 📷 写真で伝える */}
				<button
					type="button"
					aria-label="写真で伝える"
					className="min-h-[56px] min-w-[240px] rounded-2xl bg-green-500 px-8 py-4 text-xl font-bold text-white shadow-lg hover:bg-green-600 active:bg-green-700"
					onClick={() => onModeSelect("image")}
				>
					📷 写真で伝える
				</button>
			</div>
		</div>
	)
}
