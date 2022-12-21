/**
 * Formats {@link date} to `YYYY-MM-DD hh:mm:ss`.
 *
 * @param date - Raw date object
 */
export default function (date: Date): string {
	const YYYY = date.getFullYear()
	const MM = date.getMonth() + 1 // starts from 0 for some reason
	const DD = date.getDate()

	const hh = date.getHours()
	const mm = date.getMinutes()
	const ss = date.getSeconds()

	return `${YYYY}-${MM}-${DD} ${hh}:${mm}:${ss}`
}
