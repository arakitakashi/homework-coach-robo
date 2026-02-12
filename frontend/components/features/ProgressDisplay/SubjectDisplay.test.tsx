import { render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"
import { SubjectDisplay } from "./SubjectDisplay"

describe("SubjectDisplay", () => {
	it("renders subject and topic when both are provided", () => {
		render(<SubjectDisplay subject="math" topic="足し算の筆算" />)
		expect(screen.getByText("算数")).toBeInTheDocument()
		expect(screen.getByText("足し算の筆算")).toBeInTheDocument()
	})

	it("renders only subject when topic is not provided", () => {
		render(<SubjectDisplay subject="japanese" topic={undefined} />)
		expect(screen.getByText("国語")).toBeInTheDocument()
		expect(screen.queryByText(/トピック:/)).not.toBeInTheDocument()
	})

	it("renders only topic when subject is not provided", () => {
		render(<SubjectDisplay subject={undefined} topic="引き算" />)
		expect(screen.getByText("引き算")).toBeInTheDocument()
		expect(screen.queryByText("算数")).not.toBeInTheDocument()
		expect(screen.queryByText("国語")).not.toBeInTheDocument()
	})

	it("returns null when both subject and topic are not provided", () => {
		const { container } = render(<SubjectDisplay subject={undefined} topic={undefined} />)
		expect(container.firstChild).toBeNull()
	})

	it("has accessible section with label", () => {
		render(<SubjectDisplay subject="math" topic="掛け算" />)
		const section = screen.getByRole("region", { name: "現在の学習内容" })
		expect(section).toBeInTheDocument()
	})

	it("renders math subject with correct colors", () => {
		render(<SubjectDisplay subject="math" topic="割り算" />)
		expect(screen.getByLabelText("現在の科目: 算数")).toBeInTheDocument()
	})

	it("renders japanese subject with correct colors", () => {
		render(<SubjectDisplay subject="japanese" topic="漢字" />)
		expect(screen.getByLabelText("現在の科目: 国語")).toBeInTheDocument()
	})
})
