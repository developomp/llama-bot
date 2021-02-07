import wbscraper.commons
import wbscraper.data

from llama_firebase import LlamaFirebase

import discord
from discord.ext import commands

from os import listdir
from os.path import isfile, join, splitext
from time import time
import traceback
import json


class Llama(commands.Bot):
	# todo: less firestore calls (cache locally?)

	def __init__(self, firebase_cred_path: str, prefix: str = "-"):
		super().__init__(
			help_command=None,
			command_prefix=prefix,
			case_insensitive=False
		)

		self.llama_firebase: LlamaFirebase = LlamaFirebase(firebase_cred_path)

		self.VARS = self.llama_firebase.read_collection("vars")
		self.WB_GAME_SERVERS = [i for i in wbscraper.commons.class_to_value_list(wbscraper.data.Location) if type(i) == str]

		self.owner_ids: set = {501277805540147220, 396333737148678165}  # Can run owner only commands
		self.fixer_ids: set = {501277805540147220}  # Pinged/DMed when there's an issue with the bot

	# ----- [ DISCORD.PY STUFF ] -----

	async def on_ready(self):
		self.LP_SERVER: discord.Guild = next((guild for guild in self.guilds if guild.id == 457373827073048604), None)
		if not self.LP_SERVER:
			print("----------[ The bot is not in LP server! ]----------")
			exit(-6969)

		# todo: don't load roles until when necessary
		self.HIGHEST_ORDER = self.get_role_from_vars("HIGHEST_ORDER")
		self.PYJAMAS = self.get_role_from_vars("PYJAMAS")
		self.THE_LLAMA = self.get_role_from_vars("THE_LLAMA")
		self.SILK_PERMISSION = self.get_role_from_vars("SILK_PERMISSION")
		self.HOMIES = self.get_role_from_vars("HOMIES")

		self.LLAMA_PERMS = [getattr(self, i) for i in self.VARS["settings"]["LLAMA_PERM"]]
		self.PIN_PERMISSIONS = [getattr(self, i) for i in self.VARS["settings"]["PIN_PERM"]]

		# load cogs at the very last moment as some of them require data from the database
		for cog in [f"cogs.{splitext(f)[0]}" for f in listdir("cogs") if isfile(join("cogs", f)) and not f[0] == "_"]:
			print(f"loading cog: {cog}")
			self.load_extension(cog)

		self.start_time = time()
		print(f"{self.user} is up and ready!")

	async def on_command_error(self, ctx: discord.ext.commands.Context, error: discord.ext.commands.CommandError):
		"""Gets executed when the bot encounters an error.
		"""
		if isinstance(error, discord.ext.commands.errors.NSFWChannelRequired):
			await ctx.send(embed=discord.Embed(title=":lock: This command is not available in non NSFW channel"))

		if isinstance(error, discord.ext.commands.errors.BotMissingPermissions):
			missing_perms_list = "".join([f"- {i}\n" for i in error.missing_perms])
			await ctx.send(embed=discord.Embed(title="Aw man", description=f"The bot require following permissions to run command `{ctx.message.content}`.\n{missing_perms_list}"))

		if isinstance(error, discord.ext.commands.errors.NotOwner):
			await ctx.send(embed=discord.Embed(title="Oops!", description=f"You have to be a bot owner to run command `{ctx.message.content}`."))

		if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
			await ctx.send(embed=discord.Embed(title="Error!", description=f"Command `{ctx.message.content}` is missing required argument(s).\nConsider using `{self.command_prefix}help {ctx.command}` to learn how to use it."))

		if isinstance(error, (discord.ext.commands.errors.BadArgument, discord.ext.commands.ArgumentParsingError)):
			await ctx.send(embed=discord.Embed(title="Hol up!", description=f"command `{ctx.message.content}` is given invalid argument(s).\nConsider using `{self.command_prefix}help {ctx.command}` to learn how to use it."))

		if isinstance(error, discord.ext.commands.errors.CommandInvokeError):
			await ctx.send(embed=discord.Embed(title="Error!", description="Command Failed to complete. This is most likely a problem on the bot's side."))

		if isinstance(error, discord.ext.commands.errors.MemberNotFound):
			await ctx.send(embed=discord.Embed(title="Hmm...", description=f"Member {error.argument} was not found in this server."))

		print("")
		print("="*30)
		print(type(error))
		print("Cog:", ctx.cog)
		print("Author:", ctx.author, ctx.author.id)
		print("Content:", ctx.message.content)
		print("Channel:", ctx.message.channel, ctx.message.channel.id)
		print("URL:", ctx.message.jump_url)
		print("")
		traceback.print_exception(type(error), error, error.__traceback__)
		print("="*30)
		print("")

	# ----- [ BOT METHODS ] -----

	def get_role_from_vars(self, name):
		return discord.utils.get(self.LP_SERVER.roles, id=int(self.VARS["roles"][name]))

	def get_channel_from_vars(self, name):
		return self.LP_SERVER.get_channel(int(self.VARS["channels"][name]))


def main():
	bot_prefix = "-"

	if not isfile("config.json"):
		print("create config.json first!")
		exit(-9999)

	with open("config.json", "rt") as f:
		config = json.loads(f.read())

		# I know it's a hacky solution lmao
		if config["beta"]:
			bot_prefix = f"b{bot_prefix}"

	# not using os.environ because it's feels like a hacky solution enough for my liking
	# Allows comments and trailing newline for TOKEN file
	with open(config["token"], "rt") as f:
		while True:
			token = f.readline().strip()
			if not token.startswith("#"):
				break

	llama_bot = Llama(
		config["firestore"],
		bot_prefix
	)

	llama_bot.run(token)


if __name__ == "__main__":
	main()
