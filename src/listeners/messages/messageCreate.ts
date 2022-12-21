import { Listener } from "@sapphire/framework"

import type { Message } from "discord.js"

import { sendEmbeddedMessage } from "../../util"

/**
 * Gets executed when a message is sent
 */
export class MessageCreate extends Listener {
	autoDeleteSeconds = 10

	run(message: Message) {
		if (message.channel.type === "DM") this.handleDMs(message)
	}

	async handleDMs(message: Message): Promise<void> {
		// ignore messages from other bots (or even itself)
		if (message.author.bot) return

		const responseMessage = await sendEmbeddedMessage(message.channel, {
			title: "❗ DM commands are not supported.",
			description: `Add a broom (🧹) emoji to a messages sent by me to delete them.
This message will deleted in ${this.autoDeleteSeconds} seconds.`,
		})

		await new Promise((resolve) =>
			setTimeout(resolve, this.autoDeleteSeconds * 1000)
		)

		responseMessage.delete()
	}
}
