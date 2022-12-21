declare namespace NodeJS {
	interface ProcessEnv {
		[key: string]: string | undefined

		// .env values
		TOKEN: string
		TESTING: string
		PREFIX_PROD: string
		PREFIX_DEV: string
		OWNER_IDS: string // ID1,ID2,ID3,...

		// default prefix currently being used
		PREFIX: string
	}
}
