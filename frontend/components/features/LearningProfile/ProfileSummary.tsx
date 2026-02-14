import { BookOpen, CheckCircle2 } from "lucide-react"

interface ProfileSummaryProps {
	totalSessions: number
	totalProblemsSolved: number
}

/** 学習プロファイルの概要表示（セッション数・問題解決数） */
export function ProfileSummary({ totalSessions, totalProblemsSolved }: ProfileSummaryProps) {
	return (
		// biome-ignore lint/a11y/useSemanticElements: fieldsetはフォーム要素用で不適切。視覚的グループ化のためrole="group"を使用
		<div className="grid grid-cols-2 gap-3" role="group" aria-label="学習サマリー">
			{/* セッション数 */}
			<div className="flex items-center gap-2 rounded-lg bg-purple-50 p-3">
				<BookOpen className="h-5 w-5 text-purple-500" aria-hidden="true" />
				<div>
					<span className="text-lg font-bold text-purple-700">{totalSessions}</span>
					<span className="ml-1 text-xs text-purple-600">回のセッション</span>
				</div>
			</div>

			{/* 解決問題数 */}
			<div className="flex items-center gap-2 rounded-lg bg-emerald-50 p-3">
				<CheckCircle2 className="h-5 w-5 text-emerald-500" aria-hidden="true" />
				<div>
					<span className="text-lg font-bold text-emerald-700">{totalProblemsSolved}</span>
					<span className="ml-1 text-xs text-emerald-600">問クリア</span>
				</div>
			</div>
		</div>
	)
}
