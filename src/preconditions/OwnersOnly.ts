import { Precondition } from "@sapphire/framework"

import type { Snowflake } from "discord-api-types"
import type { Message } from "discord.js"

import { sendEmbeddedMessage } from "../util"

export default class OwnersOnlyPrecondition extends Precondition {
	// IDs of users who can run owners only commands
	owners: Snowflake[] = []

	run(message: Message) {
		if (this.owners.length <= 0) {
			// convert comma separated string to array and remove empty values
			// trailing comma and double comma can result in empty values
			this.owners = process.env.OWNER_IDS.split(",").filter((elem) => elem)
		}

		if (this.owners.includes(message.author.id)) {
			return this.ok()
		}

		sendEmbeddedMessage(message.channel, {
			title: "Permission Error!",
			description: `Only the bot owners can use this command!
[message](${message.url})`,
		})

		return this.error()
	}
}
