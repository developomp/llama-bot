/**
 * Cannot name file to `test.ts` because then it'll treat it like a testing file.
 */

import { ApplyOptions } from "@sapphire/decorators"

import type { Message } from "discord.js"
import type { Args, CommandOptions } from "@sapphire/framework"

import CustomCommand from "../../custom/CustomCommand"

@ApplyOptions<CommandOptions>({
	aliases: ["t"],
	description: "Tests bot features. Only available to bot owners.",
	preconditions: ["OwnersOnly"],
})
export default class TestCommand extends CustomCommand {
	usage = `> {$} [feature]

If feature is not passed, then the command will result in a error.
This is an intended behavior to make testing easier.
`

	async messageRun(message: Message, args: Args) {
		await args.pick("string").catch(() => {
			throw new Error("") // the intended behavior
		})
	}
}
