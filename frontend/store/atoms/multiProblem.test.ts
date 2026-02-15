/**
 * 複数問題管理用Jotai atoms テスト
 *
 * worksheetProblemsAtom, currentProblemIndexAtom,
 * currentProblemAtom (derived), remainingProblemsCountAtom (derived),
 * showProblemSelectorAtom の初期値・計算を検証する。
 */

import { createStore } from "jotai"
import { beforeEach, describe, expect, it } from "vitest"
import type { ProblemState } from "./multiProblem"
import {
	currentProblemAtom,
	currentProblemIndexAtom,
	remainingProblemsCountAtom,
	showProblemSelectorAtom,
	worksheetProblemsAtom,
} from "./multiProblem"

describe("multiProblem atoms", () => {
	let store: ReturnType<typeof createStore>

	beforeEach(() => {
		store = createStore()
	})

	describe("worksheetProblemsAtom", () => {
		it("初期値は空配列", () => {
			expect(store.get(worksheetProblemsAtom)).toEqual([])
		})

		it("問題リストをセットできる", () => {
			const problems: ProblemState[] = [
				{
					id: "p1",
					problem: { text: "1+1=?", type: "arithmetic", difficulty: 1 },
					status: "pending",
				},
				{
					id: "p2",
					problem: { text: "2+3=?", type: "arithmetic", difficulty: 1 },
					status: "pending",
				},
			]
			store.set(worksheetProblemsAtom, problems)
			expect(store.get(worksheetProblemsAtom)).toEqual(problems)
		})
	})

	describe("currentProblemIndexAtom", () => {
		it("初期値はnull", () => {
			expect(store.get(currentProblemIndexAtom)).toBeNull()
		})

		it("インデックスをセットできる", () => {
			store.set(currentProblemIndexAtom, 0)
			expect(store.get(currentProblemIndexAtom)).toBe(0)
		})
	})

	describe("currentProblemAtom (derived)", () => {
		it("インデックスがnullの場合はnullを返す", () => {
			store.set(worksheetProblemsAtom, [
				{
					id: "p1",
					problem: { text: "1+1=?", type: "arithmetic", difficulty: 1 },
					status: "pending",
				},
			])
			expect(store.get(currentProblemAtom)).toBeNull()
		})

		it("有効なインデックスの場合は対応する問題を返す", () => {
			const problems: ProblemState[] = [
				{
					id: "p1",
					problem: { text: "1+1=?", type: "arithmetic", difficulty: 1 },
					status: "pending",
				},
				{
					id: "p2",
					problem: { text: "2+3=?", type: "arithmetic", difficulty: 1 },
					status: "in_progress",
				},
			]
			store.set(worksheetProblemsAtom, problems)
			store.set(currentProblemIndexAtom, 1)
			expect(store.get(currentProblemAtom)).toEqual(problems[1])
		})

		it("インデックスが範囲外の場合はnullを返す", () => {
			store.set(worksheetProblemsAtom, [
				{
					id: "p1",
					problem: { text: "1+1=?", type: "arithmetic", difficulty: 1 },
					status: "pending",
				},
			])
			store.set(currentProblemIndexAtom, 5)
			expect(store.get(currentProblemAtom)).toBeNull()
		})
	})

	describe("remainingProblemsCountAtom (derived)", () => {
		it("問題がない場合は0を返す", () => {
			expect(store.get(remainingProblemsCountAtom)).toBe(0)
		})

		it("pending + skippedの数を返す", () => {
			store.set(worksheetProblemsAtom, [
				{
					id: "p1",
					problem: { text: "1+1=?", type: "arithmetic", difficulty: 1 },
					status: "pending",
				},
				{
					id: "p2",
					problem: { text: "2+3=?", type: "arithmetic", difficulty: 1 },
					status: "completed",
				},
				{
					id: "p3",
					problem: { text: "4-2=?", type: "arithmetic", difficulty: 1 },
					status: "skipped",
				},
				{
					id: "p4",
					problem: { text: "5+1=?", type: "arithmetic", difficulty: 1 },
					status: "in_progress",
				},
			])
			// pending(1) + skipped(1) = 2
			expect(store.get(remainingProblemsCountAtom)).toBe(2)
		})
	})

	describe("showProblemSelectorAtom", () => {
		it("初期値はfalse", () => {
			expect(store.get(showProblemSelectorAtom)).toBe(false)
		})

		it("trueにセットできる", () => {
			store.set(showProblemSelectorAtom, true)
			expect(store.get(showProblemSelectorAtom)).toBe(true)
		})
	})
})
