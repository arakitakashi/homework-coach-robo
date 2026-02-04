import type { ReactNode } from "react"

type CardPadding = "medium" | "large"

interface CardProps {
	children: ReactNode
	className?: string
	padding?: CardPadding
}

const paddingStyles: Record<CardPadding, string> = {
	medium: "p-4",
	large: "p-6",
}

export function Card({ children, className = "", padding = "medium" }: CardProps) {
	const baseStyles = "bg-white rounded-xl shadow-md"

	return (
		<div className={`${baseStyles} ${paddingStyles[padding]} ${className}`.trim()}>{children}</div>
	)
}
