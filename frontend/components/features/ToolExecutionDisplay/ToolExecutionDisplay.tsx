import { LoadingSpinner } from "@/components/ui/LoadingSpinner"
import type { ToolExecution, ToolExecutionStatus, ToolName } from "@/types"

interface ToolExecutionDisplayProps {
	executions: ToolExecution[]
	isRunning: boolean
}

const toolNameLabels: Record<ToolName, string> = {
	calculate_tool: "けいさん",
	manage_hint_tool: "ヒント",
	record_progress_tool: "きろく",
	check_curriculum_tool: "きょうかしょ",
	analyze_image_tool: "しゃしん",
}

function StatusIcon({ status }: { status: ToolExecutionStatus }) {
	switch (status) {
		case "pending":
		case "running":
			return <LoadingSpinner size="small" aria-label="じっこうちゅう" />
		case "completed":
			return (
				<span data-testid="tool-status-completed" className="text-green-500">
					<svg role="img" aria-label="かんりょう" viewBox="0 0 20 20" className="h-5 w-5">
						<path
							fill="currentColor"
							fillRule="evenodd"
							d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
							clipRule="evenodd"
						/>
					</svg>
				</span>
			)
		case "error":
			return (
				<span data-testid="tool-status-error" className="text-red-500">
					<svg role="img" aria-label="エラー" viewBox="0 0 20 20" className="h-5 w-5">
						<path
							fill="currentColor"
							fillRule="evenodd"
							d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
							clipRule="evenodd"
						/>
					</svg>
				</span>
			)
	}
}

export function ToolExecutionDisplay({ executions, isRunning }: ToolExecutionDisplayProps) {
	if (executions.length === 0) {
		return null
	}

	return (
		// biome-ignore lint/a11y/useSemanticElements: outputは計算結果用。ツール実行状態にはrole="status"が適切
		<div
			role="status"
			aria-live="polite"
			aria-label={isRunning ? "ツールじっこうちゅう" : "ツールじっこうかんりょう"}
			className="flex items-center gap-2 rounded-lg bg-white/80 px-3 py-2 shadow-sm"
		>
			{executions.map((execution) => (
				<div
					key={`${execution.toolName}-${execution.timestamp.getTime()}`}
					className="flex items-center gap-1.5"
				>
					<StatusIcon status={execution.status} />
					<span className="text-sm font-medium text-gray-700">
						{toolNameLabels[execution.toolName]}
					</span>
				</div>
			))}
		</div>
	)
}
