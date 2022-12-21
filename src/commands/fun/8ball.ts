import { MessageEmbed } from "discord.js"
import { ApplyOptions } from "@sapphire/decorators"

import type { Message } from "discord.js"
import type { Args, CommandOptions } from "@sapphire/framework"

import { globalObject } from "../.."
import CustomCommand from "../../custom/CustomCommand"

@ApplyOptions<CommandOptions>({
	aliases: ["8", "ball"],
	description:
		"Gives you the best advice you can get. We are not responsible for your action though.",
})
export default class EightBallCommand extends CustomCommand {
	usage = `> {$} [your question]

e.g.
> {$}

> {$} Should I buy more doge coin?
`

	async messageRun(message: Message, args: Args) {
		message.channel.sendTyping()

		//
		// Parse user input
		//

		let text = ""

		const allStr = await args.repeat("string").catch(() => "")

		if (typeof allStr === "string") {
			text = allStr
		}
		if (Array.isArray(allStr)) {
			text = allStr.join(" ")
		}

		//
		// Get response from nekos.life
		//

		const { response, url } = await globalObject.nekosClient.sfw["eightBall"]({
			text,
		})

		//
		// Reply
		//

		message.channel.send({
			embeds: [
				new MessageEmbed({
					title: response,
					image: { url },
					footer: { text: "powered by nekos.life" },
				}),
			],
		})
	}
}
