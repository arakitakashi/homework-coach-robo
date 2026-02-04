import type { Metadata } from "next"
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
	const characterType = (params.character || "robot") as "robot" | "wizard" | "astronaut" | "animal"

	return <SessionContent characterType={characterType} />
}
