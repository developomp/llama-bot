import wbscraper.player

import discord
from discord.ext import commands


# todo: add change/remove uid feature
class WarBrokers(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

		self.LLAMA_BOT = self.bot.get_channel_from_vars("LLAMA_BOT")
		self.ADMIN_BOT = self.bot.get_channel_from_vars("ADMIN_BOT")
		self.BOT_WORK = [self.LLAMA_BOT, self.ADMIN_BOT]

		self.help_msg = "<#475048014604402708> and <#693401827710074931> automatically updates when the contents of the database is changed."

	async def update_player(self, user_id):
		player = self.bot.llama_firebase.read("players", user_id)

		stat_page = wbscraper.URL.join(wbscraper.URL.stat_root, "players/i", player["uid"])
		player_wb = wbscraper.player.get_player(stat_page)

		user = self.bot.LP_SERVER.get_member(user_id)
		role = "Error"
		if self.bot.PYJAMAS in user.roles:
			role = "Pyjama"
		if self.bot.THE_LLAMA in user.roles:
			role = "The Llama"

		player_description = f"Discord: {user.mention}\n"
		player_description += f"Role: {role}\n"

		try:
			player_description += "Preferred Weapon: %s\n" % player["weapon"]
		except KeyError:
			player_description += "Preferred Weapon: %s\n" % "No Data"

		player_description += "K/D: %.4s\n" % player_wb.kdr

		try:
			player_description += "Time Zone: %s\n" % player["time"]
		except KeyError:
			player_description += "Time Zone: %s\n" % "No Data"

		player_description += f"Stats page: {stat_page}\n"

		embed = discord.Embed(
			title=player_wb.nick,
			description=player_description
		)

		# update if stat message is in the database, add to the database otherwise.
		lp_info_channel = self.bot.get_channel_from_vars("LLAMAS_AND_PYJAMAS_INFO")
		try:
			stat_msg = await lp_info_channel.fetch_message(player["message_id"])
			await stat_msg.edit(embed=embed)
		except (KeyError, discord.NotFound):
			info_message = await lp_info_channel.send(embed=embed)
			self.bot.llama_firebase.write("players", user_id, "message_id", info_message.id)

	async def update_active(self):
		players = self.bot.llama_firebase.read_collection("players")

		description = ""
		for game_server in self.bot.WB_GAME_SERVERS:
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

		active_roster_channel = self.bot.get_channel_from_vars("ACTIVE")
		try:
			active_msg = await active_roster_channel.fetch_message(int(self.bot.VARS["messages"]["ACTIVE"]))
			await active_msg.edit(embed=embed)
		except (KeyError, discord.NotFound):
			active_msg = await active_roster_channel.send(embed=embed)
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
		# todo: invalid field or args
		# check if user has the right role
		if not self.bot.lists_has_intersection(self.bot.LLAMA_PERMS, ctx.message.author.roles):
			await ctx.send(embed=discord.Embed(title="Nope!", description="LMAO You're not even in LP! Access denied!"))
			return

		# if the message is sent in the right channel
		if ctx.message.channel not in self.BOT_WORK:
			await ctx.send(embed=discord.Embed(description=f"Bruh what do you think {self.LLAMA_BOT.mention} is for?"))
			return

		if not (field or args):
			raise discord.ext.commands.errors.MissingRequiredArgument

		if field not in ["uid", "weapon", "time", "server"]:
			raise discord.ext.commands.errors.BadArgument

		field = field.lower()
		user_exists_in_firestore = self.bot.llama_firebase.exists("players", ctx.message.author.id)

		# -set uid <uid>
		if field == "uid":
			if user_exists_in_firestore:
				# todo: do you want to update it?
				await ctx.send(embed=discord.Embed(description=f"You're already in the database. ask {', '.join([f'<@{fixer_id}>' for fixer_id in self.bot.fixer_ids])} to change it."))
				return

			original_content = "checking uid validity..."
			msg = await ctx.send(embed=discord.Embed(description=original_content))
			try:
				wbscraper.player.get_player(args[0])  # inefficient but effective
			except Exception:
				await msg.edit(embed=discord.Embed(description=f"{original_content}\nuid not valid. Aborting."))
				raise discord.ext.commands.errors.BadArgument

			original_content = f"{original_content}\nuid is valid. Adding user to database..."
			await msg.edit(embed=discord.Embed(description=original_content))
			self.bot.llama_firebase.create("players", ctx.message.author.id, "uid", args[0])
			await msg.edit(embed=discord.Embed(description=f"{original_content}\nnew player registered!"))
			return

		if user_exists_in_firestore:
			if field in ["weapon", "time"]:
				self.bot.llama_firebase.write("players", ctx.message.author.id, field, " ".join(args))
				await self.bot.update_player(ctx.message.author.id)
			elif field == "server":
				if all(i in self.bot.WB_GAME_SERVERS for i in args):
					self.bot.llama_firebase.write("players", ctx.message.author.id, "server", ",".join(list(dict.fromkeys(args))))  # remove duplicate
					await self.bot.update_active()
				else:
					await ctx.send(embed=discord.Embed(description=f"""
1 - List of available servers: {', '.join("`{0}`".format(w) for w in self.bot.WB_GAME_SERVERS)} (case sensitive)
2 - servers should be separated with spaces (not commas)
3 - you can choose multiple servers

ex: `-set server ASIA USA`"""))
					return

			await ctx.send(
				embed=discord.Embed(
					description=f"updated <#{self.bot.VARS['channels']['ACTIVE']}> and/or <#{self.bot.VARS['channels']['LLAMAS_AND_PYJAMAS_INFO']}>!"
				)
			)
		else:
			await ctx.send(embed=discord.Embed(description=f"You'll have to register first. Try using `{self.bot.command_prefix}help set`"))

	@commands.command(
		help="Removes data from the database.",
		usage="""> {prefix}{command} *<data to remove>
data to remove: weapon | time | server

ex:
Removes time and weapon data from the database
> {prefix}{commands} time weapon
"""
	)
	async def rm(self, ctx, a1):
		a1 = str(a1).lower()
		if not self.bot.lists_has_intersection(self.bot.LLAMA_PERMS, ctx.message.author.roles):
			await ctx.send(embed=discord.Embed(description=f"Ew! non LP peasant! *spits at {ctx.message.author.mention}*"))
			return

		if ctx.message.channel not in self.BOT_WORK:
			await ctx.send(embed=discord.Embed(description=f"You're not in the right channel. Do it in {self.LLAMA_BOT.mention}"))
			return

		if not self.bot.llama_firebase.exists("players", ctx.message.author.id):
			await ctx.send(embed=discord.Embed(description="You're not even in my database. At least register."))
			await ctx.send(embed=discord.Embed(description=self.bot.HELP_STAT))
			return

		if a1 in ["weapon", "time", "server"]:
			try:
				self.bot.llama_firebase.read("players", ctx.message.author.id)[a1]
			except KeyError:
				await ctx.send(embed=discord.Embed(description=f"field {a1} is not set or already deleted"))
				return

			self.bot.llama_firebase.delete("players", ctx.message.author.id, a1)
			await ctx.send(embed=discord.Embed(description=f"field `{a1}` removed from `{ctx.message.author.name}`"))
		else:
			await ctx.send(embed=discord.Embed(description=f"field {a1} does not exist"))
			return


def setup(bot):
	bot.add_cog(WarBrokers(bot))
