interface TopicLabelProps {
	topic: string
}

export function TopicLabel({ topic }: TopicLabelProps) {
	return (
		<div className="flex items-center gap-2">
			<span className="text-xs text-gray-500">トピック:</span>
			<span className="text-sm text-gray-700">{topic}</span>
		</div>
	)
}
