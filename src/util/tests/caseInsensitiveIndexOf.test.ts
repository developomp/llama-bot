import caseInsensitiveIndexOf from "../caseInsensitiveIndexOf"

test("Correctly identifies index", () => {
	const array = ["A", "B", "C", "D"]

	array.map((entry, index) => {
		expect(caseInsensitiveIndexOf(array, entry.toLowerCase())).toStrictEqual(
			index
		)
	})

	expect(
		caseInsensitiveIndexOf(array, "this does not exist in the array")
	).toStrictEqual(-1)

	expect(caseInsensitiveIndexOf([], "testing empty array")).toStrictEqual(-1)
})
