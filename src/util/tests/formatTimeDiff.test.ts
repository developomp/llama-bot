import formatTimeDiff from "../formatTimeDiff"

test("Correctly formats time", () => {
	expect(
		formatTimeDiff(
			new Date("2022/02/22").getTime(),
			new Date("2023/02/23 01:01:01").getTime()
		)
	).toStrictEqual("1 year 1 day 1 hour 1 minute 1 second")

	expect(
		formatTimeDiff(
			new Date("2022/02/22").getTime(),
			new Date("2024/02/24 02:02:02").getTime()
		)
	).toStrictEqual("2 years 2 days 2 hours 2 minutes 2 seconds")

	expect(
		formatTimeDiff(
			new Date("2022/02/22").getTime(),
			new Date("2022/02/22").getTime()
		)
	).toStrictEqual("0 second")
})
