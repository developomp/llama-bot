import { MessageEmbed } from "discord.js"

import type {
	BaseGuildTextChannel,
	Message,
	MessageEmbedOptions,
	TextBasedChannel,
} from "discord.js"

/**
 * Sends message with one embed.
 *
 * @param channel - Text channel to send the embedded message
 * @param data - Message content to send
 */
export default function (
	channel: BaseGuildTextChannel | TextBasedChannel,
	data: MessageEmbed | MessageEmbedOptions
): Promise<Message<boolean>> {
	return channel.send({
		embeds: [new MessageEmbed(data)],
	})
}
