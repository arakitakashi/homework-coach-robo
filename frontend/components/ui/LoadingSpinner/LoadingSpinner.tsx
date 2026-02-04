type SpinnerSize = "small" | "medium" | "large"

interface LoadingSpinnerProps {
	size?: SpinnerSize
	"aria-label"?: string
}

const sizeStyles: Record<SpinnerSize, string> = {
	small: "w-5 h-5",
	medium: "w-8 h-8",
	large: "w-12 h-12",
}

export function LoadingSpinner({
	size = "medium",
	"aria-label": ariaLabel = "Loading",
}: LoadingSpinnerProps) {
	return (
		// biome-ignore lint/a11y/useSemanticElements: outputは計算結果用。ローディング状態にはrole="status"が適切
		<div
			role="status"
			aria-label={ariaLabel}
			className={`${sizeStyles[size]} animate-spin rounded-full border-4 border-gray-200 border-t-blue-600`}
		/>
	)
}
