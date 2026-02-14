"use client"

import { useAtomValue } from "jotai"
import { ThinkingTendenciesDisplay } from "@/components/features/ProgressDisplay"
import { learningProfileAtom } from "@/store/atoms/phase2"
import { ProfileSummary } from "./ProfileSummary"
import { SubjectCard } from "./SubjectCard"

/** 学習プロファイル表示コンポーネント（Jotai atom連携） */
export function LearningProfile() {
	const profile = useAtomValue(learningProfileAtom)

	// プロファイルが未設定の場合は表示しない
	if (!profile) {
		return null
	}

	return (
		<section className="space-y-4" aria-label="学習プロファイル">
			{/* 概要: セッション数・問題解決数 */}
			<ProfileSummary
				totalSessions={profile.totalSessions}
				totalProblemsSolved={profile.totalProblemsSolved}
			/>

			{/* 思考の傾向（既存コンポーネント再利用） */}
			<ThinkingTendenciesDisplay tendencies={profile.thinking} />

			{/* 教科別理解度 */}
			<section aria-label="教科別の理解度">
				<h3 className="mb-3 text-sm font-semibold text-gray-700">教科べつの理解度</h3>
				{profile.subjects.length > 0 ? (
					<div className="space-y-3">
						{profile.subjects.map((subject) => (
							<SubjectCard key={`${subject.subject}-${subject.topic}`} understanding={subject} />
						))}
					</div>
				) : (
					<p className="text-sm text-gray-400">まだデータがありません</p>
				)}
			</section>
		</section>
	)
}
