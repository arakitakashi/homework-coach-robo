"use client"

import { useCallback } from "react"
import { useAudioPlayer, useVoiceRecorder } from "@/lib/hooks"

interface VoiceInterfaceProps {
	onAudioData: (data: ArrayBuffer) => void
	isConnected: boolean
}

export function VoiceInterface({ onAudioData, isConnected }: VoiceInterfaceProps) {
	const { recordingState, audioLevel, startRecording, stopRecording } = useVoiceRecorder({
		onAudioData,
	})
	const { isPlaying } = useAudioPlayer()

	const isRecording = recordingState === "recording"

	const handleToggleRecording = useCallback(async () => {
		if (isRecording) {
			stopRecording()
		} else {
			await startRecording()
		}
	}, [isRecording, startRecording, stopRecording])

	const getStatusText = () => {
		if (!isConnected) return "接続中..."
		if (isPlaying) return "聞いているよ"
		if (isRecording) return "録音中..."
		return "話しかけてね"
	}

	const getButtonLabel = () => {
		if (isRecording) return "録音を止める"
		return "録音を開始"
	}

	return (
		<div className="flex flex-col items-center gap-4">
			{/* Audio Level Visualizer */}
			<div className="relative h-2 w-48 overflow-hidden rounded-full bg-gray-200">
				<div
					className="absolute left-0 top-0 h-full bg-blue-500 transition-all duration-100"
					style={{ width: `${audioLevel * 100}%` }}
				/>
			</div>

			{/* Status Text */}
			<p className="text-lg font-medium text-gray-700">{getStatusText()}</p>

			{/* Record Button */}
			<button
				type="button"
				onClick={handleToggleRecording}
				disabled={!isConnected}
				aria-label={getButtonLabel()}
				aria-pressed={isRecording}
				className={`
          flex h-20 w-20 items-center justify-center rounded-full
          transition-all duration-200
          focus:outline-none focus:ring-4 focus:ring-blue-300
          ${
						isRecording
							? "animate-pulse bg-red-500 hover:bg-red-600"
							: "bg-blue-500 hover:bg-blue-600"
					}
          ${!isConnected ? "cursor-not-allowed opacity-50" : ""}
        `}
			>
				<svg
					xmlns="http://www.w3.org/2000/svg"
					className="h-10 w-10 text-white"
					fill="none"
					viewBox="0 0 24 24"
					stroke="currentColor"
					aria-hidden="true"
				>
					{isRecording ? (
						<rect x="6" y="6" width="12" height="12" strokeWidth={2} fill="currentColor" />
					) : (
						<path
							strokeLinecap="round"
							strokeLinejoin="round"
							strokeWidth={2}
							d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
						/>
					)}
				</svg>
			</button>
		</div>
	)
}
