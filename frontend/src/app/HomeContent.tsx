"use client"

import { useRouter } from "next/navigation"
import { useState } from "react"
import { Button } from "@/components/ui/Button"
import { Card } from "@/components/ui/Card"
import type { CharacterType } from "@/types"

const characters: { type: CharacterType; label: string; emoji: string }[] = [
	{ type: "robot", label: "ロボット", emoji: "🤖" },
	{ type: "wizard", label: "まほうつかい", emoji: "🧙" },
	{ type: "astronaut", label: "うちゅうひこうし", emoji: "🚀" },
	{ type: "animal", label: "どうぶつ", emoji: "🐻" },
]

export function HomeContent() {
	const router = useRouter()
	const [selectedCharacter, setSelectedCharacter] = useState<CharacterType>("robot")

	const handleStart = () => {
		router.push(`/session?character=${selectedCharacter}`)
	}

	return (
		<main className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-b from-blue-50 to-purple-50 p-4">
			<div className="w-full max-w-md space-y-8">
				{/* タイトル */}
				<div className="text-center">
					<h1 className="text-3xl font-bold text-purple-600">宿題コーチロボット</h1>
					<p className="mt-2 text-gray-600">いっしょに がんばろう！</p>
				</div>

				{/* キャラクター選択 */}
				<Card padding="large">
					<h2 className="mb-4 text-center text-lg font-semibold text-gray-700">
						キャラクターを選んでね
					</h2>
					<div className="grid grid-cols-2 gap-3">
						{characters.map(({ type, label, emoji }) => (
							<button
								key={type}
								type="button"
								onClick={() => setSelectedCharacter(type)}
								aria-pressed={selectedCharacter === type}
								className={`
									flex flex-col items-center rounded-xl p-4 transition-all
									${
										selectedCharacter === type
											? "bg-purple-100 ring-2 ring-purple-500"
											: "bg-gray-50 hover:bg-gray-100"
									}
								`}
							>
								<span className="text-4xl">{emoji}</span>
								<span className="mt-2 text-sm font-medium text-gray-700">{label}</span>
							</button>
						))}
					</div>
				</Card>

				{/* スタートボタン */}
				<Button variant="primary" size="large" onClick={handleStart} className="w-full text-xl">
					はじめる
				</Button>
			</div>
		</main>
	)
}
