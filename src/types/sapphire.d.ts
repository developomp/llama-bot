import "@sapphire/framework"

declare module "@sapphire/framework" {
	abstract class Command {
		usage?: string
	}

	interface Preconditions {
		AdminsOnly: never
		OwnersOnly: never
		NoDM: never
	}
}
