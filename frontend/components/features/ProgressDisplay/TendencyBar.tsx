interface TendencyBarProps {
	label: string
	score: number
	invert?: boolean
}

export function TendencyBar({ label, score, invert = false }: TendencyBarProps) {
	// スコアを0〜100の範囲に正規化
	const normalizedScore = Math.max(0, Math.min(100, score))

	// invert が true の場合は色を反転（低い方が良い指標）
	const fillColor = invert ? "bg-orange-500" : "bg-blue-500"

	return (
		<div className="flex items-center gap-3">
			<span className="w-20 text-xs text-gray-600">{label}</span>
			<div
				className="relative h-4 flex-1 overflow-hidden rounded-full bg-gray-200"
				role="progressbar"
				aria-valuenow={normalizedScore}
				aria-valuemin={0}
				aria-valuemax={100}
				aria-label={`${label}: ${normalizedScore}%`}
			>
				<div
					className={`h-full transition-all duration-300 ${fillColor}`}
					style={{ width: `${normalizedScore}%` }}
					data-testid="progress-fill"
				/>
			</div>
			<span className="w-10 text-right text-xs text-gray-600">{normalizedScore}%</span>
		</div>
	)
}
