import formatDate from "../formatDate"

test("Properly formats date", () => {
	expect(formatDate(new Date("Feb 22, 2022 22:22:22"))).toStrictEqual(
		"2022-2-22 22:22:22"
	)

	expect(formatDate(new Date("2022/02/22 22:22:22"))).toStrictEqual(
		"2022-2-22 22:22:22"
	)
})
