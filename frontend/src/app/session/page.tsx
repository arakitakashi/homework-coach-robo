import type { Metadata } from "next"
import { redirect } from "next/navigation"
import { isValidCharacter } from "@/lib/validation/characterValidation"
import { SessionContent } from "./SessionContent"

export const metadata: Metadata = {
	title: "セッション | 宿題コーチロボット",
	description: "一緒に宿題を解こう",
}

interface SessionPageProps {
	searchParams: Promise<{
		character?: string
	}>
}

export default async function SessionPage({ searchParams }: SessionPageProps) {
	const params = await searchParams
	const character = params.character

	// 不正なキャラクターの場合、トップページにリダイレクト
	if (!isValidCharacter(character)) {
		redirect("/")
	}

	return <SessionContent characterType={character} />
}
