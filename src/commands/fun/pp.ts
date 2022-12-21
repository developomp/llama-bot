import { Formatters } from "discord.js"
import { ApplyOptions } from "@sapphire/decorators"

import type { Message } from "discord.js"
import type { Args, CommandOptions } from "@sapphire/framework"

import { sendEmbeddedMessage } from "../../util"
import CustomCommand from "../../custom/CustomCommand"

interface PPUser {
	id: string
	length: number
}

@ApplyOptions<CommandOptions>({
	aliases: ["penis"],
	description: `Measure user's pp length and arrange them in descending order.

Shortest length (0):
\`8D\`
Longest length (30):
\`8==============================D\`

This is 101% accurate.`,
})
export default class PPCommand extends CustomCommand {
	usage = `> {$} [user]*

e.g.
Measure yourself:
> {$}

Measure someone else's pp:
> {$} @someone

Measure multiple people's pp:
> {$} @someone @sometwo ...
`

	async messageRun(message: Message, args: Args) {
		let membersRaw: string[] = await args.repeat("string").catch(() => [])

		//  handle 0 argument case
		if (membersRaw.length <= 0) {
			if (!message.member) {
				sendEmbeddedMessage(message.channel, {
					title: "Error",
					description: "Failed to get user",
				})

				return
			}

			membersRaw = [message.author.id]
		}

		const users = PPCommand.calculatePPLengths(membersRaw)
		sendEmbeddedMessage(message.channel, {
			title: "pp",
			description: PPCommand.buildPPList(users),
		})
	}

	/**
	 * Calculates pp lengths for a list of people.
	 *
	 * @param membersRaw - A list of discord snowflakes to convert to pp length.
	 * @returns A sorted array of users from lowest to highest.
	 */
	static calculatePPLengths(membersRaw: string[]): PPUser[] {
		const users: PPUser[] = []

		for (const memberRaw of membersRaw) {
			const numbersInString = memberRaw.match(/\d+/)
			if (!numbersInString) continue
			const memberIDStr = numbersInString[0]
			if (!memberIDStr) continue
			const memberID = parseInt(memberIDStr)
			if (!memberID) continue

			try {
				users.push({
					id: memberIDStr,
					length: memberID % 31 /* Calculation happens here */,
				})
			} catch (e) {
				continue
			}
		}

		// sort users ascending by pp length
		users.sort((prev, curr) => curr.length - prev.length)

		return users
	}

	/**
	 * Builds the final text that will be shown to the user.
	 *
	 * @param users - A list of user and their pp size.
	 */
	static buildPPList(users: PPUser[]): string {
		let ppList = ""

		for (const user of users) {
			const userMention = Formatters.userMention(user.id)

			ppList += `${userMention}:\n`
			ppList += `8${"=".repeat(user.length)}D **(${user.length})**\n`
		}

		return ppList
	}
}
