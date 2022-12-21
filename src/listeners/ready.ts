import { ApplyOptions } from "@sapphire/decorators"
import { Listener } from "@sapphire/framework"
import { gray, yellow } from "colorette"

import type { ListenerOptions } from "@sapphire/framework"

import { globalObject } from ".."

const y = yellow

@ApplyOptions<ListenerOptions>({
	once: true,
})
export class Ready extends Listener {
	run() {
		globalObject.startTime = Date.now()

		this.printReady()
	}

	printReady(): void {
		const botTag = this.container.client.user?.tag || "unknown bot tag"
		const botID = this.container.client.user?.id || "unknown bot ID"
		const botMode =
			process.env.TESTING === "true" ? "DEVELOPMENT" : "PRODUCTION"

		console.log(
			gray(`
${y(botTag)} (ID: ${y(botID)}) is Ready!
Mode: ${y(botMode)}
`)
		)
	}
}
