/**
 * Counts the number of days in between {@link startDate} and {@link endDate}.
 *
 * - Returns NaN if either of the arguments are NaN.
 * - Result could be a negative number if the {@link startDate} is greater than {@link endDate}.
 *
 * @param startDate - Starting date in milliseconds
 * @param endDate - Ending date in milliseconds
 */
export default function (startDate: number, endDate: number): number {
	return Math.ceil((endDate - startDate) / (1000 * 60 * 60 * 24))
}
