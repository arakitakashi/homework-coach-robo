import { render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"
import { TopicLabel } from "./TopicLabel"

describe("TopicLabel", () => {
	it("renders topic text", () => {
		render(<TopicLabel topic="足し算の筆算" />)
		expect(screen.getByText("トピック:")).toBeInTheDocument()
		expect(screen.getByText("足し算の筆算")).toBeInTheDocument()
	})

	it("renders long topic text", () => {
		const longTopic = "二桁の掛け算と割り算の組み合わせ問題の解き方"
		render(<TopicLabel topic={longTopic} />)
		expect(screen.getByText(longTopic)).toBeInTheDocument()
	})

	it("has accessible structure", () => {
		render(<TopicLabel topic="引き算" />)
		// トピックラベルがテキストとして表示されていることを確認
		expect(screen.getByText(/トピック:/)).toBeInTheDocument()
		expect(screen.getByText("引き算")).toBeInTheDocument()
	})
})
