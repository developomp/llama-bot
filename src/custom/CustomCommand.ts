import { Command } from "@sapphire/framework"

import type { PieceContext } from "@sapphire/framework"

export default abstract class CustomCommand extends Command {
	public constructor(context: PieceContext, options?: Command.Options) {
		super(context, {
			...options,

			// default preconditions
			preconditions: ["NoDM", ...(options?.preconditions || [])],
		})
	}
}
