/**
 * From [URI.js](https://github.com/medialize/URI.js).
 * More information can be found in [this stackOverflow answer](https://stackoverflow.com/a/11209098).
 */
const pattern =
	/\b((?:[a-z][\w-]+:(?:\/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.-]+[.][a-z]{2,4}\/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()[\]{};:'".,<>?«»“”‘’]))/gi

/**
 * Extract URLs from string
 *
 * @param input - Raw string to check
 */
export default function (input: string): string[] {
	return input.match(pattern) || []
}
