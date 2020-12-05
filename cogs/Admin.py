import json
from io import StringIO

import discord
from discord.ext import commands


def must_be_admin():
	"""
		Discord bot command decorator.
		Put it under @discord.ext.commands.command()
	"""

	async def predicate(ctx: discord.ext.commands.Context):
		if ctx.message.author.guild_permissions.administrator:
			return True
		await ctx.send(embed=discord.Embed(description=f"You need to be a server administrator to issue the command. Aborting."))
		return False

	return commands.check(predicate)


class Admin(commands.Cog):
	# todo: refresh bot

	def __init__(self, bot):
		self.bot = bot

	@commands.command(
		aliases=["db", ],
		help="Read/write from/to database. Incomplete",
		usage="""> {prefix}{command} <operation> <scope> <data>
operation: read, r | write, w
scope: firestore database path | all, a (all is only available for read operation)
data: data to be overwritten in write command. Only available in write operation.
ex:
> {prefix}{command} read all"""
	)
	@must_be_admin()
	async def database(self, ctx, operation: str, scope: str, data: str = None):
		available_channel_ids = [self.bot.VARS["channels"]["ADMIN_BOT"], ]
		if ctx.message.channel.id not in available_channel_ids:  # todo: make it expandable
			ctx.send(embed=discord.Embed(title="Oops", description=f"Admin commands can only be executed in: {', '.join([f'<#{channel_id}>' for channel_id in available_channel_ids])}>"))
			return

		if operation in ["read", "r"]:
			if scope in ["all", "a"]:
				await ctx.send(
					file=discord.File(
						fp=StringIO((json.dumps(self.bot.llama_firebase.read_all(), indent=4))),
						filename="discord_warbrokers_llama_firestore_all.json"
					)
				)
		elif operation in ["write", "w"]:
			pass


def setup(bot):
	bot.add_cog(Admin(bot))
