import { Formatters, MessageEmbed } from "discord.js"
import { ApplyOptions } from "@sapphire/decorators"

import type { Message } from "discord.js"
import type { Args, CommandOptions } from "@sapphire/framework"

import CustomCommand from "../../custom/CustomCommand"

@ApplyOptions<CommandOptions>({
	aliases: ["c", "clap"],
	description:
		"Does the annoying Karen clap.👏Does👏not👏work👏with👏external👏emojis.",
})
export default class ClapifyCommand extends CustomCommand {
	usage = `> {$} [message to clapify]

e.g.
> {$} I said bring me the manager.
`

	async messageRun(message: Message, args: Args): Promise<void> {
		const inputs = await args.repeat("string").catch(() => [])

		//
		// Handle empty argument
		//

		if (!inputs) {
			message.channel.send({
				embeds: [
					new MessageEmbed({
						title: "Error!",
						description: "What should I clapify?",
					}),
				],
			})

			return
		}

		//
		// Reply
		//

		message.channel.send({
			embeds: [
				new MessageEmbed({
					description: `**${Formatters.userMention(message.author.id)} says:**

${ClapifyCommand.clapify(inputs)}`,
				}),
			],
		})
	}

	static clapify(inputs: string[]): string {
		return inputs.join("👏")
	}
}
