import { SapphireClient } from "@sapphire/framework"
import { start as startPrettyError } from "pretty-error"
import nekosClient from "nekos.life"
import dotenv from "dotenv"
import "./DB"

function initializeEnv() {
	dotenv.config()
	// do not start the bot if token is not found
	if (!process.env.TOKEN) throw Error("Token not found!")

	// set to default values if not defined already
	process.env.TESTING ??= "false"
	process.env.PREFIX_PROD ??= "-"
	process.env.PREFIX_DEV ??= "b-"

	process.env.PREFIX =
		process.env.TESTING == "true"
			? process.env.PREFIX_DEV
			: process.env.PREFIX_PROD
}

function initialize() {
	startPrettyError()
	initializeEnv()
}

initialize()

export const globalObject = {
	startTime: 0,
	nekosClient: new nekosClient(),
}

const client = new SapphireClient({
	caseInsensitiveCommands: true,
	caseInsensitivePrefixes: true,
	defaultPrefix: process.env.PREFIX,
	partials: [
		// necessary for DM events to work
		// https://discordjs.guide/popular-topics/partials.html#enabling-partials

		"CHANNEL",

		// necessary for reaction detection to work

		"MESSAGE",
		"REACTION",
		"USER",
	],
	intents: [
		"DIRECT_MESSAGE_REACTIONS",
		"DIRECT_MESSAGE_TYPING",
		"DIRECT_MESSAGES",

		"GUILD_MESSAGE_REACTIONS",
		"GUILD_MESSAGE_TYPING",
		"GUILD_MESSAGES",
	],
	defaultCooldown: {
		delay: 1_000,
		filteredUsers: process.env.OWNER_IDS.split(","),
		limit: 5,
	},
})

//
// start the  bot
//

try {
	client.login(process.env.TOKEN)
} catch (err) {
	console.log("The bot crashed :(")
	console.error(err)

	client.destroy()
}
