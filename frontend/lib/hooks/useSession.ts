/**
 * セッション管理フック
 *
 * セッションの作成・削除を管理し、Jotai atomsと連携する。
 */

import { useAtom } from "jotai"
import { useCallback, useState } from "react"
import { SessionClient } from "@/lib/api"
import { sessionAtom } from "@/store/atoms/session"
import type { CharacterType, Session } from "@/types"

/** useSessionのオプション */
export interface UseSessionOptions {
	/** バックエンドのベースURL */
	baseUrl?: string
}

/** useSessionの戻り値 */
export interface UseSessionReturn {
	/** 現在のセッション */
	session: Session | null
	/** セッション作成中かどうか */
	isCreating: boolean
	/** エラー */
	error: string | null
	/** セッションを作成 */
	createSession: (problem: string, childGrade: number, characterType?: string) => Promise<void>
	/** セッションをクリア */
	clearSession: () => Promise<void>
	/** エラーをクリア */
	clearError: () => void
}

/**
 * セッション管理フック
 *
 * @param options - オプション
 * @returns セッション操作と状態
 *
 * @example
 * ```typescript
 * const { session, createSession, clearSession } = useSession()
 *
 * // セッション作成
 * await createSession("1+1=?", 1, "robot")
 *
 * // セッション終了
 * await clearSession()
 * ```
 */
export function useSession(options?: UseSessionOptions): UseSessionReturn {
	const baseUrl = options?.baseUrl ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

	const [session, setSession] = useAtom(sessionAtom)
	const [isCreating, setIsCreating] = useState(false)
	const [error, setError] = useState<string | null>(null)

	const createSession = useCallback(
		async (problem: string, childGrade: number, characterType?: string): Promise<void> => {
			setIsCreating(true)
			setError(null)

			try {
				const client = new SessionClient({ baseUrl })
				const response = await client.createSession({
					problem,
					child_grade: childGrade,
					character_type: characterType,
				})

				// Session型に変換してatomに保存
				const newSession: Session = {
					id: response.session_id,
					userId: "anonymous", // TODO: 認証実装時に正式なユーザーIDを使用
					character: (characterType as CharacterType) || "robot",
					status: "active",
					startTime: new Date(response.created_at),
				}

				setSession(newSession)
			} catch (err) {
				const message = err instanceof Error ? err.message : "セッション作成に失敗しました"
				setError(message)
			} finally {
				setIsCreating(false)
			}
		},
		[baseUrl, setSession],
	)

	const clearSession = useCallback(async (): Promise<void> => {
		if (!session) {
			return
		}

		const client = new SessionClient({ baseUrl })

		try {
			await client.deleteSession(session.id)
		} catch {
			// 削除エラーは無視してローカル状態をクリア
		}

		setSession(null)
	}, [session, baseUrl, setSession])

	const clearError = useCallback(() => {
		setError(null)
	}, [])

	return {
		session,
		isCreating,
		error,
		createSession,
		clearSession,
		clearError,
	}
}
