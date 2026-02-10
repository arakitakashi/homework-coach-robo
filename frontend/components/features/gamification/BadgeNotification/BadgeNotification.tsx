/**
 * バッジ獲得通知コンポーネント
 */

"use client"

import { AnimatePresence, motion } from "framer-motion"
import { useAtomValue } from "jotai"
import * as LucideIcons from "lucide-react"
import { recentBadgeAtom } from "@/store/atoms/gamification"
import type { Badge } from "@/types/gamification"

/**
 * バッジカテゴリに応じた色を取得
 */
function getCategoryColor(category: Badge["category"]) {
	switch (category) {
		case "achievement":
			return "from-yellow-400 to-orange-500"
		case "streak":
			return "from-red-400 to-pink-500"
		case "mastery":
			return "from-purple-400 to-blue-500"
		default:
			return "from-gray-400 to-gray-500"
	}
}

/**
 * BadgeNotification コンポーネント
 *
 * バッジ獲得時にトースト通知を表示します
 */
export function BadgeNotification() {
	const recentBadge = useAtomValue(recentBadgeAtom)

	// アイコンコンポーネントを動的に取得
	// 動的インポートは警告されるが、バッジごとに異なるアイコンをロードするため必要
	const IconComponent = recentBadge
		? (LucideIcons[recentBadge.iconName as keyof typeof LucideIcons] as React.ComponentType<{
				className?: string
			}>)
		: null

	return (
		<AnimatePresence>
			{recentBadge && (
				<motion.div
					initial={{ opacity: 0, y: -50, scale: 0.8 }}
					animate={{ opacity: 1, y: 0, scale: 1 }}
					exit={{ opacity: 0, y: -20, scale: 0.9 }}
					transition={{
						type: "spring",
						stiffness: 300,
						damping: 20,
					}}
					role="alert"
					aria-live="polite"
					className="fixed top-4 right-4 z-50 max-w-sm"
				>
					<div
						className={`
              p-4 rounded-lg shadow-2xl border-2 border-white
              bg-gradient-to-r ${getCategoryColor(recentBadge.category)}
            `}
					>
						<div className="flex items-start gap-3">
							{/* アイコン */}
							{IconComponent && (
								<div className="flex-shrink-0">
									<IconComponent className="w-8 h-8 text-white" />
								</div>
							)}

							{/* テキスト */}
							<div className="flex-1 min-w-0">
								<p className="text-sm font-bold text-white mb-1">🏆 バッジ獲得！</p>
								<p className="text-base font-bold text-white mb-1">{recentBadge.name}</p>
								<p className="text-sm text-white/90">{recentBadge.description}</p>
							</div>
						</div>
					</div>
				</motion.div>
			)}
		</AnimatePresence>
	)
}
