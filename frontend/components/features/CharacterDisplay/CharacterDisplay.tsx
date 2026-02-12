"use client"

import { useAtom } from "jotai"
import { emotionAnalysisAtom } from "@/store/atoms/phase2"
import type { CharacterState, CharacterType, EmotionType } from "@/types"

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
	const [emotionAnalysis] = useAtom(emotionAnalysisAtom)
	const animationClass = stateAnimations[state]

	return (
		<div
			data-testid="character-container"
			className={`flex items-center justify-center ${animationClass}`}
		>
			{character === "robot" && (
				<RobotCharacter state={state} emotion={emotionAnalysis?.primaryEmotion} />
			)}
			{character === "wizard" && (
				<WizardCharacter state={state} emotion={emotionAnalysis?.primaryEmotion} />
			)}
			{character === "astronaut" && (
				<AstronautCharacter state={state} emotion={emotionAnalysis?.primaryEmotion} />
			)}
			{character === "animal" && (
				<AnimalCharacter state={state} emotion={emotionAnalysis?.primaryEmotion} />
			)}
		</div>
	)
}

interface RobotCharacterProps {
	state: CharacterState
	emotion?: EmotionType
}

function RobotCharacter({ state, emotion }: RobotCharacterProps) {
	// 感情優先で表情を決定
	const getEyeStyle = (): string => {
		if (emotion) {
			switch (emotion) {
				case "frustrated":
					return "fill-red-400" // 困った表情 - 赤みがかった目
				case "confident":
					return "fill-green-400" // 自信満々 - 輝く目
				case "confused":
					return "fill-blue-300" // わからない - 疑問の目
				case "happy":
					return "fill-yellow-400" // 幸せ - キラキラした目
				case "tired":
					return "fill-gray-400" // 疲れている - くすんだ目
				case "neutral":
					return "fill-blue-500" // 落ち着いている - 通常の目
			}
		}

		// 感情がない場合は既存のstateで判定
		switch (state) {
			case "happy":
				return "fill-yellow-400"
			case "thinking":
				return "fill-blue-300"
			default:
				return "fill-blue-500"
		}
	}

	const getMouthStyle = (): string => {
		if (emotion) {
			switch (emotion) {
				case "frustrated":
					return "fill-red-500" // 困った口
				case "confident":
					return "fill-green-400" // 笑顔
				case "confused":
					return "fill-blue-400" // 疑問の口
				case "happy":
					return "fill-green-400" // 大きな笑顔
				case "tired":
					return "fill-gray-400" // 平らな口
				case "neutral":
					return "fill-gray-500" // 通常の口
			}
		}

		// 感情がない場合は既存のstateで判定
		return state === "happy" ? "fill-green-400" : "fill-gray-500"
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
			<rect x="45" y="45" width="30" height="4" rx="2" className={getMouthStyle()} />

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

interface WizardCharacterProps {
	state: CharacterState
	emotion?: EmotionType
}

function WizardCharacter({ state, emotion }: WizardCharacterProps) {
	const getEyeStyle = (): string => {
		if (emotion) {
			switch (emotion) {
				case "frustrated":
					return "fill-red-400"
				case "confident":
					return "fill-green-400"
				case "confused":
					return "fill-blue-300"
				case "happy":
					return "fill-yellow-400"
				case "tired":
					return "fill-gray-400"
				case "neutral":
					return "fill-purple-500"
			}
		}
		return state === "happy" ? "fill-yellow-400" : "fill-purple-500"
	}

	const getMouthStyle = (): string => {
		if (emotion) {
			switch (emotion) {
				case "frustrated":
					return "fill-red-500"
				case "confident":
				case "happy":
					return "fill-green-400"
				case "confused":
					return "fill-blue-400"
				case "tired":
					return "fill-gray-400"
				case "neutral":
					return "fill-gray-500"
			}
		}
		return state === "happy" ? "fill-green-400" : "fill-gray-500"
	}

	return (
		<svg
			role="img"
			aria-label="まほうつかいキャラクター"
			viewBox="0 0 120 120"
			className="h-32 w-32"
		>
			{/* Body (robe) */}
			<path d="M 30 50 Q 30 100, 20 110 L 100 110 Q 90 100, 90 50 Z" className="fill-purple-600" />

			{/* Head */}
			<circle cx="60" cy="35" r="18" className="fill-purple-200" />

			{/* Hat */}
			<path d="M 45 30 L 60 5 L 75 30 Z" className="fill-purple-700" />
			<ellipse cx="60" cy="30" rx="20" ry="5" className="fill-purple-700" />

			{/* Stars on hat */}
			<circle cx="60" cy="15" r="2" className="fill-yellow-300" />

			{/* Eyes */}
			<circle cx="53" cy="33" r="3" className={getEyeStyle()} />
			<circle cx="67" cy="33" r="3" className={getEyeStyle()} />

			{/* Mouth */}
			<path
				d="M 53 40 Q 60 43, 67 40"
				className={`stroke-current ${getMouthStyle()} stroke-2 fill-none`}
			/>

			{/* Wand */}
			<line x1="90" y1="60" x2="105" y2="45" className="stroke-yellow-600 stroke-2" />
			<circle cx="105" cy="45" r="4" className="fill-yellow-400" />
		</svg>
	)
}

interface AstronautCharacterProps {
	state: CharacterState
	emotion?: EmotionType
}

function AstronautCharacter({ state, emotion }: AstronautCharacterProps) {
	const getEyeStyle = (): string => {
		if (emotion) {
			switch (emotion) {
				case "frustrated":
					return "fill-red-400"
				case "confident":
					return "fill-green-400"
				case "confused":
					return "fill-blue-300"
				case "happy":
					return "fill-yellow-400"
				case "tired":
					return "fill-gray-400"
				case "neutral":
					return "fill-blue-500"
			}
		}
		return state === "happy" ? "fill-yellow-400" : "fill-blue-500"
	}

	const getMouthStyle = (): string => {
		if (emotion) {
			switch (emotion) {
				case "frustrated":
					return "fill-red-500"
				case "confident":
				case "happy":
					return "fill-green-400"
				case "confused":
					return "fill-blue-400"
				case "tired":
					return "fill-gray-400"
				case "neutral":
					return "fill-gray-500"
			}
		}
		return state === "happy" ? "fill-green-400" : "fill-gray-500"
	}

	return (
		<svg
			role="img"
			aria-label="うちゅうひこうしキャラクター"
			viewBox="0 0 120 120"
			className="h-32 w-32"
		>
			{/* Spacesuit body */}
			<rect x="30" y="50" width="60" height="50" rx="10" className="fill-gray-100" />

			{/* Helmet */}
			<circle cx="60" cy="35" r="22" className="fill-blue-200 opacity-70" />

			{/* Head inside helmet */}
			<circle cx="60" cy="35" r="18" className="fill-pink-200" />

			{/* Eyes */}
			<circle cx="53" cy="33" r="4" className={getEyeStyle()} />
			<circle cx="67" cy="33" r="4" className={getEyeStyle()} />

			{/* Mouth */}
			<rect x="53" y="40" width="14" height="3" rx="2" className={getMouthStyle()} />

			{/* Oxygen tank */}
			<rect x="85" y="55" width="10" height="30" rx="3" className="fill-gray-400" />
			<rect x="85" y="55" width="10" height="30" rx="3" className="fill-gray-400" />

			{/* Arms */}
			<rect x="15" y="55" width="15" height="8" rx="4" className="fill-gray-100" />
			<rect x="90" y="55" width="15" height="8" rx="4" className="fill-gray-100" />

			{/* Legs */}
			<rect x="40" y="100" width="12" height="15" rx="4" className="fill-gray-200" />
			<rect x="68" y="100" width="12" height="15" rx="4" className="fill-gray-200" />

			{/* Flag */}
			<line x1="105" y1="30" x2="105" y2="60" className="stroke-gray-500 stroke-2" />
			<rect x="105" y="30" width="10" height="8" className="fill-red-500" />
		</svg>
	)
}

interface AnimalCharacterProps {
	state: CharacterState
	emotion?: EmotionType
}

function AnimalCharacter({ state, emotion }: AnimalCharacterProps) {
	const getEyeStyle = (): string => {
		if (emotion) {
			switch (emotion) {
				case "frustrated":
					return "fill-red-400"
				case "confident":
					return "fill-green-400"
				case "confused":
					return "fill-blue-300"
				case "happy":
					return "fill-yellow-400"
				case "tired":
					return "fill-gray-400"
				case "neutral":
					return "fill-brown-700"
			}
		}
		return state === "happy" ? "fill-yellow-400" : "fill-brown-700"
	}

	const getMouthStyle = (): string => {
		if (emotion) {
			switch (emotion) {
				case "frustrated":
					return "fill-red-500"
				case "confident":
				case "happy":
					return "fill-green-400"
				case "confused":
					return "fill-blue-400"
				case "tired":
					return "fill-gray-400"
				case "neutral":
					return "fill-gray-700"
			}
		}
		return state === "happy" ? "fill-green-400" : "fill-gray-700"
	}

	return (
		<svg role="img" aria-label="どうぶつキャラクター" viewBox="0 0 120 120" className="h-32 w-32">
			{/* Cat body */}
			<ellipse cx="60" cy="70" rx="35" ry="30" className="fill-orange-300" />

			{/* Head */}
			<circle cx="60" cy="35" r="20" className="fill-orange-400" />

			{/* Ears */}
			<path d="M 45 25 L 35 10 L 50 20 Z" className="fill-orange-400" />
			<path d="M 75 25 L 85 10 L 70 20 Z" className="fill-orange-400" />

			{/* Inner ears */}
			<path d="M 45 23 L 40 15 L 48 20 Z" className="fill-pink-300" />
			<path d="M 75 23 L 80 15 L 72 20 Z" className="fill-pink-300" />

			{/* Eyes */}
			<circle cx="52" cy="33" r="4" className={getEyeStyle()} />
			<circle cx="68" cy="33" r="4" className={getEyeStyle()} />

			{/* Nose */}
			<path d="M 60 38 L 57 42 L 63 42 Z" className="fill-pink-400" />

			{/* Mouth */}
			<path
				d="M 60 42 Q 55 45, 50 43"
				className={`stroke-current ${getMouthStyle()} stroke-2 fill-none`}
			/>
			<path
				d="M 60 42 Q 65 45, 70 43"
				className={`stroke-current ${getMouthStyle()} stroke-2 fill-none`}
			/>

			{/* Whiskers */}
			<line x1="30" y1="35" x2="45" y2="33" className="stroke-gray-600 stroke-1" />
			<line x1="30" y1="40" x2="45" y2="38" className="stroke-gray-600 stroke-1" />
			<line x1="75" y1="33" x2="90" y2="35" className="stroke-gray-600 stroke-1" />
			<line x1="75" y1="38" x2="90" y2="40" className="stroke-gray-600 stroke-1" />

			{/* Tail */}
			<path d="M 90 75 Q 100 65, 105 55" className="stroke-orange-400 stroke-4 fill-none" />
		</svg>
	)
}
