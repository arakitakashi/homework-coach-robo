"use client"

import { useAtom } from "jotai"
import { useRouter } from "next/navigation"
import { useCallback, useEffect, useState } from "react"
import {
	CharacterDisplay,
	DialogueHistory,
	HintIndicator,
	ProgressDisplay,
	VoiceInterface,
} from "@/components/features"
import { Button } from "@/components/ui/Button"
import { Card } from "@/components/ui/Card"
import { ErrorMessage } from "@/components/ui/ErrorMessage"
import { LoadingSpinner } from "@/components/ui/LoadingSpinner"
import { TextInput } from "@/components/ui/TextInput"
import { useDialogue, useSession, useVoiceStream } from "@/lib/hooks"
import { characterStateAtom, dialogueTurnsAtom, hintLevelAtom } from "@/store/atoms/dialogue"
import { learningProgressAtom } from "@/store/atoms/session"
import type { CharacterType, DialogueTurn } from "@/types"

interface SessionContentProps {
	characterType: CharacterType
}

const initialDialogue: DialogueTurn = {
	id: "welcome",
	speaker: "robot",
	text: "こんにちは！いっしょにがんばろうね！",
	timestamp: new Date(),
}

export function SessionContent({ characterType }: SessionContentProps) {
	const router = useRouter()
	const [dialogueTurns, setDialogueTurns] = useAtom(dialogueTurnsAtom)
	const [hintLevel] = useAtom(hintLevelAtom)
	const [characterState] = useAtom(characterStateAtom)
	const [learningProgress] = useAtom(learningProgressAtom)

	// 音声入力の有効化状態
	const [isVoiceEnabled] = useState(true)

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

	// 音声ストリーミングフック
	const {
		connectionState: voiceConnectionState,
		isRecording,
		startRecording,
		stopRecording,
	} = useVoiceStream()

	// 初期化時にセッションを作成
	useEffect(() => {
		if (!session && !isCreating && !sessionError) {
			createSession("いっしょにがんばろう！", 1, characterType)
		}
	}, [session, isCreating, sessionError, createSession, characterType])

	// 初期化時にウェルカムメッセージを追加（初回のみ）
	useEffect(() => {
		if (dialogueTurns.length === 0) {
			setDialogueTurns([initialDialogue])
		}
	}, [dialogueTurns.length, setDialogueTurns])

	const handleEndSession = useCallback(async () => {
		await clearSession()
		router.push("/")
	}, [clearSession, router])

	const handleSendMessage = useCallback(
		(text: string) => {
			sendMessage(text)
		},
		[sendMessage],
	)

	const handleToggleRecording = useCallback(async () => {
		if (isRecording) {
			stopRecording()
		} else {
			await startRecording()
		}
	}, [isRecording, startRecording, stopRecording])

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
		<main className="flex min-h-screen flex-col bg-gradient-to-b from-blue-50 to-purple-50">
			{/* ヘッダー */}
			<header className="flex items-center justify-between p-4">
				<HintIndicator currentLevel={hintLevel} />
				<Button variant="secondary" size="medium" onClick={handleEndSession}>
					おわる
				</Button>
			</header>

			{/* メインコンテンツ */}
			<div className="flex flex-1 flex-col items-center p-4">
				{/* キャラクター表示 */}
				<div className="mb-4">
					<CharacterDisplay character={characterType} state={characterState} />
				</div>

				{/* 対話履歴 */}
				<Card padding="medium" className="mb-4 w-full max-w-md flex-1">
					<DialogueHistory turns={dialogueTurns} />
				</Card>

				{/* 対話エラー表示 */}
				{dialogueError && (
					<div className="mb-4 w-full max-w-md">
						<ErrorMessage
							title="そうしんエラー"
							message={dialogueError}
							onRetry={clearDialogueError}
							retryText="とじる"
						/>
					</div>
				)}

				{/* 進捗表示 */}
				<div className="mb-4 w-full max-w-md">
					<ProgressDisplay {...learningProgress} />
				</div>

				{/* テキスト入力（MVP） */}
				<div className="mb-4 w-full max-w-md">
					<TextInput
						onSubmit={handleSendMessage}
						disabled={isSending || !isConnected}
						placeholder="ここにかいてね"
					/>
				</div>

				{/* 音声インターフェース（将来のために残す） */}
				<div className="w-full max-w-md opacity-50">
					<p className="mb-2 text-center text-sm text-gray-500">
						（おんせいにゅうりょくはじゅんびちゅう）
					</p>
					<VoiceInterface
						isRecording={isRecording}
						audioLevel={0}
						isConnected={isVoiceConnected}
						isPlaying={false}
						onToggleRecording={handleToggleRecording}
					/>
				</div>
			</div>
		</main>
	)
}
