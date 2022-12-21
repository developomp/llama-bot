import ClapifyCommand from "../clapify"

test("Correctly adds clap between the words", () => {
	expect(
		ClapifyCommand.clapify([
			"<@123456789012345678>",
			"<#123456789012345678>",
			"<@&123456789012345678>",
			"word",
			"1234",
		])
	).toStrictEqual(
		"<@123456789012345678>👏<#123456789012345678>👏<@&123456789012345678>👏word👏1234"
	)
})
