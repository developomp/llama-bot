import { MessageEmbed } from "discord.js"
import { ApplyOptions } from "@sapphire/decorators"

import type { Message } from "discord.js"
import type { CommandOptions } from "@sapphire/framework"

import { globalObject } from "../.."
import CustomCommand from "../../custom/CustomCommand"

@ApplyOptions<CommandOptions>({
	aliases: ["f", "facts"],
	description: "Shows useless facts.",
})
export default class FactCommand extends CustomCommand {
	usage = "> {$}"

	async messageRun(message: Message) {
		message.channel.sendTyping()

		message.channel.send({
			embeds: [
				new MessageEmbed({
					title: "Here's a fact for you",
					description: (await globalObject.nekosClient.sfw.fact()).fact,
					footer: { text: "powered by nekos.life" },
				}),
			],
		})
	}
}
