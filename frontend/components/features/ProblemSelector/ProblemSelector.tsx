/**
 * ProblemSelector コンポーネント
 *
 * 画像認識で検出された複数問題を一覧表示し、
 * ユーザーが1つ選択してコーチングセッションを開始するためのUI。
 * ターゲットユーザーは小学校低学年のため、大きなボタン・やさしい日本語で構成。
 */

"use client"

import type { ProblemState } from "@/store/atoms/multiProblem"
import { ProblemItem } from "./ProblemItem"

interface ProblemSelectorProps {
	/** 認識された問題の状態リスト */
	problems: ProblemState[]
	/** 問題選択時のコールバック（0ベースインデックス） */
	onProblemSelect: (index: number) => void
	/** 撮り直しコールバック（省略可能） */
	onRetake?: () => void
}

export function ProblemSelector({ problems, onProblemSelect, onRetake }: ProblemSelectorProps) {
	return (
		<div className="flex flex-col items-center gap-4 p-4">
			{/* ヘッダー */}
			<p className="text-lg font-bold text-gray-700">
				もんだいが {problems.length} こ みつかったよ！
			</p>
			<p className="text-gray-500">やりたいもんだいをえらんでね</p>

			{/* 問題リスト */}
			<ul className="flex w-full max-w-[500px] flex-col gap-3">
				{problems.map((problemState, index) => (
					<ProblemItem
						key={problemState.id}
						problemState={problemState}
						number={index + 1}
						onSelect={() => onProblemSelect(index)}
					/>
				))}
			</ul>

			{/* とりなおすボタン */}
			{onRetake && (
				<button
					type="button"
					aria-label="とりなおす"
					className="min-h-[48px] rounded-2xl bg-gray-400 px-6 py-3 text-lg font-bold text-white shadow hover:bg-gray-500 active:bg-gray-600"
					onClick={onRetake}
				>
					とりなおす
				</button>
			)}
		</div>
	)
}
