import PPCommand from "../pp"

test("Correctly builds pp list", () => {
	const ppList = PPCommand.calculatePPLengths([
		"<@123456789012345678>",
		"<@111111111111111111>",
		"<@333333333333333333>",
		"<@444444444444444444>",
	])

	expect(ppList).toStrictEqual([
		{ id: "123456789012345678", length: 24 },
		{ id: "444444444444444444", length: 13 },
		{ id: "111111111111111111", length: 11 },
		{ id: "333333333333333333", length: 2 },
	])

	expect(PPCommand.buildPPList(ppList)).toStrictEqual(`<@123456789012345678>:
8========================D **(24)**
<@444444444444444444>:
8=============D **(13)**
<@111111111111111111>:
8===========D **(11)**
<@333333333333333333>:
8==D **(2)**
`)
})
