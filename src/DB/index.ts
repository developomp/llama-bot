/**
 * @file Firestore Database interface for the bot.
 *
 * More information about firestore can be found here: https://firebase.google.com/docs/firestore
 * Though there are no plans to move away from firebase,
 * all firebase interactions are contained in this file so it's easier to move to other platform.
 *
 * Database structure:
 * bot/                      // Discord Bot related data
 *   settings/               // Discord bot settings
 * servers/                  // Server-specific data
 *   SERVER_ID/              // discord server ID (snowflake)
 *     settings/             // server-specific settings
 *       name: string        // server name
 *     vars/                 // server-specific variables
 * users/                    // user data
 *   USER_ID/                // discord user ID (snowflake)
 *     avatar: string        // discord avatar ID
 *     discriminator: string // a 4 digit numerical discord user discriminator
 *     id: string            // discord user ID (snowflake)
 *     username: string      // discord user name
 */

// todo: create and populate if it doesn't exist already

import admin from "firebase-admin"
import serviceAccountKey from "../secret/firebase-adminsdk.json"

import type { Snowflake } from "discord-api-types"
import type { Settings, Servers, ServerData } from "../types/bot"

admin.initializeApp({
	credential: admin.credential.cert(serviceAccountKey as admin.ServiceAccount),
})

const firestoreDB = admin.firestore()

const botCollection = firestoreDB.collection("bot")
const serversCollection = firestoreDB.collection("servers")

const settingsDoc = botCollection.doc("settings")

/**
 * Global bot settings. Fetched by calling the {@link fetchSettings} function.
 */
export let settings: Settings = {}

/**
 * Server-specific data.
 * Fetched by calling the {@link fetchServerData} function.
 */
export const servers: Servers = {}

/**
 * Fetch settings from the database.
 */
export async function fetchSettings(): Promise<void> {
	await settingsDoc.get().then((doc) => {
		settings = doc.data() as Settings
	})
}

/**
 * Fetch server-specific data from the database.
 */
export async function fetchServerData(
	serverSnowflake: Snowflake
): Promise<void> {
	await serversCollection
		.doc(serverSnowflake)
		.get()
		.then((doc) => {
			servers[serverSnowflake] = doc.data() as unknown as ServerData
		})
}

//
// initialize
//

// todo: make sure settings is fetched before anyone runs a command
fetchSettings()

export default {
	settings,
	servers,
	fetchSettings,
	fetchServerData,
}
