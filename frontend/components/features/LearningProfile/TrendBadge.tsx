import { Minus, TrendingDown, TrendingUp } from "lucide-react"

/** トレンドの設定マッピング */
const TREND_CONFIG = {
	improving: {
		icon: TrendingUp,
		label: "上がっている",
		colorClass: "text-green-600 bg-green-50",
	},
	stable: {
		icon: Minus,
		label: "安定",
		colorClass: "text-blue-600 bg-blue-50",
	},
	declining: {
		icon: TrendingDown,
		label: "がんばろう",
		colorClass: "text-orange-600 bg-orange-50",
	},
} as const

interface TrendBadgeProps {
	trend: "improving" | "stable" | "declining"
}

/** トレンドバッジ（improving/stable/declining を視覚的に表示） */
export function TrendBadge({ trend }: TrendBadgeProps) {
	const config = TREND_CONFIG[trend]
	const Icon = config.icon

	return (
		// biome-ignore lint/a11y/useSemanticElements: outputは計算結果用で不適切。トレンド状態表示のためrole="status"を使用
		<span
			className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ${config.colorClass}`}
			role="status"
			aria-label={`トレンド: ${config.label}`}
		>
			<Icon className="h-3 w-3" aria-hidden="true" />
			{config.label}
		</span>
	)
}
