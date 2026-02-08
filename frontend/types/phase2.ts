/**
 * Phase 2 型定義
 * Phase 2a: ツール (Function Calling)
 * Phase 2b: マルチエージェント
 * Phase 2c: RAG (セマンティック検索)
 * Phase 2d: 感情適応
 */

// ============================================
// Phase 2a: ツール (Function Calling)
// ============================================

/** ADKツール名（Phase 2aで導入） */
export type ToolName =
	| "calculate_tool"
	| "manage_hint_tool"
	| "record_progress_tool"
	| "check_curriculum_tool"
	| "analyze_image_tool"

/** ツール実行ステータス */
export type ToolExecutionStatus = "pending" | "running" | "completed" | "error"

/** ツール実行結果 */
export interface ToolExecution {
	toolName: ToolName
	status: ToolExecutionStatus
	input?: Record<string, unknown>
	output?: Record<string, unknown>
	error?: string
	timestamp: Date
}

/** 計算検証結果 (calculate_tool) */
export interface CalculationResult {
	expression: string
	result: number
	isCorrect: boolean
	steps?: string[]
}

/** ヒント管理結果 (manage_hint_tool) */
export interface HintManagementResult {
	currentLevel: number
	hint: string
	shouldAdvanceLevel: boolean
}

/** 進捗記録結果 (record_progress_tool) */
export interface ProgressRecordResult {
	discoveryType: "self" | "hint" | "together"
	pointsEarned: number
	totalPoints: number
}

/** カリキュラム参照結果 (check_curriculum_tool) */
export interface CurriculumCheckResult {
	subject: SubjectType
	grade: number
	topic: string
	relatedConcepts: string[]
	difficulty: number
}

/** 画像分析結果 (analyze_image_tool) */
export interface ImageAnalysisResult {
	recognizedText: string
	problemType?: string
	confidence: number
	extractedExpression?: string
}

// ============================================
// Phase 2b: マルチエージェント
// ============================================

/** 科目タイプ */
export type SubjectType = "math" | "japanese"

/** エージェントタイプ */
export type AgentType = "router" | "math_coach" | "japanese_coach" | "encouragement" | "review"

/** アクティブエージェント情報 */
export interface ActiveAgent {
	type: AgentType
	name: string
	startedAt: Date
}

/** エージェント切り替えイベント */
export interface AgentTransition {
	fromAgent: AgentType
	toAgent: AgentType
	reason: string
	timestamp: Date
}

// ============================================
// Phase 2c: RAG (セマンティック検索)
// ============================================

/** 記憶タイプ */
export type MemoryType = "learning_insight" | "thinking_pattern" | "effective_approach"

/** 検索された記憶 */
export interface RetrievedMemory {
	id: string
	memoryType: MemoryType
	content: string
	tags: string[]
	relevanceScore: number
	createdAt: Date
}

// ============================================
// Phase 2d: 感情適応
// ============================================

/** 感情タイプ */
export type EmotionType = "frustrated" | "confident" | "confused" | "happy" | "tired" | "neutral"

/** 感情分析結果 */
export interface EmotionAnalysis {
	primaryEmotion: EmotionType
	confidence: number
	frustrationLevel: number
	engagementLevel: number
	timestamp: Date
}

/** サポートレベル */
export type SupportLevel = "minimal" | "moderate" | "intensive"

/** 対話トーン (backend DialogueTone mirror) */
export type DialogueTone = "encouraging" | "neutral" | "empathetic"

/** 感情適応設定 */
export interface EmotionAdaptation {
	currentEmotion: EmotionType
	supportLevel: SupportLevel
	dialogueTone: DialogueTone
	adjustedAt: Date
}

// ============================================
// 共通拡張型
// ============================================

/** 質問タイプ (backend QuestionType mirror) */
export type QuestionType = "understanding_check" | "thinking_guide" | "hint"

/** 回答分析結果 (backend ResponseAnalysis mirror) */
export interface ResponseAnalysis {
	understandingLevel: number
	isCorrectDirection: boolean
	needsClarification: boolean
	keyInsights: string[]
}

/** 思考の傾向 */
export interface ThinkingTendencies {
	persistenceScore: number
	independenceScore: number
	reflectionQuality: number
	hintDependency: number
	updatedAt: Date
}

/** 科目別理解度 */
export interface SubjectUnderstanding {
	subject: string
	topic: string
	level: number
	trend: "improving" | "stable" | "declining"
	weakPoints: string[]
	strongPoints: string[]
	assessedAt: Date
}

/** セッションサマリー */
export interface SessionSummary {
	sessionId: string
	date: Date
	durationSeconds: number
	problemsAttempted: number
	problemsSolvedIndependently: number
	hintsUsed: number
	subjectsCovered: string[]
	insights: string[]
}

/** 学習プロファイル */
export interface ChildLearningProfile {
	childId: string
	thinking: ThinkingTendencies
	subjects: SubjectUnderstanding[]
	totalSessions: number
	totalProblemsSolved: number
	createdAt: Date
	updatedAt: Date
}
