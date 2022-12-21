import formatNumber from "../formatNumber"

test("Correctly formats numbers", () => {
	expect(formatNumber(1_000)).toStrictEqual("1,000")
	expect(formatNumber(999_999_999)).toStrictEqual("999,999,999")
	expect(formatNumber(0)).toStrictEqual("0")
	expect(formatNumber(-0)).toStrictEqual("0")
	expect(formatNumber(-1_000)).toStrictEqual("-1000")
	expect(formatNumber(-999_999_999)).toStrictEqual("-999999999")
})
