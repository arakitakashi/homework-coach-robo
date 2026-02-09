interface EmotionLevelBarProps {
	label: string
	level: number
	maxLevel: number
}

export function EmotionLevelBar({ label, level, maxLevel }: EmotionLevelBarProps) {
	// レベルを low/medium/high に分類
	const getLevelCategory = (): string => {
		const ratio = level / maxLevel
		if (ratio <= 0.3) return "低"
		if (ratio <= 0.6) return "中"
		return "高"
	}

	// レベルに応じた色
	const getColorClass = (): string => {
		const ratio = level / maxLevel
		if (ratio <= 0.3) return "bg-blue-500"
		if (ratio <= 0.6) return "bg-yellow-500"
		return "bg-red-500"
	}

	const widthPercentage = (level / maxLevel) * 100

	return (
		<div className="mb-2">
			<div className="mb-1 flex items-center justify-between text-sm">
				<span className="text-gray-700">{label}</span>
				<span className="text-xs text-gray-500">({getLevelCategory()})</span>
			</div>
			<div
				role="progressbar"
				aria-label={label}
				aria-valuenow={level}
				aria-valuemin={0}
				aria-valuemax={maxLevel}
				className="h-2 w-full rounded-full bg-gray-200"
			>
				<div
					data-testid="level-bar-fill"
					className={`h-full rounded-full transition-all duration-300 ${getColorClass()}`}
					style={{ width: `${widthPercentage}%` }}
				/>
			</div>
		</div>
	)
}
