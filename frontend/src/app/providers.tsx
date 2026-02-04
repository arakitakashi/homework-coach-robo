"use client"

import { Provider } from "jotai"
import type { ReactNode } from "react"

interface ProvidersProps {
	children: ReactNode
}

export function Providers({ children }: ProvidersProps) {
	return <Provider>{children}</Provider>
}
