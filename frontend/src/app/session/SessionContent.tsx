"use client"

import { AnimatePresence } from "framer-motion"
import { useAtom } from "jotai"
import { useRouter } from "next/navigation"
import { useCallback, useEffect, useRef, useState } from "react"
import {
	AgentIndicator,
	BadgeNotification,
	CameraInterface,
	CharacterDisplay,
	DialogueHistory,
	EmotionIndicator,
	HintIndicator,
	PointDisplay,
	ProgressDisplay,
	StoryProgress,
	ToolExecutionDisplay,
	VoiceInterface,
} from "@/components/features"
import { Button } from "@/components/ui/Button"
import { Card } from "@/components/ui/Card"
import { ErrorMessage } from "@/components/ui/ErrorMessage"
import { LoadingSpinner } from "@/components/ui/LoadingSpinner"
import { TextInput } from "@/components/ui/TextInput"
import { useDialogue, usePcmPlayer, useSession, useVoiceStream } from "@/lib/hooks"
import { inputModeAtom } from "@/store/atoms/camera"
import { characterStateAtom, dialogueTurnsAtom, hintLevelAtom } from "@/store/atoms/dialogue"
import {
	activeAgentAtom,
	activeToolExecutionsAtom,
	agentTransitionHistoryAtom,
	emotionAnalysisAtom,
	emotionHistoryAtom,
	isToolRunningAtom,
} from "@/store/atoms/phase2"
import { learningProgressAtom } from "@/store/atoms/session"
import type {
	ActiveAgent,
	AgentTransition,
	AgentType,
	CharacterType,
	DialogueTurn,
	EmotionAnalysis,
	EmotionType,
	HintLevel,
	ImageAnalysisResult,
	ToolExecution,
	ToolExecutionStatus,
	ToolName,
} from "@/types"

interface SessionContentProps {
	characterType: CharacterType
}

/**
 * ウェルカムメッセージを生成
 */
function createInitialDialogue(characterType: CharacterType): DialogueTurn {
	return {
		id: "welcome",
		speaker: characterType,
		text: "こんにちは！いっしょにがんばろうね！",
		timestamp: new Date(),
	}
}

export function SessionContent({ characterType }: SessionContentProps) {
	const router = useRouter()
	const [dialogueTurns, setDialogueTurns] = useAtom(dialogueTurnsAtom)
	const [hintLevel, setHintLevel] = useAtom(hintLevelAtom)
	const [characterState, setCharacterState] = useAtom(characterStateAtom)
	const [learningProgress, setLearningProgress] = useAtom(learningProgressAtom)
	const [activeToolExecutions, setActiveToolExecutions] = useAtom(activeToolExecutionsAtom)
	const [isToolRunning] = useAtom(isToolRunningAtom)
	const [, _setActiveAgent] = useAtom(activeAgentAtom)
	const [, _setAgentTransitionHistory] = useAtom(agentTransitionHistoryAtom)
	const [, _setEmotionAnalysis] = useAtom(emotionAnalysisAtom)
	const [, _setEmotionHistory] = useAtom(emotionHistoryAtom)
	const [inputMode, setInputMode] = useAtom(inputModeAtom)

	// カメラオーバーレイ表示状態
	const [showCamera, setShowCamera] = useState(false)

	// 音声入力の有効化状態
	const [isVoiceEnabled] = useState(true)

	// トランスクリプションID用カウンター
	const transcriptionIdRef = useRef(0)

	// PCM再生フック
	const {
		isPlaying,
		feedAudio,
		stop: stopPlayback,
		initialize: initPlayer,
		cleanup: cleanupPlayer,
	} = usePcmPlayer()

	// セッション管理フック
	const {
		session,
		isCreating,
		error: sessionError,
		createSession,
		clearSession,
		clearError: clearSessionError,
	} = useSession()

	// 対話フック
	const {
		sendMessage,
		isLoading: isSending,
		error: dialogueError,
		clearError: clearDialogueError,
	} = useDialogue()

	// WebSocketコールバック
	const handleAudioData = useCallback(
		(data: ArrayBuffer) => {
			feedAudio(data)
			setCharacterState("speaking")
		},
		[feedAudio, setCharacterState],
	)

	const handleTranscription = useCallback(
		(text: string, isUser: boolean, finished: boolean) => {
			// 完了したトランスクリプションのみ対話履歴に追加
			if (!finished) {
				return
			}

			transcriptionIdRef.current += 1
			const turn: DialogueTurn = {
				id: `voice-${transcriptionIdRef.current}`,
				speaker: isUser ? "child" : "robot",
				text,
				timestamp: new Date(),
			}
			setDialogueTurns((prev) => [...prev, turn])

			if (isUser) {
				setCharacterState("thinking")
			} else {
				setCharacterState("speaking")
			}
		},
		[setDialogueTurns, setCharacterState],
	)

	const handleTurnComplete = useCallback(() => {
		setCharacterState("idle")
	}, [setCharacterState])

	const handleInterrupted = useCallback(() => {
		stopPlayback()
		setCharacterState("listening")
	}, [stopPlayback, setCharacterState])

	// ツール実行イベントハンドラ
	const handleToolExecution = useCallback(
		(toolName: string, status: string, result?: Record<string, unknown>) => {
			const execution: ToolExecution = {
				toolName: toolName as ToolName,
				status: status as ToolExecutionStatus,
				output: result,
				timestamp: new Date(),
			}
			setActiveToolExecutions((prev) => {
				// 同じツール名の既存実行を更新、なければ追加
				const existingIndex = prev.findIndex((e) => e.toolName === toolName)
				if (existingIndex >= 0) {
					const updated = [...prev]
					updated[existingIndex] = execution
					return updated
				}
				return [...prev, execution]
			})

			// ヒントレベル同期: manage_hint_tool完了時にhintLevelAtomを更新
			if (toolName === "manage_hint_tool" && status === "completed" && result) {
				const level = result.current_level
				if (typeof level === "number" && level >= 0 && level <= 3) {
					setHintLevel(level as HintLevel)
				}
			}

			// 進捗ポイント同期: record_progress_tool完了時にlearningProgressAtomを更新
			if (toolName === "record_progress_tool" && status === "completed" && result) {
				const pointsEarned = result.points_earned
				if (typeof pointsEarned === "number") {
					setLearningProgress((prev) => {
						if (pointsEarned === 3)
							return { ...prev, selfDiscoveryCount: prev.selfDiscoveryCount + 1 }
						if (pointsEarned === 2)
							return { ...prev, hintDiscoveryCount: prev.hintDiscoveryCount + 1 }
						return { ...prev, togetherCount: prev.togetherCount + 1 }
					})
				}
			}
		},
		[setActiveToolExecutions, setHintLevel, setLearningProgress],
	)

	// エージェント遷移イベントハンドラ
	const handleAgentTransition = useCallback(
		(fromAgent: string, toAgent: string, reason: string) => {
			const agent: ActiveAgent = {
				type: toAgent as AgentType,
				name: toAgent,
				startedAt: new Date(),
			}
			_setActiveAgent(agent)

			const transition: AgentTransition = {
				fromAgent: fromAgent as AgentType,
				toAgent: toAgent as AgentType,
				reason,
				timestamp: new Date(),
			}
			_setAgentTransitionHistory((prev) => [...prev, transition])
		},
		[_setActiveAgent, _setAgentTransitionHistory],
	)

	// 感情更新イベントハンドラ
	const handleEmotionUpdate = useCallback(
		(emotion: string, frustrationLevel: number, engagementLevel: number) => {
			const analysis: EmotionAnalysis = {
				primaryEmotion: emotion as EmotionType,
				confidence: 1.0,
				frustrationLevel,
				engagementLevel,
				timestamp: new Date(),
			}
			_setEmotionAnalysis(analysis)
			_setEmotionHistory((prev) => [...prev, analysis])
		},
		[_setEmotionAnalysis, _setEmotionHistory],
	)

	// 画像問題確認イベントハンドラ
	const handleImageProblemConfirmed = useCallback(
		(problemId: string, coachResponse: string) => {
			// 画像認識完了メッセージを対話履歴に追加
			transcriptionIdRef.current += 1
			const turn: DialogueTurn = {
				id: `image-confirmed-${problemId}`,
				speaker: "robot",
				text: coachResponse,
				timestamp: new Date(),
			}
			setDialogueTurns((prev) => [...prev, turn])
			setCharacterState("speaking")
			// 音声モードに自動切り替え
			setInputMode("voice")
		},
		[setDialogueTurns, setCharacterState, setInputMode],
	)

	// 画像認識エラーイベントハンドラ
	const handleImageRecognitionError = useCallback(
		(_error: string, code: string) => {
			// エラーメッセージを対話履歴に追加
			transcriptionIdRef.current += 1
			const turn: DialogueTurn = {
				id: `image-error-${Date.now()}`,
				speaker: "robot",
				text: `しゃしんがよめなかったよ。もういちどためしてね！（${code}）`,
				timestamp: new Date(),
			}
			setDialogueTurns((prev) => [...prev, turn])
			setCharacterState("thinking")
		},
		[setDialogueTurns, setCharacterState],
	)

	// 音声ストリーミングフック
	const {
		connectionState: voiceConnectionState,
		isRecording,
		audioLevel,
		startRecording,
		stopRecording,
		connect: voiceConnect,
		disconnect: voiceDisconnect,
		sendImageStart,
	} = useVoiceStream({
		onAudioData: handleAudioData,
		onTranscription: handleTranscription,
		onTurnComplete: handleTurnComplete,
		onInterrupted: handleInterrupted,
		onToolExecution: handleToolExecution,
		onAgentTransition: handleAgentTransition,
		onEmotionUpdate: handleEmotionUpdate,
		onImageProblemConfirmed: handleImageProblemConfirmed,
		onImageRecognitionError: handleImageRecognitionError,
	})

	// 画像問題認識完了ハンドラ
	const handleProblemRecognized = useCallback(
		(recognizedText: string, result: ImageAnalysisResult) => {
			// sendImageStartを呼び出してWebSocket経由でバックエンドに送信
			if (session) {
				sendImageStart(
					recognizedText,
					"", // imageUrl: バックエンドが既に保存している想定
					result.problemType,
					{
						confidence: result.confidence,
						extractedExpression: result.extractedExpression,
					},
				)
			}
			// オーバーレイを閉じる
			setShowCamera(false)
		},
		[session, sendImageStart],
	)

	// 初期化時にセッションを作成
	useEffect(() => {
		if (!session && !isCreating && !sessionError) {
			createSession("いっしょにがんばろう！", 1, characterType)
		}
	}, [session, isCreating, sessionError, createSession, characterType])

	// 初期化時にウェルカムメッセージを追加（初回のみ）
	useEffect(() => {
		if (dialogueTurns.length === 0) {
			setDialogueTurns([createInitialDialogue(characterType)])
		}
	}, [dialogueTurns.length, setDialogueTurns, characterType])

	// セッション作成完了時にWebSocket接続とPCMプレーヤー初期化
	useEffect(() => {
		if (session) {
			initPlayer()
			voiceConnect(session.userId || "anonymous", session.id)
			// 入力モードが未設定の場合は音声モードをデフォルトに設定
			if (inputMode === null) {
				setInputMode("voice")
			}
		}
	}, [session, initPlayer, voiceConnect, inputMode, setInputMode])

	// コンポーネントアンマウント時のクリーンアップ処理
	useEffect(() => {
		return () => {
			// 対話履歴をリセット
			setDialogueTurns([])
			// その他のセッション関連atomsもリセット
			setCharacterState("idle")
			setActiveToolExecutions([])
			_setActiveAgent(null)
			_setAgentTransitionHistory([])
			_setEmotionAnalysis(null)
			_setEmotionHistory([])
		}
	}, [
		setDialogueTurns,
		setCharacterState,
		setActiveToolExecutions,
		_setActiveAgent,
		_setAgentTransitionHistory,
		_setEmotionAnalysis,
		_setEmotionHistory,
	])

	const handleEndSession = useCallback(async () => {
		voiceDisconnect()
		cleanupPlayer()
		await clearSession()
		setInputMode(null) // 入力モードをリセット
		router.push("/")
	}, [voiceDisconnect, cleanupPlayer, clearSession, setInputMode, router])

	const handleSendMessage = useCallback(
		(text: string) => {
			sendMessage(text)
		},
		[sendMessage],
	)

	const handleToggleRecording = useCallback(async () => {
		if (isRecording) {
			stopRecording()
			setCharacterState("thinking")
		} else {
			setCharacterState("listening")
			await startRecording()
		}
	}, [isRecording, startRecording, stopRecording, setCharacterState])

	const handleRetry = useCallback(() => {
		clearSessionError()
		createSession("いっしょにがんばろう！", 1, characterType)
	}, [clearSessionError, createSession, characterType])

	// セッション作成中はローディング表示
	if (isCreating) {
		return (
			<main className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-b from-blue-50 to-purple-50">
				<LoadingSpinner size="large" />
				<p className="mt-4 text-lg text-gray-600">じゅんびちゅう...</p>
			</main>
		)
	}

	// セッション作成エラー
	if (sessionError) {
		return (
			<main className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-b from-blue-50 to-purple-50 p-4">
				<ErrorMessage title="エラー" message={sessionError} />
				<div className="mt-4 flex gap-4">
					<Button variant="primary" size="medium" onClick={handleRetry}>
						もういちど
					</Button>
					<Button variant="secondary" size="medium" onClick={() => router.push("/")}>
						もどる
					</Button>
				</div>
			</main>
		)
	}

	// セッションが存在する場合のメインUI
	const isConnected = !!session
	const isVoiceConnected = isVoiceEnabled && voiceConnectionState === "connected"

	return (
		<>
			{/* バッジ通知（フロート表示） */}
			<BadgeNotification />

			{/* カメラオーバーレイ */}
			{showCamera && (
				<div className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-gradient-to-b from-blue-50 to-purple-50">
					<div className="mb-4 flex w-full max-w-lg justify-end px-4">
						<Button variant="secondary" size="medium" onClick={() => setShowCamera(false)}>
							とじる
						</Button>
					</div>
					<CameraInterface onProblemRecognized={handleProblemRecognized} />
				</div>
			)}

			<main className="flex min-h-screen flex-col bg-gradient-to-b from-blue-50 to-purple-50 md:grid md:grid-cols-[280px_1fr] md:grid-rows-[auto_1fr] lg:grid-cols-[360px_1fr]">
				{/* ヘッダー */}
				<header className="flex items-center justify-between gap-2 p-4 md:col-span-2">
					<HintIndicator currentLevel={hintLevel} />
					<PointDisplay />
					<AgentIndicator />
					<Button variant="secondary" size="medium" onClick={handleEndSession}>
						おわる
					</Button>
				</header>

				{/* メインコンテンツ - モバイル: 縦並び、タブレット以上: 左サイドバー */}
				<div className="flex flex-1 flex-col items-center p-4 md:items-start">
					{/* キャラクター表示 */}
					<div className="mb-4 md:flex md:w-full md:justify-center">
						<CharacterDisplay character={characterType} state={characterState} />
					</div>

					{/* ツール実行表示 */}
					<div className="md:mb-4 md:w-full">
						<ToolExecutionDisplay executions={activeToolExecutions} isRunning={isToolRunning} />
					</div>

					{/* 感情インジケーター - タブレット以上のみ */}
					<AnimatePresence mode="wait">
						<div className="mb-4 hidden w-full max-w-md md:block md:max-w-none">
							<EmotionIndicator />
						</div>
					</AnimatePresence>

					{/* 進捗表示 - タブレット以上のみ */}
					<div className="mb-4 hidden w-full max-w-md md:block md:max-w-none">
						<ProgressDisplay {...learningProgress} />
					</div>

					{/* ストーリー進捗 - タブレット以上のみ */}
					<div className="mb-4 hidden w-full max-w-md md:block md:max-w-none">
						<StoryProgress characterType={characterType} />
					</div>

					{/* モバイルのみの対話履歴 */}
					<Card padding="medium" className="mb-4 w-full max-w-md flex-1 md:hidden">
						<DialogueHistory turns={dialogueTurns} />
					</Card>

					{/* モバイルのみの感情・進捗・ストーリー */}
					<AnimatePresence mode="wait">
						<div className="mb-4 w-full max-w-md md:hidden">
							<EmotionIndicator />
						</div>
					</AnimatePresence>

					<div className="mb-4 w-full max-w-md md:hidden">
						<ProgressDisplay {...learningProgress} />
					</div>

					<div className="mb-4 w-full max-w-md md:hidden">
						<StoryProgress characterType={characterType} />
					</div>

					{/* モバイルのみのテキスト入力 */}
					<div className="mb-4 w-full max-w-md md:hidden">
						<TextInput
							onSubmit={handleSendMessage}
							disabled={isSending || !isConnected}
							placeholder="ここにかいてね"
						/>
					</div>

					{/* モバイルのみの音声インターフェース */}
					{isVoiceEnabled ? (
						<div className="w-full max-w-md md:hidden">
							<VoiceInterface
								isRecording={isRecording}
								audioLevel={audioLevel}
								isConnected={isVoiceConnected}
								isPlaying={isPlaying}
								onToggleRecording={handleToggleRecording}
							/>
						</div>
					) : (
						<div className="w-full max-w-md opacity-50 md:hidden">
							<p className="mb-2 text-center text-sm text-gray-500">
								（おんせいにゅうりょくはじゅんびちゅう）
							</p>
							<VoiceInterface
								isRecording={isRecording}
								audioLevel={audioLevel}
								isConnected={isVoiceConnected}
								isPlaying={isPlaying}
								onToggleRecording={handleToggleRecording}
							/>
						</div>
					)}
				</div>

				{/* 右メインエリア（タブレット以上のみ） */}
				<section className="hidden flex-col gap-4 p-4 md:flex">
					{/* 対話履歴 */}
					<Card padding="medium" className="flex-1 overflow-auto">
						<DialogueHistory turns={dialogueTurns} />
					</Card>

					{/* 対話エラー表示 */}
					{dialogueError && (
						<div>
							<ErrorMessage
								title="そうしんエラー"
								message={dialogueError}
								onRetry={clearDialogueError}
								retryText="とじる"
							/>
						</div>
					)}

					{/* テキスト入力 */}
					<div>
						<TextInput
							onSubmit={handleSendMessage}
							disabled={isSending || !isConnected}
							placeholder="ここにかいてね"
						/>
					</div>

					{/* 音声インターフェース */}
					{isVoiceEnabled ? (
						<div>
							<VoiceInterface
								isRecording={isRecording}
								audioLevel={audioLevel}
								isConnected={isVoiceConnected}
								isPlaying={isPlaying}
								onToggleRecording={handleToggleRecording}
							/>
						</div>
					) : (
						<div className="opacity-50">
							<p className="mb-2 text-center text-sm text-gray-500">
								（おんせいにゅうりょくはじゅんびちゅう）
							</p>
							<VoiceInterface
								isRecording={isRecording}
								audioLevel={audioLevel}
								isConnected={isVoiceConnected}
								isPlaying={isPlaying}
								onToggleRecording={handleToggleRecording}
							/>
						</div>
					)}
				</section>
			</main>

			{/* フローティングカメラボタン */}
			<button
				type="button"
				aria-label="しゃしんをとる"
				className="fixed bottom-6 right-6 z-40 flex h-14 w-14 items-center justify-center rounded-full bg-green-500 text-2xl text-white shadow-lg transition-colors hover:bg-green-600 active:bg-green-700"
				onClick={() => setShowCamera(true)}
			>
				📷
			</button>
		</>
	)
}
