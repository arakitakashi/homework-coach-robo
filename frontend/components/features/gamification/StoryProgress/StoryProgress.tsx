/**
 * ストーリー進行状況表示コンポーネント
 */

"use client"

import { useAtomValue } from "jotai"
import { gamificationStateAtom } from "@/store/atoms/gamification"

/**
 * チャプターIDから番号を抽出
 */
function getChapterNumber(chapterId: string): number {
	const match = chapterId.match(/\d+/)
	return match ? Number.parseInt(match[0], 10) : 1
}

/**
 * StoryProgress コンポーネント
 *
 * ストーリーチャプターの進行状況を表示します
 */
export function StoryProgress() {
	const { currentChapter, totalPoints } = useAtomValue(gamificationStateAtom)

	const chapterNumber = getChapterNumber(currentChapter.id)
	const progress = Math.min(totalPoints, currentChapter.requiredPoints)
	const percentage = (progress / currentChapter.requiredPoints) * 100

	return (
		<section
			aria-label="ストーリー進行状況"
			className="p-4 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg border border-indigo-200"
		>
			{/* チャプターヘッダー */}
			<div className="flex items-center justify-between mb-3">
				<div className="flex items-center gap-2">
					<span className="text-2xl">📖</span>
					<h3 className="text-lg font-bold text-indigo-700">
						Chapter {chapterNumber}: {currentChapter.title}
					</h3>
				</div>

				{/* 完了バッジ */}
				{currentChapter.completed && (
					<span className="px-3 py-1 bg-green-500 text-white text-sm font-bold rounded-full">
						✓ 完了
					</span>
				)}
			</div>

			{/* チャプター説明 */}
			<p className="text-sm text-gray-600 mb-3">{currentChapter.description}</p>

			{/* 進捗テキスト */}
			<div className="flex items-center gap-2 mb-2">
				<span className="text-sm font-semibold text-gray-700">
					{progress} / {currentChapter.requiredPoints} pts
				</span>
			</div>

			{/* プログレスバー */}
			<div
				role="progressbar"
				aria-label={`Chapter ${chapterNumber} の進行度`}
				aria-valuenow={progress}
				aria-valuemin={0}
				aria-valuemax={currentChapter.requiredPoints}
				className="w-full h-3 bg-gray-200 rounded-full overflow-hidden"
			>
				<div
					className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 transition-all duration-500"
					style={{ width: `${percentage}%` }}
				/>
			</div>
		</section>
	)
}
