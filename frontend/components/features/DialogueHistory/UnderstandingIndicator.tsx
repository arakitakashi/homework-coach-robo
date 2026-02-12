import type { ResponseAnalysis } from "@/types"

interface UnderstandingIndicatorProps {
	analysis: ResponseAnalysis
}

export function UnderstandingIndicator({ analysis }: UnderstandingIndicatorProps) {
	const percentage = Math.round(analysis.understandingLevel * 100)
	const color = analysis.isCorrectDirection ? "bg-green-500" : "bg-yellow-500"

	return (
		// biome-ignore lint/a11y/useSemanticElements: outputは不適切。計算結果ではなく状態表示のため
		<div role="status" className="flex items-center gap-2" aria-label={`理解度: ${percentage}%`}>
			<div className="flex h-2 w-20 overflow-hidden rounded-full bg-gray-200">
				<div className={color} style={{ width: `${percentage}%` }} />
			</div>
			<span className="text-xs text-gray-600">{percentage}%</span>
			{analysis.needsClarification && (
				<span role="img" className="text-xs text-blue-600" aria-label="明確化が必要">
					?
				</span>
			)}
		</div>
	)
}
