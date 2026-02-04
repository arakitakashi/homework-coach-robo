import type { LearningProgress } from "@/types"

type ProgressDisplayProps = LearningProgress

export function ProgressDisplay({
	selfDiscoveryCount,
	hintDiscoveryCount,
	togetherCount,
}: ProgressDisplayProps) {
	const totalPoints = selfDiscoveryCount * 3 + hintDiscoveryCount * 2 + togetherCount * 1

	return (
		<div className="rounded-xl bg-gradient-to-r from-purple-50 to-pink-50 p-4">
			<div className="mb-3 text-center">
				<span className="text-2xl font-bold text-purple-600">{totalPoints}</span>
				<span className="ml-1 text-gray-600">ポイント</span>
			</div>

			<div className="flex justify-around">
				<ProgressItem
					label="自分で"
					count={selfDiscoveryCount}
					points={3}
					color="text-green-600"
					bgColor="bg-green-100"
				/>
				<ProgressItem
					label="ヒントで"
					count={hintDiscoveryCount}
					points={2}
					color="text-blue-600"
					bgColor="bg-blue-100"
				/>
				<ProgressItem
					label="一緒に"
					count={togetherCount}
					points={1}
					color="text-orange-600"
					bgColor="bg-orange-100"
				/>
			</div>
		</div>
	)
}

interface ProgressItemProps {
	label: string
	count: number
	points: number
	color: string
	bgColor: string
}

function ProgressItem({ label, count, points, color, bgColor }: ProgressItemProps) {
	return (
		<div className="flex flex-col items-center">
			<div className={`flex h-10 w-10 items-center justify-center rounded-full ${bgColor}`}>
				<span className={`text-lg font-bold ${color}`}>{count}</span>
			</div>
			<span className="mt-1 text-xs text-gray-600">{label}</span>
			<span className="text-xs text-gray-400">({points}pt)</span>
		</div>
	)
}
