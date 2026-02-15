/**
 * 複数問題管理用 Jotai atoms
 *
 * 宿題プリント撮影時に認識された複数問題の状態管理。
 * ProblemSelectorコンポーネントとSessionContentで使用。
 */

import { atom } from "jotai"
import type { ProblemDetail } from "@/types"

/** 問題の進行状態 */
export type ProblemStatus = "pending" | "in_progress" | "completed" | "skipped"

/** 個別問題の状態 */
export interface ProblemState {
	/** 問題の詳細 */
	problem: ProblemDetail
	/** 一意識別子 */
	id: string
	/** 進行状態 */
	status: ProblemStatus
}

/** 全問題リスト */
export const worksheetProblemsAtom = atom<ProblemState[]>([])

/** 選択中の問題インデックス（null = 未選択） */
export const currentProblemIndexAtom = atom<number | null>(null)

/** 現在の問題（derived） */
export const currentProblemAtom = atom<ProblemState | null>((get) => {
	const problems = get(worksheetProblemsAtom)
	const index = get(currentProblemIndexAtom)
	if (index === null || index < 0 || index >= problems.length) return null
	return problems[index]
})

/** 未完了問題数（derived） - pending + skipped */
export const remainingProblemsCountAtom = atom<number>((get) => {
	return get(worksheetProblemsAtom).filter((p) => p.status === "pending" || p.status === "skipped")
		.length
})

/** 問題セレクタ表示フラグ */
export const showProblemSelectorAtom = atom<boolean>(false)
