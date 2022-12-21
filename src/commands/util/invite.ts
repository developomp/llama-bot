import { CommandOptions } from "@sapphire/framework"
import { ApplyOptions } from "@sapphire/decorators"
import { MessageEmbed } from "discord.js"

import type { Message } from "discord.js"

import CustomCommand from "../../custom/CustomCommand"

@ApplyOptions<CommandOptions>({
	description: "Shows information about inviting the bot.",
})
export default class InviteCommand extends CustomCommand {
	usage = "> {$}"

	async messageRun(message: Message) {
		message.channel.send({
			embeds: [
				new MessageEmbed({
					title: "Sorry",
					description: `Sorry, but only the owner can invite the bot.
Check the [documentation](https://docs.llama.developomp.com/docs/overview#can-i-use-this-bot-in-my-discord-server) for more information.`,
				}),
			],
		})
	}
}
