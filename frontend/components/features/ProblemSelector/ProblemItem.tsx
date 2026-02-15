/**
 * ProblemItem コンポーネント
 *
 * 個別問題のカード表示。大きなタッチターゲット（min-h-[64px]）で
 * 小学校低学年でも操作しやすいデザイン。
 * 問題番号 + テキスト + ステータスバッジを表示。
 */

"use client"

import type { ProblemState, ProblemStatus } from "@/store/atoms/multiProblem"

/** ステータスに応じたスタイルを返す */
function getStatusStyle(status: ProblemStatus): {
	bg: string
	border: string
	badge: string | null
} {
	switch (status) {
		case "completed":
			return {
				bg: "bg-green-50",
				border: "border-green-300",
				badge: "✓",
			}
		case "in_progress":
			return {
				bg: "bg-yellow-50",
				border: "border-yellow-300",
				badge: null,
			}
		case "skipped":
			return {
				bg: "bg-gray-50",
				border: "border-gray-300",
				badge: null,
			}
		default:
			return {
				bg: "bg-white",
				border: "border-gray-200",
				badge: null,
			}
	}
}

interface ProblemItemProps {
	/** 問題の状態 */
	problemState: ProblemState
	/** 1ベースの問題番号 */
	number: number
	/** 選択時のコールバック */
	onSelect: () => void
}

export function ProblemItem({ problemState, number, onSelect }: ProblemItemProps) {
	const style = getStatusStyle(problemState.status)

	return (
		<li data-testid={`problem-item-${problemState.id}`}>
			<button
				type="button"
				className={`flex min-h-[64px] w-full items-center gap-3 rounded-xl border-2 px-4 py-3 text-left transition-colors hover:shadow-md active:shadow-sm ${style.bg} ${style.border}`}
				onClick={onSelect}
			>
				{/* 問題番号 */}
				<span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-blue-500 text-lg font-bold text-white">
					{number}
				</span>

				{/* 問題テキスト */}
				<span className="flex-1 text-lg font-medium text-gray-800 line-clamp-2">
					{problemState.problem.text}
				</span>

				{/* ステータスバッジ */}
				{style.badge && (
					<span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-green-500 text-lg font-bold text-white">
						{style.badge}
					</span>
				)}
			</button>
		</li>
	)
}
