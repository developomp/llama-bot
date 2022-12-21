import { Precondition } from "@sapphire/framework"

import type { Message } from "discord.js"

/**
 * Only allow commands sent in non-DM channels
 */
export default class AdminsOnlyPrecondition extends Precondition {
	async run(message: Message) {
		if (!message.guild) return this.error()

		const guild = await message.guild.fetch()
		const member = await guild.members.fetch(message.author.id)

		if (member.permissions.has("ADMINISTRATOR")) return this.ok()
		return this.error()
	}
}
