// todo: also prevent command from having same name as command category

import { MessageEmbed } from "discord.js"
import { ApplyOptions } from "@sapphire/decorators"
import stringSimilarity from "string-similarity"

import type { Message } from "discord.js"
import type {
	Args,
	Command,
	CommandOptions,
	CommandStore,
} from "@sapphire/framework"

import CustomCommand from "../../custom/CustomCommand"

enum QueryType {
	empty = "empty",
	command = "command",
	category = "category",
	unknown = "unknown",
}

type CategorizeQueryReturn =
	| { queryType: QueryType.empty }
	| { queryType: QueryType.command; command: Command }
	| { queryType: QueryType.category }
	| { queryType: QueryType.unknown }

@ApplyOptions<CommandOptions>({
	aliases: ["h"],
	description:
		"Shows list of helpful information about a command or a command category.",
})
export default class HelpCommand extends CustomCommand {
	usage = `> {$} ["command"|"category"]

ex:
List categories:
> {$}

List commands in the \`util\` category:
> {$} util

Shows information about the \`ping\` command:
> {$} ping`

	//
	commands: CommandStore = this.container.client.stores.get("commands")
	// lower case names of categories
	lowerCaseCategoryNames: string[] = []
	// all command names and aliases
	allCommands: string[] = []

	async messageRun(message: Message, args: Args): Promise<void> {
		if (this.lowerCaseCategoryNames.length <= 0) {
			// can not put this in class constructor because then `this.commands.categories` will be equal to `[]`
			// can not put this in the "ready" listener either because of race conditions
			this.lowerCaseCategoryNames = this.commands.categories.map((elem) =>
				elem.toLowerCase()
			)
		}

		const query: string = await args.pick("string").catch(() => "")
		const queryCategory = this.categorizeQuery(query)

		switch (queryCategory.queryType) {
			case QueryType.empty:
				this.sendDefaultHelpMessage(message)
				break

			case QueryType.command:
				this.sendCommandHelpMessage(message, queryCategory.command)
				break

			case QueryType.category:
				this.sendCategoryHelpMessage(message, query)
				break

			default:
				this.sendCommandNotFoundMessage(message, query)
				break
		}
	}

	categorizeQuery(input: string): CategorizeQueryReturn {
		const query = input.toLowerCase()

		if (!query) return { queryType: QueryType.empty }

		if (this.lowerCaseCategoryNames.includes(query))
			return { queryType: QueryType.category }

		const command = this.commands.find(
			(command: Command, key: string) =>
				key.toLowerCase() === query ||
				command.aliases.some((elem) => elem.toLowerCase() === query)
		)
		if (command) return { queryType: QueryType.command, command }

		return { queryType: QueryType.unknown }
	}

	sendDefaultHelpMessage(message: Message): void {
		const helpEmbed = new MessageEmbed({
			title: "Help",
			description: `Use the \`${process.env.PREFIX}help <category>\` command to get more information about a category.
This command is not case sensitive.

You can read more about the bot in the [documentation](https://docs.llama.developomp.com/docs/usage/overview).

**Categories:**`,
		})

		//
		// add categories
		//

		this.commands.categories.map((categoryName) => {
			const commandsInCategory = this.commands.filter((command) =>
				command.fullCategory.includes(categoryName)
			)

			helpEmbed.addField(
				categoryName,
				`${commandsInCategory.size} commands`,
				true
			)
		})

		//
		// reply
		//

		message.channel.send({
			embeds: [helpEmbed],
		})
	}

	sendCommandHelpMessage(message: Message, command: Command): void {
		const aliases = command.aliases
			? `\`${command.aliases.join("`, `")}\``
			: "None"

		message.channel.send({
			embeds: [
				new MessageEmbed({
					title: command.name,
					description: `Aliases: ${aliases}`,
					fields: [
						{
							name: "Description",
							value: command.description || "WIP",
						},
						{
							name: "Usage",
							value:
								// replace `{$}` with <prefix><command>
								command.usage?.replace(
									/{\$}/g,
									`${process.env.PREFIX}${command.name}`
								) || "WIP",
						},
					],
				}),
			],
		})
	}

	sendCategoryHelpMessage(message: Message, query: string): void {
		//
		// find category
		//

		let selectedCategoryName = ""

		const lowerCaseCategoryName = query.toLowerCase()
		this.commands.categories.some((categoryName) => {
			if (categoryName.toLowerCase() === lowerCaseCategoryName) {
				selectedCategoryName = categoryName
				return true
			}
		})

		//
		// Find commands in category
		//

		const commandsInCategory = this.commands.filter((command) =>
			command.fullCategory.includes(selectedCategoryName)
		)

		//
		// Reply
		//

		message.channel.send({
			embeds: [
				new MessageEmbed({
					title: `${selectedCategoryName} category`,
					description: `Use the \`${process.env.PREFIX}help <command>\` command to get more information about a command.
This command is not case sensitive.`,
					fields: [
						{
							name: "commands",
							value: commandsInCategory
								.map((command) => `- \`${command.name}\`\n`)
								.join(""),
						},
					],
				}),
			],
		})
	}

	sendCommandNotFoundMessage(message: Message, query: string): void {
		if (this.allCommands.length <= 0) {
			this.allCommands = [...this.commands.keys()].concat(
				this.commands.aliases
					.map((elem) => elem.aliases)
					.reduce((prev, curr) => prev.concat(curr)) as string[]
			)
		}

		const mostLikelyGuess =
			this.allCommands[
				stringSimilarity.findBestMatch(query, this.allCommands).bestMatchIndex
			]

		message.channel.send({
			embeds: [
				new MessageEmbed({
					title: "Command not found",
					description: `Command \`${query}\` was not found. Did you mean \`${mostLikelyGuess}\`?
You can also use the \`${process.env.PREFIX}help\` command to list all available commands.`,
				}),
			],
		})
	}
}
