import { CheckCircle, HelpCircle, Lightbulb, type LucideIcon } from "lucide-react"
import type { QuestionType } from "@/types"

const questionTypeConfig: Record<
	QuestionType,
	{
		icon: LucideIcon
		label: string
		color: string
	}
> = {
	understanding_check: {
		icon: CheckCircle,
		label: "理解確認",
		color: "text-green-600",
	},
	thinking_guide: {
		icon: Lightbulb,
		label: "思考誘導",
		color: "text-yellow-600",
	},
	hint: {
		icon: HelpCircle,
		label: "ヒント",
		color: "text-blue-600",
	},
}

interface QuestionTypeIconProps {
	type: QuestionType
}

export function QuestionTypeIcon({ type }: QuestionTypeIconProps) {
	const config = questionTypeConfig[type]
	const Icon = config.icon

	return (
		<div role="img" className="flex items-center gap-1" aria-label={`質問タイプ: ${config.label}`}>
			<Icon className={`h-4 w-4 ${config.color}`} aria-hidden="true" />
		</div>
	)
}
