import type { HintLevel } from "@/types"

interface HintIndicatorProps {
	currentLevel: HintLevel
}

export function HintIndicator({ currentLevel }: HintIndicatorProps) {
	const levels = [1, 2, 3] as const

	return (
		<div className="flex items-center gap-2" role="group" aria-label="ヒントレベル">
			{levels.map((level) => (
				<TreasureBox key={level} level={level} isOpen={currentLevel >= level} />
			))}
		</div>
	)
}

interface TreasureBoxProps {
	level: 1 | 2 | 3
	isOpen: boolean
}

function TreasureBox({ level, isOpen }: TreasureBoxProps) {
	return (
		<div
			data-testid="hint-box"
			data-open={isOpen}
			className={`
        transition-all duration-300
        ${isOpen ? "scale-110" : "scale-100"}
      `}
		>
			<svg
				role="img"
				aria-label={`ヒント${level}: ${isOpen ? "使用済み" : "未使用"}`}
				viewBox="0 0 40 40"
				className="h-10 w-10"
			>
				{isOpen ? (
					// Open treasure box
					<>
						{/* Box base */}
						<rect x="5" y="20" width="30" height="15" rx="2" className="fill-amber-600" />
						{/* Box lid (open) */}
						<rect
							x="5"
							y="10"
							width="30"
							height="10"
							rx="2"
							className="fill-amber-500"
							transform="rotate(-15 20 20)"
						/>
						{/* Sparkle */}
						<circle cx="20" cy="18" r="3" className="fill-yellow-300" />
						<circle cx="15" cy="15" r="2" className="fill-yellow-200" />
						<circle cx="25" cy="15" r="2" className="fill-yellow-200" />
					</>
				) : (
					// Closed treasure box
					<>
						{/* Box base */}
						<rect x="5" y="20" width="30" height="15" rx="2" className="fill-amber-700" />
						{/* Box lid (closed) */}
						<rect x="5" y="12" width="30" height="10" rx="2" className="fill-amber-600" />
						{/* Lock */}
						<circle cx="20" cy="22" r="3" className="fill-gray-400" />
						<rect x="18" y="22" width="4" height="5" className="fill-gray-400" />
					</>
				)}
			</svg>
		</div>
	)
}
