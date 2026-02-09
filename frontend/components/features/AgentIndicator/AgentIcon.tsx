import { BookOpen, Calculator, ClipboardList, Heart, Router } from "lucide-react"
import type { AgentType } from "@/types/phase2"

interface AgentIconProps {
	type: AgentType
	className?: string
}

const AGENT_ICONS = {
	router: Router,
	math_coach: Calculator,
	japanese_coach: BookOpen,
	encouragement: Heart,
	review: ClipboardList,
} as const

export function AgentIcon({ type, className = "h-5 w-5" }: AgentIconProps) {
	const Icon = AGENT_ICONS[type]
	return <Icon className={className} aria-hidden="true" />
}
