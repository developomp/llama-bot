import type { Message } from "discord.js"

/**
 * Checks if channel where the message sent is a NSFW channel.
 *
 * @param message - Message to get the channel
 */
export default function (message: Message): boolean {
	return Reflect.get(message.channel, "nsfw") === true
}
