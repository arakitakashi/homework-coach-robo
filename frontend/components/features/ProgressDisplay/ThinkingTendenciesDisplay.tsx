import type { ThinkingTendencies } from "@/types/phase2"
import { TendencyBar } from "./TendencyBar"

interface ThinkingTendenciesDisplayProps {
	tendencies?: ThinkingTendencies
}

export function ThinkingTendenciesDisplay({ tendencies }: ThinkingTendenciesDisplayProps) {
	// 未設定の場合は表示しない
	if (!tendencies) {
		return null
	}

	return (
		<section className="mt-4 rounded-lg bg-gray-50 p-4" aria-label="思考の傾向">
			<h3 className="mb-3 text-sm font-semibold text-gray-700">思考の傾向</h3>
			<div className="space-y-2">
				<TendencyBar label="粘り強さ" score={tendencies.persistenceScore} />
				<TendencyBar label="自立度" score={tendencies.independenceScore} />
				<TendencyBar label="振り返り" score={tendencies.reflectionQuality} />
				<TendencyBar label="ヒント依存" score={tendencies.hintDependency} invert={true} />
			</div>
		</section>
	)
}
