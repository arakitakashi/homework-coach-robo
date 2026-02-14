import type { SubjectUnderstanding } from "@/types/phase2"
import { TrendBadge } from "./TrendBadge"

interface SubjectCardProps {
	understanding: SubjectUnderstanding
}

/** 教科別理解度カード（1教科分の習熟度・トレンド・得意/苦手を表示） */
export function SubjectCard({ understanding }: SubjectCardProps) {
	const { subject, topic, level, trend, strongPoints, weakPoints } = understanding
	/** レベルを0-10に正規化 */
	const normalizedLevel = Math.max(0, Math.min(10, level))
	/** プログレスバーの幅（パーセント） */
	const widthPercent = normalizedLevel * 10

	return (
		<article
			className="rounded-lg border border-gray-200 bg-white p-4"
			aria-label={`${subject} - ${topic}`}
		>
			{/* ヘッダー: 教科名 + トレンド */}
			<div className="mb-2 flex items-center justify-between">
				<div>
					<h4 className="text-sm font-bold text-gray-800">{subject}</h4>
					<p className="text-xs text-gray-500">{topic}</p>
				</div>
				<TrendBadge trend={trend} />
			</div>

			{/* 習熟度レベルバー */}
			<div className="mb-3">
				<div className="mb-1 flex items-baseline gap-1">
					<span className="text-lg font-bold text-indigo-600">{normalizedLevel}</span>
					<span className="text-xs text-gray-400">/ 10</span>
				</div>
				<div
					className="h-2 w-full overflow-hidden rounded-full bg-gray-200"
					role="progressbar"
					aria-valuenow={normalizedLevel}
					aria-valuemin={0}
					aria-valuemax={10}
					aria-label={`${subject}の習熟度: ${normalizedLevel}/10`}
				>
					<div
						className="h-full rounded-full bg-indigo-500 transition-all"
						style={{ width: `${widthPercent}%` }}
					/>
				</div>
			</div>

			{/* 得意な点 */}
			{strongPoints.length > 0 && (
				<div className="mb-2">
					<p className="mb-1 text-xs font-medium text-gray-600">とくいなところ</p>
					<div className="flex flex-wrap gap-1">
						{strongPoints.map((point) => (
							<span
								key={point}
								className="rounded-full bg-green-50 px-2 py-0.5 text-xs text-green-700"
							>
								{point}
							</span>
						))}
					</div>
				</div>
			)}

			{/* 苦手な点（ネガティブ表現を避ける） */}
			{weakPoints.length > 0 && (
				<div>
					<p className="mb-1 text-xs font-medium text-gray-600">がんばるところ</p>
					<div className="flex flex-wrap gap-1">
						{weakPoints.map((point) => (
							<span
								key={point}
								className="rounded-full bg-orange-50 px-2 py-0.5 text-xs text-orange-700"
							>
								{point}
							</span>
						))}
					</div>
				</div>
			)}
		</article>
	)
}
