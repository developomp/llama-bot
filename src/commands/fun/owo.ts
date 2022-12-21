import { Formatters, MessageEmbed } from "discord.js"
import { CommandOptions } from "@sapphire/framework"
import { ApplyOptions } from "@sapphire/decorators"

import type { Message } from "discord.js"
import type { Args } from "@sapphire/framework"

import { globalObject } from "../.."
import CustomCommand from "../../custom/CustomCommand"

@ApplyOptions<CommandOptions>({
	aliases: ["owoify"],
	description: "OwOifies youw message OwO",
})
export default class CatCommand extends CustomCommand {
	usage = "> {$} [message to owoify]"

	async messageRun(message: Message, args: Args) {
		message.channel.sendTyping()

		// combine all arguments to a single string
		const input = [...(await args.repeat("string").catch(() => ""))].join(" ")

		message.channel.send({
			embeds: [
				new MessageEmbed({
					title: "OwO",
					description: `**${Formatters.userMention(message.author.id)} says:**

${
	(
		await globalObject.nekosClient.sfw.OwOify({
			text: input,
		})
	).owo
}`,
					footer: { text: "powered by nekos.life" },
				}),
			],
		})
	}
}
