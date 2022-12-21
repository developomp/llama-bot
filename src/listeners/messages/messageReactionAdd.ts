import { Listener } from "@sapphire/framework"

import type { MessageReaction, PartialMessageReaction } from "discord.js"

import { settings, fetchSettings } from "../../DB"

/**
 * Gets executed when a reaction is added to a message
 */
export class MessageReactionAdd extends Listener {
	run(reaction: MessageReaction | PartialMessageReaction) {
		if (reaction.message.channel.type === "DM") this.handleDMs(reaction)
	}

	async handleDMs(
		reaction: MessageReaction | PartialMessageReaction
	): Promise<void> {
		const message = await reaction.message.fetch()

		if (
			!reaction.emoji.name ||
			!this.container.client.id ||
			this.container.client.id !== message.author.id
		)
			return

		if (!settings.clear_emojis) await fetchSettings()

		if (settings.clear_emojis?.includes(reaction.emoji.name)) message.delete()
	}
}
