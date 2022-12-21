// todo: nitro boost

import { Formatters, MessageEmbed } from "discord.js"
import { CommandOptions } from "@sapphire/framework"
import { ApplyOptions } from "@sapphire/decorators"

import type { GuildMember, Message } from "discord.js"
import type { Args } from "@sapphire/framework"

import { formatDate, formatTimeDiff } from "../../util"
import CustomCommand from "../../custom/CustomCommand"

@ApplyOptions<CommandOptions>({
	aliases: ["ui"],
	description: "Shows information about a user.",
})
export default class UserInfoCommand extends CustomCommand {
	usage = `> {$} [user]

e.g.
Get your user info
> {$}

Get someone else's user info by mentioning
> {$} @someone

Get someone else's user info with user id
> {$} 123456789012345678
`

	async messageRun(message: Message, args: Args) {
		let user = await args.pick("user").catch(() => undefined)

		if (!user) user = message.author

		const avatarURL = user.avatarURL() || undefined

		const resultEmbed = new MessageEmbed({
			author: { name: user.tag, icon_url: avatarURL },
			thumbnail: { url: avatarURL },
			description: Formatters.userMention(user.id),
			footer: { text: `USER ID: ${user.id}` },
		})

		resultEmbed.addField(
			"Discord join date",
			this.formattedJoinDate(user.createdAt)
		)

		if (message.guild) {
			const member = await message.guild.members.fetch(user.id)

			resultEmbed.addField(
				"Server join date",
				this.formattedJoinDate(member.joinedAt)
			)

			const roleMentions = this.getMemberRoles(member, message.guild.id)
			resultEmbed.addField(
				`Roles (${roleMentions.length})`,
				roleMentions.join(" ")
			)
		}

		message.channel.send({
			embeds: [resultEmbed],
		})
	}

	formattedJoinDate(joinedAt: Date | null): string {
		let result = "Unknown"

		if (joinedAt) {
			const xAgo = formatTimeDiff(joinedAt.getTime(), Date.now())

			result = `${formatDate(joinedAt)}\n${xAgo} ago`
		}

		return result
	}

	getMemberRoles(member: GuildMember, guildID: string): string[] {
		return [...member.roles.cache.entries()] // returns a list if [role_id, Role]
			.map((elem) => elem[0]) // only get role IDs
			.filter((value) => value != guildID) // remove @everyone role
			.map((id) => Formatters.roleMention(id)) // converts role ID to mention string
	}

	// converts "SOMETHING_LIKE_THIS" to "Something Like This"
	// from https://stackoverflow.com/a/32589289/12979111
	convertCase(input: string): string {
		return input
			.replace(/_/g, " ")
			.toLowerCase()
			.split(" ")
			.map((word) => word.charAt(0).toUpperCase() + word.substring(1))
			.join(" ")
	}
}
