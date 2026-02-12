import type { Metadata } from "next"
import Link from "next/link"

export const metadata: Metadata = {
	title: "ページがみつかりません | 宿題コーチロボット",
	description: "404 Not Found",
}

/**
 * 404 Not Foundページ
 *
 * 存在しないURLにアクセスした際に表示されるカスタム404ページ。
 * 小学校低学年向けに優しい日本語で表示します。
 */
export default function NotFoundPage() {
	return (
		<main className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-b from-blue-50 to-purple-50 p-4">
			<div className="text-center">
				{/* 404タイトル */}
				<h1 className="text-9xl font-bold text-gray-300 mb-4">404</h1>

				{/* キャラクター */}
				<div className="text-8xl mb-8 animate-bounce">🤖</div>

				{/* メッセージ */}
				<p className="text-3xl font-bold text-gray-700 mb-8">このページは みつからないよ</p>

				{/* トップページへのリンク */}
				<Link
					href="/"
					className="inline-block px-8 py-4 bg-blue-500 text-white text-xl font-bold rounded-full hover:bg-blue-600 transition-colors"
				>
					トップページにもどる →
				</Link>
			</div>
		</main>
	)
}
