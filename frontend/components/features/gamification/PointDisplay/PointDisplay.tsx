/**
 * ポイント・レベル表示コンポーネント
 */

"use client"

import { useAtomValue } from "jotai"
import { gamificationStateAtom } from "@/store/atoms/gamification"

/**
 * レベルアップまでの進捗を計算
 */
function calculateProgress(totalPoints: number, level: number) {
	const pointsPerLevel = 50
	const currentLevelMinPoints = (level - 1) * pointsPerLevel
	const pointsInCurrentLevel = totalPoints - currentLevelMinPoints

	return {
		current: pointsInCurrentLevel,
		max: pointsPerLevel,
		percentage: (pointsInCurrentLevel / pointsPerLevel) * 100,
	}
}

/**
 * PointDisplay コンポーネント
 *
 * 現在のポイント・レベル・レベルアップまでの進捗を表示します
 */
export function PointDisplay() {
	const { totalPoints, level } = useAtomValue(gamificationStateAtom)

	const progress = calculateProgress(totalPoints, level)

	return (
		<div className="flex flex-col gap-2 p-4 bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg border border-purple-200">
			{/* レベル表示 */}
			<div className="flex items-center gap-2">
				<span className="text-2xl">⭐</span>
				<span className="text-lg font-bold text-purple-700">Level {level}</span>
			</div>

			{/* 進捗テキスト */}
			<div className="flex items-center gap-2">
				<span className="text-xl">💎</span>
				<span className="text-sm font-semibold text-gray-700">
					{progress.current} / {progress.max} pts
				</span>
			</div>

			{/* プログレスバー */}
			<div
				role="progressbar"
				aria-label="レベルアップまでの進捗"
				aria-valuenow={progress.current}
				aria-valuemin={0}
				aria-valuemax={progress.max}
				className="w-full h-2 bg-gray-200 rounded-full overflow-hidden"
			>
				<div
					className="h-full bg-gradient-to-r from-purple-500 to-blue-500 transition-all duration-300"
					style={{ width: `${progress.percentage}%` }}
				/>
			</div>
		</div>
	)
}
