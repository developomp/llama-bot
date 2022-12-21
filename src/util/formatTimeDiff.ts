const SECONDS_IN_A_YEAR = 60 * 60 * 24 * 365
const SECONDS_IN_A_DAY = 60 * 60 * 24
const SECONDS_IN_A_HOUR = 60 * 60
const SECONDS_IN_A_MINUTE = 60

/**
 * Formats difference in time in a readable format.
 *
 * @param startTime - Start date in millisecond
 * @param endTime - End date in millisecond
 */
export default function (startTime: number, endTime: number): string {
	let result = ""

	function addToResult(num: number, unit: string) {
		if (num) result += ` ${num} ${unit}` + (num > 1 ? "s" : "")
	}

	let diffSec = (endTime - startTime) / 1000

	// prevent empty response
	if (diffSec === 0) return "0 second"

	const years = Math.floor(diffSec / SECONDS_IN_A_YEAR)
	diffSec -= years * SECONDS_IN_A_YEAR
	addToResult(years, "year")

	const days = Math.floor(diffSec / SECONDS_IN_A_DAY)
	diffSec -= days * SECONDS_IN_A_DAY
	addToResult(days, "day")

	const hours = Math.floor(diffSec / SECONDS_IN_A_HOUR) % 24
	diffSec -= hours * SECONDS_IN_A_HOUR
	addToResult(hours, "hour")

	const minutes = Math.floor(diffSec / SECONDS_IN_A_MINUTE) % 60
	diffSec -= minutes * SECONDS_IN_A_MINUTE
	addToResult(minutes, "minute")

	addToResult(diffSec, "second")

	return result.trim()
}
