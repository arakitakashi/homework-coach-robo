import type { AgentType } from "@/types/phase2"

const agentLabels: Record<AgentType, string> = {
	router: "ルーター",
	math_coach: "算数",
	japanese_coach: "国語",
	encouragement: "励まし",
	review: "振り返り",
}

interface AgentBadgeProps {
	agent: AgentType
}

export function AgentBadge({ agent }: AgentBadgeProps) {
	return (
		// biome-ignore lint/a11y/useSemanticElements: outputは不適切。計算結果ではなく状態表示のため
		<div
			role="status"
			className="rounded-full bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-700"
			aria-label={`エージェント: ${agentLabels[agent]}`}
		>
			{agentLabels[agent]}
		</div>
	)
}
