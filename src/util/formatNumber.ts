/**
 * Add commas to a long, positive number. Does not add comma to negative numbers.
 *
 * @param num - raw number
 */
export default function (num: number | undefined | null): string {
	if (num === undefined || num === null) return "None"

	if (num <= 999) return String(num)

	return String(num).replace(/(.)(?=(\d{3})+$)/g, "$1,")
}
