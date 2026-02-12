import { useEffect, useRef } from "react"
import type { DialogueTurn } from "@/types"
import { DialogueMetadataFooter } from "./DialogueMetadataFooter"
import { DialogueMetadataHeader } from "./DialogueMetadataHeader"

interface DialogueHistoryProps {
	turns: DialogueTurn[]
}

export function DialogueHistory({ turns }: DialogueHistoryProps) {
	const containerRef = useRef<HTMLDivElement>(null)

	// Auto-scroll to bottom when new turns are added
	useEffect(() => {
		if (containerRef.current) {
			containerRef.current.scrollTop = containerRef.current.scrollHeight
		}
	}, [])

	if (turns.length === 0) {
		return (
			<div
				role="log"
				aria-label="対話履歴"
				className="flex h-64 items-center justify-center rounded-xl bg-gray-50 p-4"
			>
				<p className="text-gray-500">対話を始めよう！</p>
			</div>
		)
	}

	return (
		<div
			ref={containerRef}
			role="log"
			aria-label="対話履歴"
			aria-live="polite"
			className="flex h-64 flex-col gap-3 overflow-y-auto rounded-xl bg-gray-50 p-4"
		>
			{turns.map((turn) => (
				<DialogueBubble key={turn.id} turn={turn} />
			))}
		</div>
	)
}

interface DialogueBubbleProps {
	turn: DialogueTurn
}

function DialogueBubble({ turn }: DialogueBubbleProps) {
	const isChild = turn.speaker === "child"
	const hasHeader = turn.questionType || turn.emotion || turn.activeAgent
	const hasFooter = turn.responseAnalysis || (turn.toolExecutions && turn.toolExecutions.length > 0)

	return (
		<div className={`flex ${isChild ? "justify-end" : "justify-start"}`}>
			<div
				className={`
          max-w-[80%] rounded-2xl px-4 py-2
          ${isChild ? "bg-blue-100 text-blue-900" : "bg-gray-100 text-gray-900"}
        `}
			>
				{hasHeader && <DialogueMetadataHeader turn={turn} />}
				<p className="text-sm">{turn.text}</p>
				{hasFooter && <DialogueMetadataFooter turn={turn} />}
			</div>
		</div>
	)
}
