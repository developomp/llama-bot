import highlightIndex from "../highlightIndex"

test("Correctly highlights entry", () => {
	const array = ["A", "B", "C"]

	expect(highlightIndex(array, -1)).toStrictEqual("A / B / C")
	expect(highlightIndex(array, 0)).toStrictEqual("**A** / B / C")
	expect(highlightIndex(array, 1)).toStrictEqual("A / **B** / C")
	expect(highlightIndex(array, 2)).toStrictEqual("A / B / **C**")
	expect(highlightIndex(array, 3)).toStrictEqual("A / B / C")

	expect(highlightIndex([], 0)).toStrictEqual("")
})
