/**
 * Phase 2 型定義のテスト
 * 型の値検証、後方互換性、discriminated union の動作確認
 */

import { describe, expect, it } from "vitest"
import type { DialogueTurn } from "./dialogue"
import type {
	ActiveAgent,
	AgentTransition,
	AgentType,
	CalculationResult,
	ChildLearningProfile,
	CurriculumCheckResult,
	DialogueTone,
	EmotionAdaptation,
	EmotionAnalysis,
	EmotionType,
	HintManagementResult,
	ImageAnalysisResult,
	MemoryType,
	ProgressRecordResult,
	QuestionType,
	ResponseAnalysis,
	RetrievedMemory,
	SessionSummary,
	SubjectType,
	SubjectUnderstanding,
	SupportLevel,
	ThinkingTendencies,
	ToolExecution,
	ToolExecutionStatus,
	ToolName,
} from "./phase2"
import type { LearningProgress } from "./session"
import type {
	AgentTransitionMessage,
	EmotionUpdateMessage,
	ToolExecutionMessage,
	WebSocketIncomingMessage,
} from "./websocket"

// ============================================
// Phase 2a: ツール型テスト
// ============================================

describe("Phase 2a: Tool Types", () => {
	it("ToolExecution を正しく生成できる", () => {
		const exec: ToolExecution = {
			toolName: "calculate_tool",
			status: "completed",
			timestamp: new Date(),
		}
		expect(exec.toolName).toBe("calculate_tool")
		expect(exec.status).toBe("completed")
		expect(exec.timestamp).toBeInstanceOf(Date)
	})

	it("ToolExecution のオプショナルフィールドが省略可能", () => {
		const exec: ToolExecution = {
			toolName: "manage_hint_tool",
			status: "pending",
			timestamp: new Date(),
		}
		expect(exec.input).toBeUndefined()
		expect(exec.output).toBeUndefined()
		expect(exec.error).toBeUndefined()
	})

	it("ToolExecution のオプショナルフィールドに値を設定できる", () => {
		const exec: ToolExecution = {
			toolName: "calculate_tool",
			status: "completed",
			input: { expression: "3+5" },
			output: { result: 8 },
			timestamp: new Date(),
		}
		expect(exec.input).toEqual({ expression: "3+5" })
		expect(exec.output).toEqual({ result: 8 })
	})

	it("ToolExecution のエラー状態を表現できる", () => {
		const exec: ToolExecution = {
			toolName: "analyze_image_tool",
			status: "error",
			error: "画像を認識できませんでした",
			timestamp: new Date(),
		}
		expect(exec.status).toBe("error")
		expect(exec.error).toBe("画像を認識できませんでした")
	})

	it("すべてのToolNameが利用可能", () => {
		const names: ToolName[] = [
			"calculate_tool",
			"manage_hint_tool",
			"record_progress_tool",
			"check_curriculum_tool",
			"analyze_image_tool",
		]
		expect(names).toHaveLength(5)
	})

	it("すべてのToolExecutionStatusが利用可能", () => {
		const statuses: ToolExecutionStatus[] = ["pending", "running", "completed", "error"]
		expect(statuses).toHaveLength(4)
	})

	it("CalculationResult を正しく生成できる", () => {
		const result: CalculationResult = {
			expression: "3 + 5",
			result: 8,
			isCorrect: true,
			steps: ["3 + 5 = 8"],
		}
		expect(result.isCorrect).toBe(true)
		expect(result.steps).toHaveLength(1)
	})

	it("HintManagementResult を正しく生成できる", () => {
		const result: HintManagementResult = {
			currentLevel: 2,
			hint: "もう一度問題を読んでみよう",
			shouldAdvanceLevel: false,
		}
		expect(result.currentLevel).toBe(2)
	})

	it("ProgressRecordResult を正しく生成できる", () => {
		const result: ProgressRecordResult = {
			discoveryType: "self",
			pointsEarned: 3,
			totalPoints: 15,
		}
		expect(result.pointsEarned).toBe(3)
	})

	it("CurriculumCheckResult を正しく生成できる", () => {
		const result: CurriculumCheckResult = {
			subject: "math",
			grade: 2,
			topic: "たし算",
			relatedConcepts: ["くり上がり", "10のかたまり"],
			difficulty: 3,
		}
		expect(result.subject).toBe("math")
		expect(result.relatedConcepts).toHaveLength(2)
	})

	it("ImageAnalysisResult を正しく生成できる", () => {
		const result: ImageAnalysisResult = {
			recognizedText: "3 + 5 = ?",
			problemType: "addition",
			confidence: 0.95,
			extractedExpression: "3+5",
		}
		expect(result.confidence).toBe(0.95)
	})
})

// ============================================
// Phase 2b: マルチエージェント型テスト
// ============================================

describe("Phase 2b: Agent Types", () => {
	it("すべてのAgentTypeが利用可能", () => {
		const types: AgentType[] = ["router", "math_coach", "japanese_coach", "encouragement", "review"]
		expect(types).toHaveLength(5)
	})

	it("すべてのSubjectTypeが利用可能", () => {
		const types: SubjectType[] = ["math", "japanese"]
		expect(types).toHaveLength(2)
	})

	it("ActiveAgent を正しく生成できる", () => {
		const agent: ActiveAgent = {
			type: "math_coach",
			name: "算数コーチ",
			startedAt: new Date(),
		}
		expect(agent.type).toBe("math_coach")
		expect(agent.name).toBe("算数コーチ")
	})

	it("AgentTransition を正しく生成できる", () => {
		const transition: AgentTransition = {
			fromAgent: "router",
			toAgent: "math_coach",
			reason: "算数の問題を検出",
			timestamp: new Date(),
		}
		expect(transition.fromAgent).toBe("router")
		expect(transition.toAgent).toBe("math_coach")
	})
})

// ============================================
// Phase 2c: RAG型テスト
// ============================================

describe("Phase 2c: RAG Types", () => {
	it("すべてのMemoryTypeが利用可能", () => {
		const types: MemoryType[] = ["learning_insight", "thinking_pattern", "effective_approach"]
		expect(types).toHaveLength(3)
	})

	it("RetrievedMemory を正しく生成できる", () => {
		const memory: RetrievedMemory = {
			id: "mem-1",
			memoryType: "learning_insight",
			content: "くり上がりの計算でつまずいていた",
			tags: ["算数", "くり上がり"],
			relevanceScore: 0.85,
			createdAt: new Date(),
		}
		expect(memory.relevanceScore).toBe(0.85)
		expect(memory.tags).toHaveLength(2)
	})
})

// ============================================
// Phase 2d: 感情適応型テスト
// ============================================

describe("Phase 2d: Emotion Types", () => {
	it("すべてのEmotionTypeが利用可能", () => {
		const types: EmotionType[] = [
			"frustrated",
			"confident",
			"confused",
			"happy",
			"tired",
			"neutral",
		]
		expect(types).toHaveLength(6)
	})

	it("すべてのSupportLevelが利用可能", () => {
		const levels: SupportLevel[] = ["minimal", "moderate", "intensive"]
		expect(levels).toHaveLength(3)
	})

	it("すべてのDialogueToneが利用可能", () => {
		const tones: DialogueTone[] = ["encouraging", "neutral", "empathetic"]
		expect(tones).toHaveLength(3)
	})

	it("EmotionAnalysis を正しく生成できる", () => {
		const analysis: EmotionAnalysis = {
			primaryEmotion: "frustrated",
			confidence: 0.8,
			frustrationLevel: 7,
			engagementLevel: 4,
			timestamp: new Date(),
		}
		expect(analysis.primaryEmotion).toBe("frustrated")
		expect(analysis.frustrationLevel).toBe(7)
	})

	it("EmotionAdaptation を正しく生成できる", () => {
		const adaptation: EmotionAdaptation = {
			currentEmotion: "frustrated",
			supportLevel: "intensive",
			dialogueTone: "empathetic",
			adjustedAt: new Date(),
		}
		expect(adaptation.supportLevel).toBe("intensive")
		expect(adaptation.dialogueTone).toBe("empathetic")
	})
})

// ============================================
// 共通拡張型テスト
// ============================================

describe("Shared Extended Types", () => {
	it("すべてのQuestionTypeが利用可能", () => {
		const types: QuestionType[] = ["understanding_check", "thinking_guide", "hint"]
		expect(types).toHaveLength(3)
	})

	it("ResponseAnalysis を正しく生成できる", () => {
		const analysis: ResponseAnalysis = {
			understandingLevel: 7,
			isCorrectDirection: true,
			needsClarification: false,
			keyInsights: ["足し算の概念を理解している"],
		}
		expect(analysis.isCorrectDirection).toBe(true)
	})

	it("ThinkingTendencies を正しく生成できる", () => {
		const tendencies: ThinkingTendencies = {
			persistenceScore: 8,
			independenceScore: 6,
			reflectionQuality: 7,
			hintDependency: 0.3,
			updatedAt: new Date(),
		}
		expect(tendencies.hintDependency).toBe(0.3)
	})

	it("SubjectUnderstanding を正しく生成できる", () => {
		const understanding: SubjectUnderstanding = {
			subject: "算数",
			topic: "たし算",
			level: 7,
			trend: "improving",
			weakPoints: ["くり上がり"],
			strongPoints: ["暗算"],
			assessedAt: new Date(),
		}
		expect(understanding.trend).toBe("improving")
	})

	it("SessionSummary を正しく生成できる", () => {
		const summary: SessionSummary = {
			sessionId: "session-1",
			date: new Date(),
			durationSeconds: 600,
			problemsAttempted: 3,
			problemsSolvedIndependently: 2,
			hintsUsed: 1,
			subjectsCovered: ["算数"],
			insights: ["くり上がりを自力で解けた"],
		}
		expect(summary.problemsSolvedIndependently).toBe(2)
	})

	it("ChildLearningProfile を正しく生成できる", () => {
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
		expect(profile.totalSessions).toBe(5)
	})
})

// ============================================
// 後方互換性テスト
// ============================================

describe("Backward Compatibility", () => {
	it("既存のDialogueTurn（Phase 2フィールドなし）が有効", () => {
		const turn: DialogueTurn = {
			id: "1",
			speaker: "child",
			text: "3たす5は？",
			timestamp: new Date(),
		}
		expect(turn.id).toBe("1")
		expect(turn.questionType).toBeUndefined()
		expect(turn.responseAnalysis).toBeUndefined()
		expect(turn.emotion).toBeUndefined()
		expect(turn.activeAgent).toBeUndefined()
		expect(turn.toolExecutions).toBeUndefined()
	})

	it("DialogueTurnにPhase 2フィールドを設定できる", () => {
		const turn: DialogueTurn = {
			id: "2",
			speaker: "robot",
			text: "この問題、何を聞いてると思う？",
			timestamp: new Date(),
			questionType: "understanding_check",
			activeAgent: "math_coach",
			emotion: "neutral",
		}
		expect(turn.questionType).toBe("understanding_check")
		expect(turn.activeAgent).toBe("math_coach")
	})

	it("既存のLearningProgress（Phase 2フィールドなし）が有効", () => {
		const progress: LearningProgress = {
			selfDiscoveryCount: 1,
			hintDiscoveryCount: 2,
			togetherCount: 3,
		}
		expect(progress.selfDiscoveryCount).toBe(1)
		expect(progress.currentSubject).toBeUndefined()
		expect(progress.currentTopic).toBeUndefined()
		expect(progress.thinkingTendencies).toBeUndefined()
	})

	it("LearningProgressにPhase 2フィールドを設定できる", () => {
		const progress: LearningProgress = {
			selfDiscoveryCount: 1,
			hintDiscoveryCount: 2,
			togetherCount: 3,
			currentSubject: "math",
			currentTopic: "たし算",
		}
		expect(progress.currentSubject).toBe("math")
	})
})

// ============================================
// WebSocket メッセージ型テスト
// ============================================

describe("WebSocket Message Types (Phase 2)", () => {
	it("ToolExecutionMessage を正しく生成できる", () => {
		const msg: ToolExecutionMessage = {
			type: "tool_execution",
			toolName: "calculate_tool",
			status: "completed",
		}
		expect(msg.type).toBe("tool_execution")
	})

	it("ToolExecutionMessage にオプショナルresultを設定できる", () => {
		const msg: ToolExecutionMessage = {
			type: "tool_execution",
			toolName: "calculate_tool",
			status: "completed",
			result: { answer: 8 },
		}
		expect(msg.result).toEqual({ answer: 8 })
	})

	it("AgentTransitionMessage を正しく生成できる", () => {
		const msg: AgentTransitionMessage = {
			type: "agent_transition",
			fromAgent: "router",
			toAgent: "math_coach",
			reason: "算数の問題を検出",
		}
		expect(msg.type).toBe("agent_transition")
		expect(msg.toAgent).toBe("math_coach")
	})

	it("EmotionUpdateMessage を正しく生成できる", () => {
		const msg: EmotionUpdateMessage = {
			type: "emotion_update",
			emotion: "frustrated",
			frustrationLevel: 7,
			engagementLevel: 4,
		}
		expect(msg.type).toBe("emotion_update")
		expect(msg.frustrationLevel).toBe(7)
	})

	it("WebSocketIncomingMessage union に新しいメッセージ型が含まれる", () => {
		const messages: WebSocketIncomingMessage[] = [
			{ type: "tool_execution", toolName: "calculate_tool", status: "completed" },
			{ type: "agent_transition", fromAgent: "router", toAgent: "math_coach", reason: "test" },
			{ type: "emotion_update", emotion: "happy", frustrationLevel: 1, engagementLevel: 9 },
			{ type: "session_start", sessionId: "s-1" },
		]
		expect(messages).toHaveLength(4)
		expect(messages[0].type).toBe("tool_execution")
		expect(messages[1].type).toBe("agent_transition")
		expect(messages[2].type).toBe("emotion_update")
	})
})
