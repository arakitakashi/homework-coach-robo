"use client"

import { useAtom } from "jotai"
import {
	AlertCircle,
	Brain,
	Frown,
	HelpCircle,
	type LucideIcon,
	Meh,
	Smile,
	Sparkles,
	Zap,
} from "lucide-react"
import { emotionAdaptationAtom, emotionAnalysisAtom } from "@/store/atoms/phase2"
import type { EmotionType, SupportLevel } from "@/types"
import { EmotionLevelBar } from "./EmotionLevelBar"

// 感情タイプごとのアイコン・ラベル・色のマッピング
const emotionConfig: Record<
	EmotionType,
	{
		icon: LucideIcon
		label: string
		color: string
		bgColor: string
	}
> = {
	frustrated: {
		icon: Frown,
		label: "困っている",
		color: "text-red-600",
		bgColor: "bg-red-50",
	},
	confident: {
		icon: Sparkles,
		label: "自信満々",
		color: "text-green-600",
		bgColor: "bg-green-50",
	},
	confused: {
		icon: HelpCircle,
		label: "わからない",
		color: "text-blue-600",
		bgColor: "bg-blue-50",
	},
	happy: {
		icon: Smile,
		label: "元気いっぱい",
		color: "text-yellow-600",
		bgColor: "bg-yellow-50",
	},
	tired: {
		icon: AlertCircle,
		label: "疲れている",
		color: "text-gray-600",
		bgColor: "bg-gray-50",
	},
	neutral: {
		icon: Meh,
		label: "落ち着いている",
		color: "text-purple-600",
		bgColor: "bg-purple-50",
	},
}

// サポートレベルのラベル・アイコン
const supportLevelConfig: Record<SupportLevel, { icon: LucideIcon; label: string }> = {
	minimal: {
		icon: Brain,
		label: "軽く",
	},
	moderate: {
		icon: HelpCircle,
		label: "普通",
	},
	intensive: {
		icon: Zap,
		label: "しっかり",
	},
}

export function EmotionIndicator() {
	const [emotionAnalysis] = useAtom(emotionAnalysisAtom)
	const [emotionAdaptation] = useAtom(emotionAdaptationAtom)

	// 感情分析データがない場合は何も表示しない
	if (!emotionAnalysis) {
		return null
	}

	const config = emotionConfig[emotionAnalysis.primaryEmotion]
	const Icon = config.icon

	return (
		<div
			role="status"
			aria-label="感情状態"
			className={`rounded-xl p-4 shadow-sm ${config.bgColor}`}
		>
			{/* 感情タイプ */}
			<div className="mb-3 flex items-center gap-2">
				<Icon className={`h-6 w-6 ${config.color}`} aria-hidden="true" />
				<span className={`text-lg font-bold ${config.color}`}>{config.label}</span>
			</div>

			{/* レベルバー */}
			<div className="space-y-2">
				<EmotionLevelBar
					label="イライラ度"
					level={emotionAnalysis.frustrationLevel}
					maxLevel={10}
				/>
				<EmotionLevelBar label="集中度" level={emotionAnalysis.engagementLevel} maxLevel={10} />
			</div>

			{/* サポートレベル */}
			{emotionAdaptation && (
				<div className="mt-3 flex items-center gap-2 border-t border-gray-200 pt-3">
					{(() => {
						const supportConfig = supportLevelConfig[emotionAdaptation.supportLevel]
						const SupportIcon = supportConfig.icon
						return (
							<>
								<SupportIcon className="h-4 w-4 text-gray-600" aria-hidden="true" />
								<span className="text-sm text-gray-700">サポート: {supportConfig.label}</span>
							</>
						)
					})()}
				</div>
			)}
		</div>
	)
}
