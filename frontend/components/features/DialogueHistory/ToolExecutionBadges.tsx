import { CheckCircle, Loader2, XCircle } from "lucide-react"
import type { ToolExecution, ToolName } from "@/types"

const toolLabels: Record<ToolName, string> = {
	calculate_tool: "けいさん",
	manage_hint_tool: "ヒント",
	record_progress_tool: "きろく",
	check_curriculum_tool: "きょうかしょ",
	analyze_image_tool: "しゃしん",
}

interface ToolExecutionBadgesProps {
	executions: ToolExecution[]
}

export function ToolExecutionBadges({ executions }: ToolExecutionBadgesProps) {
	if (executions.length === 0) {
		return null
	}

	return (
		<div className="flex flex-wrap gap-1.5">
			{executions.map((execution) => (
				<ToolBadge
					key={`${execution.toolName}-${execution.timestamp.getTime()}`}
					execution={execution}
				/>
			))}
		</div>
	)
}

function ToolBadge({ execution }: { execution: ToolExecution }) {
	const Icon =
		execution.status === "completed"
			? CheckCircle
			: execution.status === "error"
				? XCircle
				: Loader2

	const color =
		execution.status === "completed"
			? "text-green-600"
			: execution.status === "error"
				? "text-red-600"
				: "text-blue-600"

	return (
		<div className="flex items-center gap-1 rounded-full bg-gray-100 px-2 py-0.5 text-xs">
			<Icon className={`h-3 w-3 ${color}`} aria-hidden="true" />
			<span className="text-gray-700">{toolLabels[execution.toolName]}</span>
		</div>
	)
}
