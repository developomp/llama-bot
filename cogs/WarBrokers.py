import wbscraper.player
import wbscraper.commons
import wbscraper.data
import cogs._util as util

import discord
from discord.ext import commands


# todo: add change/remove uid feature
class WarBrokers(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

		self.LLAMA_BOT = self.bot.get_channel_from_vars("LLAMA_BOT")
		self.ADMIN_BOT = self.bot.get_channel_from_vars("ADMIN_BOT")
		self.BOT_WORK = [self.LLAMA_BOT, self.ADMIN_BOT]

		# list of string values of WB servers (ASIA, USA, etc.)
		self.WB_GAME_SERVERS: list[str] = [i for i in wbscraper.commons.class_to_value_list(wbscraper.data.Location) if type(i) == str]

		self.help_msg = f"<#{self.bot.VARS['channels']['LLAMAS_AND_PYJAMAS_INFO']}> and <#{self.bot.VARS['channels']['ACTIVE']}> automatically updates when the contents of the database is changed."

		self.active_roster_channel = self.bot.LP_SERVER.get_channel(self.bot.VARS["channels"]["ACTIVE"])
		self.lp_info_channel = self.bot.LP_SERVER.get_channel(self.bot.VARS["channels"]["LLAMAS_AND_PYJAMAS_INFO"])

	async def update_player(self, user_id):
		"""Update LP member list message
		"""
		player = self.bot.llama_firebase.read("players", user_id)
		stat_page_url = wbscraper.URL.join(wbscraper.URL.stat_root, "players/i", player["uid"])
		player_wb = wbscraper.player.get_player(stat_page_url)

		player_description = f"User: {self.bot.LP_SERVER.get_member(user_id).mention}\n"

		try:
			player_description += "Preferred Weapon: %s\n" % player["weapon"]
		except KeyError:
			player_description += "Preferred Weapon: %s\n" % "No Data"

		player_description += "K/D: %.4s\n" % player_wb.kdr

		try:
			player_description += "Time Zone: %s\n" % player["time"]
		except KeyError:
			player_description += "Time Zone: %s\n" % "No Data"

		player_description += f"Stats page: {stat_page_url}\n"

		embed = discord.Embed(
			title=player_wb.nick,
			description=player_description
		)

		# update if stat message is in the database, add to the database otherwise.
		try:  # try assuming that the stat message exists already
			stat_msg = await self.lp_info_channel.fetch_message(player["message_id"])
			await stat_msg.edit(embed=embed)
		except (KeyError, discord.NotFound):
			info_message = await self.lp_info_channel.send(embed=embed)
			self.bot.llama_firebase.write("players", user_id, "message_id", info_message.id)

	async def update_active(self):
		"""Update active roster message
		"""
		players = self.bot.llama_firebase.read_collection("players")

		description = ""
		for game_server in self.WB_GAME_SERVERS:
			description += f"{game_server}:\n"
			region_is_empty = True
			for player in players:
				try:
					if game_server in players[player]["server"]:
						description += f"<@{player}>\n"
						region_is_empty = False
				except KeyError:
					pass
			if region_is_empty:
				description += "-- Empty --\n"
			description += "\n"

		emoji = discord.utils.get(self.bot.LP_SERVER.emojis, name="blobsalute")
		embed = discord.Embed(
			title=f"{emoji} LLAMA’S PYJAMAS ACTIVE ROSTER {emoji}",
			description=description
		)

		# make a new message if the active roster doesn't exist, edit otherwise.
		try:  # assume that the active roster message exists
			active_msg = await self.active_roster_channel.fetch_message(int(self.bot.VARS["messages"]["ACTIVE"]))
			await active_msg.edit(embed=embed)
		except (KeyError, discord.NotFound):
			active_msg = await self.active_roster_channel.send(embed=embed)
			self.bot.llama_firebase.write("vars", "messages", "ACTIVE", active_msg.id)

	@commands.command(
		help="Sets/updates data in the database.",
		usage="""> {prefix}{command} <field> <data>
field: uid | weapon | time | server
data: anything that comes after the field

> {prefix}{command} uid <uid>
**Must run this before running other set commands**
Correlates WB uid with your discord ID. Must be a valid WB uid.
Only correlates with one uid. Alt accounts are not supported yet.
ex:
> {prefix}{command} uid 5d2ead35d142affb05757778

> {prefix}{command} weapon <weapon>
Sets your preferred weapon. No input specifications.
ex:
> {prefix}{command} weapon Sniper & AR

> {prefix}{command} time <time>
Sets your time zone. No input specifications.
ex:
> {prefix}{command} time UTC+8

> {prefix}{command} server <server1> <server2> ...
Sets the servers you usually play on. Use `{prefix}set server help` to get more info.
ex:
> {prefix}{command} server ASIA USA
"""
	)
	async def set(self, ctx, field: str, *args):
		# check if user is authorized to use this command
		if not util.lists_has_intersection(self.bot.LLAMA_PERMS, ctx.message.author.roles):
			await ctx.send(embed=discord.Embed(title="Nope!", description="You need to join the LPWB squad to use this command."))
			return

		# Deny usage if the bot is not run in the LPWB bot channel to prevent information leak.
		if ctx.message.channel not in self.BOT_WORK:
			await ctx.send(embed=discord.Embed(description=f"Bruh what do you think {self.LLAMA_BOT.mention} is for?"))
			return

		field = field.lower()
		available_fields = ["uid", "weapon", "time", "server"]
		if field not in available_fields:
			raise discord.ext.commands.errors.BadArgument(
				"first command argument should be one of:\n"+"\n- ".join(available_fields)
			)

		user_exists_in_firestore = self.bot.llama_firebase.exists("players", ctx.message.author.id)

		if field == "uid":
			original_content = "checking uid validity..."
			msg = await ctx.send(embed=discord.Embed(description=original_content))
			try:
				wbscraper.player.get_player(args[0])  # inefficient but effective
			except Exception:
				err_msg = f"{original_content}\nuid not valid. Aborting."
				await msg.edit(embed=discord.Embed(description=err_msg))
				raise discord.ext.commands.errors.BadArgument(err_msg)

			if user_exists_in_firestore:
				original_content += f"\nuid is valid. Updating uid..."
				complete_msg = "Updated uid!"
			else:
				original_content += f"\nuid is valid. Adding user to database..."
				complete_msg = "New player registered!"

			await msg.edit(embed=discord.Embed(description=original_content))
			self.bot.llama_firebase.create("players", ctx.message.author.id, "uid", args[0])
			await msg.edit(embed=discord.Embed(description=f"{original_content}\n{complete_msg}"))
			return

		if user_exists_in_firestore:
			updated_active = False
			updated_player_list = False

			if field in ["weapon", "time"]:
				self.bot.llama_firebase.write("players", ctx.message.author.id, field, " ".join(args))
				await self.update_player(ctx.message.author.id)
				updated_player_list = True
			elif field == "server":
				if all(i in self.WB_GAME_SERVERS for i in args):  # if all the inputs is a valid server
					self.bot.llama_firebase.write("players", ctx.message.author.id, "server", ",".join(list(dict.fromkeys(args))))  # Not doing join(args) to remove duplicate inputs
					await self.update_active()
					updated_active = True
				else:
					err_message = f"""
1 - List of available servers: {', '.join("`{0}`".format(w) for w in self.WB_GAME_SERVERS)} (case sensitive)
2 - servers should be separated with spaces (not commas)
3 - you can choose multiple servers

ex: `-set server ASIA USA`"""
					await ctx.send(embed=discord.Embed(description=err_message))
					raise discord.ext.commands.errors.BadArgument(err_message)

			description = "Updated %s!"
			if updated_active and not updated_player_list:
				description = description % f"<#{self.bot.VARS['channels']['ACTIVE']}>"
			elif updated_player_list and not updated_active:
				description = description % f"<#{self.bot.VARS['channels']['LLAMAS_AND_PYJAMAS_INFO']}>"
			elif updated_active and updated_player_list:
				description = description % f"<#{self.bot.VARS['channels']['ACTIVE']}> and <#{self.bot.VARS['channels']['LLAMAS_AND_PYJAMAS_INFO']}>"

			await ctx.send(embed=discord.Embed(description=description))
		else:
			await ctx.send(embed=discord.Embed(description=f"You'll have to register first. Type `{self.bot.command_prefix}help set` to get more info"))

	@commands.command(
		help="Removes data from the database.",
		usage="""> {prefix}{command} *<data to remove>
data to remove: weapon, time, server
Removing yourself from active roster and members list is not available yet.

ex:
Removes time and weapon data from the database
> {prefix}{commands} time weapon
"""
	)
	async def rm(self, ctx, *fields):
		# checks if the user is authorized to use this command
		if not util.lists_has_intersection(self.bot.LLAMA_PERMS, ctx.message.author.roles):
			await ctx.send(embed=discord.Embed(
				description=f"Ew! non WB squad member peasant! *spits at {ctx.message.author.mention}*"
			))
			return

		# check if the command is run in the right channels
		if ctx.message.channel not in self.BOT_WORK:
			await ctx.send(embed=discord.Embed(description=f"Do it in {self.LLAMA_BOT.mention} dumdum."))
			return

		if not self.bot.llama_firebase.exists("players", ctx.message.author.id):
			await ctx.send(embed=discord.Embed(
				title="User not found in the database",
				description="You didn't even register. There's nothing to remove."
			))
			return

		fields = [str(field).lower() for field in fields]
		if util.lists_has_intersection(fields, ["weapon", "time", "server"]):
			fields_that_does_not_exist = []
			for field in fields:
				try:
					self.bot.llama_firebase.read("players", ctx.message.author.id)[field]
				except KeyError:
					fields_that_does_not_exist.append(field)

			if fields_that_does_not_exist:
				description = f"field %s is not set or already deleted"
				if len(fields_that_does_not_exist) > 1:
					description = f"fields %s are not set or already deleted"
				await ctx.send(embed=discord.Embed(description=description % "/".join(fields_that_does_not_exist)))

			for field in fields:
				self.bot.llama_firebase.delete("players", ctx.message.author.id, field)

			fields_removed = list(set(fields)-set(fields_that_does_not_exist))
			if fields_removed:
				description = f"field %s removed from `{ctx.message.author.name}`"
				if len(fields_removed) > 1:
					description = f"fields %s removed from `{ctx.message.author.name}`"
				await ctx.send(embed=discord.Embed(description=description % "/".join(fields_removed)))


def setup(bot):
	bot.add_cog(WarBrokers(bot))
