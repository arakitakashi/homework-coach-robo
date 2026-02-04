import type { ReactNode } from "react"

type ButtonVariant = "primary" | "secondary"
type ButtonSize = "medium" | "large"

interface ButtonProps {
	children: ReactNode
	onClick?: () => void
	variant?: ButtonVariant
	size?: ButtonSize
	disabled?: boolean
	type?: "button" | "submit" | "reset"
	className?: string
	"aria-label"?: string
}

const variantStyles: Record<ButtonVariant, string> = {
	primary: "bg-blue-600 text-white hover:bg-blue-700",
	secondary: "bg-gray-200 text-gray-900 hover:bg-gray-300",
}

const sizeStyles: Record<ButtonSize, string> = {
	medium: "px-4 py-2 text-base",
	large: "px-6 py-3 text-lg",
}

export function Button({
	children,
	onClick,
	variant = "primary",
	size = "medium",
	disabled = false,
	type = "button",
	className = "",
	"aria-label": ariaLabel,
}: ButtonProps) {
	const baseStyles =
		"rounded-lg font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
	const disabledStyles = disabled ? "opacity-50 cursor-not-allowed" : ""

	return (
		<button
			type={type}
			onClick={disabled ? undefined : onClick}
			disabled={disabled}
			aria-label={ariaLabel}
			className={`${baseStyles} ${variantStyles[variant]} ${sizeStyles[size]} ${disabledStyles} ${className}`.trim()}
		>
			{children}
		</button>
	)
}
