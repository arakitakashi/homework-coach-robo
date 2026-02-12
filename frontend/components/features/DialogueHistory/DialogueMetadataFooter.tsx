import type { DialogueTurn } from "@/types"
import { ToolExecutionBadges } from "./ToolExecutionBadges"
import { UnderstandingIndicator } from "./UnderstandingIndicator"

interface DialogueMetadataFooterProps {
	turn: DialogueTurn
}

export function DialogueMetadataFooter({ turn }: DialogueMetadataFooterProps) {
	return (
		<div className="mt-1 flex items-center gap-2">
			{turn.responseAnalysis && <UnderstandingIndicator analysis={turn.responseAnalysis} />}
			{turn.toolExecutions && turn.toolExecutions.length > 0 && (
				<ToolExecutionBadges executions={turn.toolExecutions} />
			)}
		</div>
	)
}
