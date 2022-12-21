import { SnowflakeUtil, MessageEmbed } from "discord.js"
import { ApplyOptions } from "@sapphire/decorators"

import type { Message } from "discord.js"
import type { Args, CommandOptions } from "@sapphire/framework"

import { countDays, formatDate, formatTimeDiff } from "../../util"
import CustomCommand from "../../custom/CustomCommand"

@ApplyOptions<CommandOptions>({
	aliases: ["s"],
	description: "Calculates when a discord ID (snowflake) was created.",
})
export default class SnowflakeCommand extends CustomCommand {
	usage = "> {$} <discord snowflake>"

	async messageRun(message: Message, args: Args) {
		let input: string

		try {
			input = await args.pick("string")
		} catch {
			message.channel.send({
				embeds: [
					new MessageEmbed({
						title: "Error",
						description: "You did not pass any snowflake :(",
					}),
				],
			})

			return
		}

		try {
			const now = message.editedTimestamp || message.createdTimestamp
			const creationDate = SnowflakeUtil.deconstruct(input).date
			const dateDelta = countDays(creationDate.getTime(), now)

			message.channel.send({
				embeds: [
					new MessageEmbed({
						title: input,
						fields: [
							{
								name: "Creation Date (UTC)",
								value: `${formatDate(creationDate)} (${dateDelta} days ago)`,
							},
							{
								name: "Age",
								value: formatTimeDiff(creationDate.getTime(), now),
							},
						],
					}),
				],
			})
		} catch {
			message.channel.send({
				embeds: [
					new MessageEmbed({
						title: "Error",
						description: `Failed to parse snowflake \`${input}\``,
					}),
				],
			})
		}
	}
}
