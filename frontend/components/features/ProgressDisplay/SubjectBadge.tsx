import type { SubjectType } from "@/types/phase2"

interface SubjectBadgeProps {
	subject: SubjectType
}

const SUBJECT_CONFIG = {
	math: {
		icon: "🧮",
		label: "算数",
		bgColor: "bg-blue-100",
		textColor: "text-blue-600",
		borderColor: "border-blue-300",
	},
	japanese: {
		icon: "📖",
		label: "国語",
		bgColor: "bg-green-100",
		textColor: "text-green-600",
		borderColor: "border-green-300",
	},
} as const

export function SubjectBadge({ subject }: SubjectBadgeProps) {
	const config = SUBJECT_CONFIG[subject]

	return (
		<div
			className={`flex items-center gap-2 rounded-lg ${config.bgColor} ${config.textColor} px-3 py-1.5`}
			role="img"
			aria-label={`現在の科目: ${config.label}`}
		>
			<span className="text-lg" aria-hidden="true">
				{config.icon}
			</span>
			<span className="text-sm font-semibold">{config.label}</span>
		</div>
	)
}
