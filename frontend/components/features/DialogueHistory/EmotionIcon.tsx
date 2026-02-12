import { AlertCircle, Frown, HelpCircle, type LucideIcon, Meh, Smile, Sparkles } from "lucide-react"
import type { EmotionType } from "@/types"

const emotionConfig: Record<
	EmotionType,
	{
		icon: LucideIcon
		label: string
		color: string
	}
> = {
	frustrated: {
		icon: Frown,
		label: "困っている",
		color: "text-red-600",
	},
	confident: {
		icon: Sparkles,
		label: "自信満々",
		color: "text-green-600",
	},
	confused: {
		icon: HelpCircle,
		label: "わからない",
		color: "text-blue-600",
	},
	happy: {
		icon: Smile,
		label: "元気いっぱい",
		color: "text-yellow-600",
	},
	tired: {
		icon: AlertCircle,
		label: "疲れている",
		color: "text-gray-600",
	},
	neutral: {
		icon: Meh,
		label: "落ち着いている",
		color: "text-purple-600",
	},
}

interface EmotionIconProps {
	emotion: EmotionType
}

export function EmotionIcon({ emotion }: EmotionIconProps) {
	const config = emotionConfig[emotion]
	const Icon = config.icon

	return (
		<div role="img" className="flex items-center gap-1" aria-label={`感情: ${config.label}`}>
			<Icon className={`h-4 w-4 ${config.color}`} aria-hidden="true" />
		</div>
	)
}
