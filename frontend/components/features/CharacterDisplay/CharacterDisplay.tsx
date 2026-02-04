import type { CharacterState, CharacterType } from "@/types"

interface CharacterDisplayProps {
	character: CharacterType
	state: CharacterState
}

const stateAnimations: Record<CharacterState, string> = {
	idle: "animate-none",
	listening: "animate-pulse",
	thinking: "animate-spin-slow",
	speaking: "animate-bounce",
	happy: "animate-wiggle",
}

export function CharacterDisplay({ character, state }: CharacterDisplayProps) {
	const animationClass = stateAnimations[state]

	return (
		<div
			data-testid="character-container"
			className={`flex items-center justify-center ${animationClass}`}
		>
			{character === "robot" && <RobotCharacter state={state} />}
		</div>
	)
}

interface RobotCharacterProps {
	state: CharacterState
}

function RobotCharacter({ state }: RobotCharacterProps) {
	const getEyeStyle = () => {
		switch (state) {
			case "happy":
				return "fill-yellow-400"
			case "thinking":
				return "fill-blue-300"
			default:
				return "fill-blue-500"
		}
	}

	return (
		<svg role="img" aria-label="ロボットキャラクター" viewBox="0 0 120 120" className="h-32 w-32">
			{/* Body */}
			<rect x="30" y="50" width="60" height="50" rx="10" className="fill-gray-400" />

			{/* Head */}
			<rect x="35" y="20" width="50" height="35" rx="8" className="fill-gray-300" />

			{/* Eyes */}
			<circle cx="50" cy="35" r="6" className={getEyeStyle()} />
			<circle cx="70" cy="35" r="6" className={getEyeStyle()} />

			{/* Mouth */}
			<rect
				x="45"
				y="45"
				width="30"
				height="4"
				rx="2"
				className={state === "happy" ? "fill-green-400" : "fill-gray-500"}
			/>

			{/* Antenna */}
			<line x1="60" y1="20" x2="60" y2="10" className="stroke-gray-400 stroke-2" />
			<circle cx="60" cy="8" r="4" className="fill-red-400" />

			{/* Arms */}
			<rect x="15" y="55" width="15" height="8" rx="4" className="fill-gray-400" />
			<rect x="90" y="55" width="15" height="8" rx="4" className="fill-gray-400" />

			{/* Legs */}
			<rect x="40" y="100" width="12" height="15" rx="4" className="fill-gray-500" />
			<rect x="68" y="100" width="12" height="15" rx="4" className="fill-gray-500" />
		</svg>
	)
}
