import type { DialogueTurn } from "@/types"
import { AgentBadge } from "./AgentBadge"
import { EmotionIcon } from "./EmotionIcon"
import { QuestionTypeIcon } from "./QuestionTypeIcon"

interface DialogueMetadataHeaderProps {
	turn: DialogueTurn
}

export function DialogueMetadataHeader({ turn }: DialogueMetadataHeaderProps) {
	return (
		<div className="mb-1 flex items-center gap-2">
			{turn.questionType && <QuestionTypeIcon type={turn.questionType} />}
			{turn.emotion && <EmotionIcon emotion={turn.emotion} />}
			{turn.activeAgent && <AgentBadge agent={turn.activeAgent} />}
		</div>
	)
}
