import type { SubjectType } from "@/types/phase2"
import { SubjectBadge } from "./SubjectBadge"
import { TopicLabel } from "./TopicLabel"

interface SubjectDisplayProps {
	subject?: SubjectType
	topic?: string
}

export function SubjectDisplay({ subject, topic }: SubjectDisplayProps) {
	// 教科もトピックも未設定の場合は表示しない
	if (!subject && !topic) {
		return null
	}

	return (
		<section
			className="mb-3 flex flex-col gap-2 sm:flex-row sm:items-center"
			aria-label="現在の学習内容"
		>
			{subject && <SubjectBadge subject={subject} />}
			{topic && <TopicLabel topic={topic} />}
		</section>
	)
}
