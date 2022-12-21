import { SnowflakeUtil, MessageEmbed } from "discord.js"
import { ApplyOptions } from "@sapphire/decorators"

import type { Message } from "discord.js"
import type { CommandOptions } from "@sapphire/framework"

import { countDays, formatDate, formatTimeDiff } from "../../util"
import { globalObject } from "../.."
import CustomCommand from "../../custom/CustomCommand"

@ApplyOptions<CommandOptions>({
	aliases: ["a", "u", "uptime"],
	description: "Shows basic information about the bot.",
})
export default class AboutCommand extends CustomCommand {
	usage = "> {$}"

	async messageRun(message: Message) {
		const now = message.editedTimestamp || message.createdTimestamp
		const startTime = globalObject.startTime

		if (!startTime || !this.container.client.id)
			return this.failedToGetStartTime(message)

		const formattedUptime = formatTimeDiff(startTime, now)
		const botCreatedTime = SnowflakeUtil.deconstruct(this.container.client.id)
		const formattedBotCreationDate = formatDate(botCreatedTime.date)
		const botAgeInDays = countDays(botCreatedTime.date.getTime(), now)

		const serversCount = this.container.client.guilds.cache.size || 0

		message.channel.send({
			embeds: [
				new MessageEmbed({
					title: "About",
					fields: [
						{
							name: "Creation date in UTC",
							value: `${formattedBotCreationDate} (${botAgeInDays} days ago)`,
							inline: true,
						},
						{
							name: "Uptime",
							value: formattedUptime,
							inline: true,
						},
						{
							name: "Servers",
							value: `The bot is in ${serversCount} server${
								serversCount > 1 ? "s" : ""
							}.`,
							inline: true,
						},
						{
							name: "Source Code",
							value: "https://github.com/llama-bot",
							inline: false,
						},
					],
				}),
			],
		})
	}

	failedToGetStartTime(message: Message): void {
		message.channel.send({
			embeds: [
				new MessageEmbed({
					title: "Failed to run command",
					description:
						"The bot failed to get one or more information about the bot.",
				}),
			],
		})
	}
}
