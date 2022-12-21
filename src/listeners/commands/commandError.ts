import { Listener } from "@sapphire/framework"

import type { CommandErrorPayload } from "@sapphire/framework"

/**
 * Gets executed when the bot encounters an error.
 */
export class CommandError extends Listener {
	run(_error: unknown, payload: CommandErrorPayload) {
		this.logToConsole(payload)
		this.logToChannels(payload)
		this.logToFirebase(payload)
	}

	async logToConsole(payload: CommandErrorPayload): Promise<void> {
		const message = payload.message
		const author = message.author

		console.error(`
===============[ ERROR ]===============
Author:  ${author.id} (${author.tag})
URL:     ${message.url}
Content: ${message.content}
=======================================
`)
	}

	// eslint-disable-next-line @typescript-eslint/no-unused-vars
	async logToChannels(payload: CommandErrorPayload): Promise<void> {
		//
	}

	// eslint-disable-next-line @typescript-eslint/no-unused-vars
	async logToFirebase(payload: CommandErrorPayload): Promise<void> {
		//
	}
}
