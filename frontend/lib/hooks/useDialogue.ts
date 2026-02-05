/**
 * 対話フック
 *
 * SSEクライアントをラップし、Jotai atomsと連携して対話を管理する。
 */

import { useAtom, useAtomValue, useSetAtom } from "jotai"
import { useCallback, useRef, useState } from "react"
import { DialogueClient } from "@/lib/api"
import { characterStateAtom, dialogueTurnsAtom } from "@/store/atoms/dialogue"
import { sessionAtom } from "@/store/atoms/session"
import type { DialogueTurn } from "@/types"

/** useDialogueのオプション */
export interface UseDialogueOptions {
	/** バックエンドのベースURL */
	baseUrl?: string
}

/** useDialogueの戻り値 */
export interface UseDialogueReturn {
	/** メッセージを送信 */
	sendMessage: (message: string) => Promise<void>
	/** 送信中かどうか */
	isLoading: boolean
	/** エラー */
	error: string | null
	/** エラーをクリア */
	clearError: () => void
}

/** 一意なIDを生成 */
function generateId(): string {
	return `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`
}

/**
 * 対話フック
 *
 * @param options - オプション
 * @returns 対話操作と状態
 */
export function useDialogue(options?: UseDialogueOptions): UseDialogueReturn {
	const baseUrl = options?.baseUrl ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

	const session = useAtomValue(sessionAtom)
	const [_dialogueTurns, setDialogueTurns] = useAtom(dialogueTurnsAtom)
	const setCharacterState = useSetAtom(characterStateAtom)

	const [isLoading, setIsLoading] = useState(false)
	const [error, setError] = useState<string | null>(null)

	// ロボットの回答を蓄積するためのref
	const robotResponseRef = useRef<string>("")
	// クライアントのref
	const clientRef = useRef<DialogueClient | null>(null)

	const sendMessage = useCallback(
		async (message: string): Promise<void> => {
			// セッションがない場合はエラー
			if (!session) {
				setError("セッションがありません")
				return
			}

			setIsLoading(true)
			setError(null)
			setCharacterState("thinking")
			robotResponseRef.current = ""

			// ユーザーメッセージを対話履歴に追加
			const userTurn: DialogueTurn = {
				id: generateId(),
				speaker: "child",
				text: message,
				timestamp: new Date(),
			}
			setDialogueTurns((prev) => [...prev, userTurn])

			// SSEクライアントを作成
			const client = new DialogueClient({
				baseUrl,
				onText: (text) => {
					robotResponseRef.current += text
				},
				onDone: () => {
					// ロボットの回答を対話履歴に追加
					if (robotResponseRef.current) {
						const robotTurn: DialogueTurn = {
							id: generateId(),
							speaker: "robot",
							text: robotResponseRef.current,
							timestamp: new Date(),
						}
						setDialogueTurns((prev) => [...prev, robotTurn])
					}
					setCharacterState("idle")
					setIsLoading(false)
				},
				onError: (errorMessage, _code) => {
					setError(errorMessage)
					setCharacterState("idle")
					setIsLoading(false)
				},
			})

			clientRef.current = client

			try {
				await client.run({
					user_id: session.userId,
					session_id: session.id,
					message,
				})
			} catch {
				// クライアント内でエラーハンドリングされるため、ここでは何もしない
			}
		},
		[session, baseUrl, setDialogueTurns, setCharacterState],
	)

	const clearError = useCallback(() => {
		setError(null)
	}, [])

	return {
		sendMessage,
		isLoading,
		error,
		clearError,
	}
}
