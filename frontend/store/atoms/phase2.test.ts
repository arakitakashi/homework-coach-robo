/**
 * Phase 2 Jotai atoms のテスト
 * 初期値、更新、派生atomの動作確認
 */

import { createStore } from "jotai"
import { describe, expect, it } from "vitest"
import type {
	ActiveAgent,
	AgentTransition,
	ChildLearningProfile,
	EmotionAdaptation,
	EmotionAnalysis,
	RetrievedMemory,
	ToolExecution,
} from "@/types"
import {
	activeAgentAtom,
	activeToolExecutionsAtom,
	agentTransitionHistoryAtom,
	emotionAdaptationAtom,
	emotionAnalysisAtom,
	emotionHistoryAtom,
	isToolRunningAtom,
	learningProfileAtom,
	retrievedMemoriesAtom,
	toolExecutionHistoryAtom,
} from "./phase2"

// ============================================
// 初期値テスト
// ============================================

describe("Phase 2 Atoms - Initial Values", () => {
	it("activeToolExecutionsAtom の初期値は空配列", () => {
		const store = createStore()
		expect(store.get(activeToolExecutionsAtom)).toEqual([])
	})

	it("toolExecutionHistoryAtom の初期値は空配列", () => {
		const store = createStore()
		expect(store.get(toolExecutionHistoryAtom)).toEqual([])
	})

	it("isToolRunningAtom の初期値は false", () => {
		const store = createStore()
		expect(store.get(isToolRunningAtom)).toBe(false)
	})

	it("activeAgentAtom の初期値は null", () => {
		const store = createStore()
		expect(store.get(activeAgentAtom)).toBeNull()
	})

	it("agentTransitionHistoryAtom の初期値は空配列", () => {
		const store = createStore()
		expect(store.get(agentTransitionHistoryAtom)).toEqual([])
	})

	it("retrievedMemoriesAtom の初期値は空配列", () => {
		const store = createStore()
		expect(store.get(retrievedMemoriesAtom)).toEqual([])
	})

	it("emotionAnalysisAtom の初期値は null", () => {
		const store = createStore()
		expect(store.get(emotionAnalysisAtom)).toBeNull()
	})

	it("emotionAdaptationAtom の初期値は null", () => {
		const store = createStore()
		expect(store.get(emotionAdaptationAtom)).toBeNull()
	})

	it("emotionHistoryAtom の初期値は空配列", () => {
		const store = createStore()
		expect(store.get(emotionHistoryAtom)).toEqual([])
	})

	it("learningProfileAtom の初期値は null", () => {
		const store = createStore()
		expect(store.get(learningProfileAtom)).toBeNull()
	})
})

// ============================================
// Phase 2a: ツール atoms テスト
// ============================================

describe("Phase 2a: Tool Atoms", () => {
	it("activeToolExecutionsAtom にツール実行を追加できる", () => {
		const store = createStore()
		const exec: ToolExecution = {
			toolName: "calculate_tool",
			status: "running",
			timestamp: new Date(),
		}
		store.set(activeToolExecutionsAtom, [exec])
		expect(store.get(activeToolExecutionsAtom)).toHaveLength(1)
		expect(store.get(activeToolExecutionsAtom)[0].toolName).toBe("calculate_tool")
	})

	it("toolExecutionHistoryAtom に履歴を追加できる", () => {
		const store = createStore()
		const exec: ToolExecution = {
			toolName: "manage_hint_tool",
			status: "completed",
			output: { hint: "考えてみよう" },
			timestamp: new Date(),
		}
		store.set(toolExecutionHistoryAtom, [exec])
		expect(store.get(toolExecutionHistoryAtom)).toHaveLength(1)
		expect(store.get(toolExecutionHistoryAtom)[0].status).toBe("completed")
	})

	it("isToolRunningAtom は running 状態のツールがあれば true を返す", () => {
		const store = createStore()
		store.set(activeToolExecutionsAtom, [
			{ toolName: "calculate_tool", status: "running", timestamp: new Date() },
		])
		expect(store.get(isToolRunningAtom)).toBe(true)
	})

	it("isToolRunningAtom は pending 状態のツールがあれば true を返す", () => {
		const store = createStore()
		store.set(activeToolExecutionsAtom, [
			{ toolName: "manage_hint_tool", status: "pending", timestamp: new Date() },
		])
		expect(store.get(isToolRunningAtom)).toBe(true)
	})

	it("isToolRunningAtom はすべて completed なら false を返す", () => {
		const store = createStore()
		store.set(activeToolExecutionsAtom, [
			{ toolName: "calculate_tool", status: "completed", timestamp: new Date() },
			{ toolName: "manage_hint_tool", status: "completed", timestamp: new Date() },
		])
		expect(store.get(isToolRunningAtom)).toBe(false)
	})

	it("isToolRunningAtom は error 状態のみなら false を返す", () => {
		const store = createStore()
		store.set(activeToolExecutionsAtom, [
			{ toolName: "analyze_image_tool", status: "error", timestamp: new Date() },
		])
		expect(store.get(isToolRunningAtom)).toBe(false)
	})

	it("isToolRunningAtom は mixed 状態で running があれば true を返す", () => {
		const store = createStore()
		store.set(activeToolExecutionsAtom, [
			{ toolName: "calculate_tool", status: "completed", timestamp: new Date() },
			{ toolName: "manage_hint_tool", status: "running", timestamp: new Date() },
		])
		expect(store.get(isToolRunningAtom)).toBe(true)
	})
})

// ============================================
// Phase 2b: エージェント atoms テスト
// ============================================

describe("Phase 2b: Agent Atoms", () => {
	it("activeAgentAtom にエージェントを設定できる", () => {
		const store = createStore()
		const agent: ActiveAgent = {
			type: "math_coach",
			name: "算数コーチ",
			startedAt: new Date(),
		}
		store.set(activeAgentAtom, agent)
		expect(store.get(activeAgentAtom)).toEqual(agent)
	})

	it("activeAgentAtom を null にリセットできる", () => {
		const store = createStore()
		store.set(activeAgentAtom, {
			type: "math_coach",
			name: "算数コーチ",
			startedAt: new Date(),
		})
		store.set(activeAgentAtom, null)
		expect(store.get(activeAgentAtom)).toBeNull()
	})

	it("agentTransitionHistoryAtom に遷移履歴を追加できる", () => {
		const store = createStore()
		const transition: AgentTransition = {
			fromAgent: "router",
			toAgent: "math_coach",
			reason: "算数の問題を検出",
			timestamp: new Date(),
		}
		store.set(agentTransitionHistoryAtom, [transition])
		expect(store.get(agentTransitionHistoryAtom)).toHaveLength(1)
		expect(store.get(agentTransitionHistoryAtom)[0].toAgent).toBe("math_coach")
	})
})

// ============================================
// Phase 2c: RAG atoms テスト
// ============================================

describe("Phase 2c: RAG Atoms", () => {
	it("retrievedMemoriesAtom に記憶を設定できる", () => {
		const store = createStore()
		const memory: RetrievedMemory = {
			id: "mem-1",
			memoryType: "learning_insight",
			content: "くり上がりでつまずいていた",
			tags: ["算数"],
			relevanceScore: 0.9,
			createdAt: new Date(),
		}
		store.set(retrievedMemoriesAtom, [memory])
		expect(store.get(retrievedMemoriesAtom)).toHaveLength(1)
		expect(store.get(retrievedMemoriesAtom)[0].relevanceScore).toBe(0.9)
	})

	it("retrievedMemoriesAtom を空配列にリセットできる", () => {
		const store = createStore()
		store.set(retrievedMemoriesAtom, [
			{
				id: "mem-1",
				memoryType: "learning_insight" as const,
				content: "test",
				tags: [],
				relevanceScore: 0.5,
				createdAt: new Date(),
			},
		])
		store.set(retrievedMemoriesAtom, [])
		expect(store.get(retrievedMemoriesAtom)).toEqual([])
	})
})

// ============================================
// Phase 2d: 感情 atoms テスト
// ============================================

describe("Phase 2d: Emotion Atoms", () => {
	it("emotionAnalysisAtom に感情分析結果を設定できる", () => {
		const store = createStore()
		const analysis: EmotionAnalysis = {
			primaryEmotion: "frustrated",
			confidence: 0.8,
			frustrationLevel: 7,
			engagementLevel: 4,
			timestamp: new Date(),
		}
		store.set(emotionAnalysisAtom, analysis)
		expect(store.get(emotionAnalysisAtom)?.primaryEmotion).toBe("frustrated")
	})

	it("emotionAdaptationAtom に適応設定を設定できる", () => {
		const store = createStore()
		const adaptation: EmotionAdaptation = {
			currentEmotion: "frustrated",
			supportLevel: "intensive",
			dialogueTone: "empathetic",
			adjustedAt: new Date(),
		}
		store.set(emotionAdaptationAtom, adaptation)
		expect(store.get(emotionAdaptationAtom)?.supportLevel).toBe("intensive")
	})

	it("emotionHistoryAtom に感情履歴を蓄積できる", () => {
		const store = createStore()
		const analysis1: EmotionAnalysis = {
			primaryEmotion: "neutral",
			confidence: 0.7,
			frustrationLevel: 2,
			engagementLevel: 6,
			timestamp: new Date(),
		}
		const analysis2: EmotionAnalysis = {
			primaryEmotion: "happy",
			confidence: 0.9,
			frustrationLevel: 1,
			engagementLevel: 9,
			timestamp: new Date(),
		}
		store.set(emotionHistoryAtom, [analysis1, analysis2])
		expect(store.get(emotionHistoryAtom)).toHaveLength(2)
		expect(store.get(emotionHistoryAtom)[1].primaryEmotion).toBe("happy")
	})
})

// ============================================
// 学習プロファイル atoms テスト
// ============================================

describe("Learning Profile Atom", () => {
	it("learningProfileAtom に学習プロファイルを設定できる", () => {
		const store = createStore()
		const profile: ChildLearningProfile = {
			childId: "child-1",
			thinking: {
				persistenceScore: 8,
				independenceScore: 6,
				reflectionQuality: 7,
				hintDependency: 0.3,
				updatedAt: new Date(),
			},
			subjects: [],
			totalSessions: 5,
			totalProblemsSolved: 12,
			createdAt: new Date(),
			updatedAt: new Date(),
		}
		store.set(learningProfileAtom, profile)
		expect(store.get(learningProfileAtom)?.childId).toBe("child-1")
		expect(store.get(learningProfileAtom)?.totalSessions).toBe(5)
	})

	it("learningProfileAtom を null にリセットできる", () => {
		const store = createStore()
		store.set(learningProfileAtom, {
			childId: "child-1",
			thinking: {
				persistenceScore: 5,
				independenceScore: 5,
				reflectionQuality: 5,
				hintDependency: 0.5,
				updatedAt: new Date(),
			},
			subjects: [],
			totalSessions: 1,
			totalProblemsSolved: 0,
			createdAt: new Date(),
			updatedAt: new Date(),
		})
		store.set(learningProfileAtom, null)
		expect(store.get(learningProfileAtom)).toBeNull()
	})
})
