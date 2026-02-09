"use client"

import { AnimatePresence, motion } from "framer-motion"
import { useAtom } from "jotai"
import { activeAgentAtom } from "@/store/atoms/phase2"
import type { AgentType } from "@/types/phase2"
import { AgentIcon } from "./AgentIcon"

// エージェント名のマッピング
const AGENT_LABELS: Record<AgentType, string> = {
	router: "ルーター",
	math_coach: "算数コーチ",
	japanese_coach: "国語コーチ",
	encouragement: "励まし",
	review: "振り返り",
}

export function AgentIndicator() {
	const [activeAgent] = useAtom(activeAgentAtom)

	if (!activeAgent) {
		return null // エージェントがアクティブでない場合は非表示
	}

	return (
		<AnimatePresence mode="wait">
			<motion.div
				key={activeAgent.type}
				initial={{ opacity: 0, y: -10 }}
				animate={{ opacity: 1, y: 0 }}
				exit={{ opacity: 0, y: 10 }}
				transition={{ duration: 0.3 }}
				className="flex items-center gap-2 rounded-lg bg-blue-50 px-3 py-2 text-sm"
				aria-label={`現在のエージェント: ${AGENT_LABELS[activeAgent.type]}`}
			>
				<AgentIcon type={activeAgent.type} />
				<span className="font-medium text-blue-700">{AGENT_LABELS[activeAgent.type]}</span>
			</motion.div>
		</AnimatePresence>
	)
}
