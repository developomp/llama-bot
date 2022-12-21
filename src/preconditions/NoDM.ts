import { Precondition } from "@sapphire/framework"

import type { Message } from "discord.js"

/**
 * Only allow commands sent in non-DM channels
 */
export default class NoDMPrecondition extends Precondition {
	run(message: Message) {
		if (message.channel.type === "DM") return this.error()

		return this.ok()
	}
}
