export type Snowflake = string
// structure: "<snowflake>/<snowflake>"
export type MessageSelector = string

export interface Settings {
	// emoji names
	clear_emojis?: string[]
	// quotes to be used in the `llama` command
	quotes?: string[]
}

export interface ServerData {
	settings: {
		// todo: enable/disable commands by default
		// todo: enabled/disabled commands/categories
	}

	vars: {
		channels: { [key: string]: Snowflake }
		messages: { [key: string]: MessageSelector }
		roles: { [key: string]: Snowflake }
	}
}

export interface Servers {
	[key: Snowflake]: ServerData
}
