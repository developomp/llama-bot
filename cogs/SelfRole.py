import cogs._util as util
import re

import discord
from discord.ext import commands


class SelfRole(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

		# {"CHANNEL_ID/MESSAGE_ID": ["EMOJI_ID_OR_NAME;ROLE_ID", ...], ...}
		self.binds: dict = self.bot.llama_firebase.read("vars", "selfrole_messages")

		self.help_msg = ""
		self.main_help_fields = [
			[
				"Self role",
				"Only admins can create self role message"
			],
		]

	# self role add
	@commands.Cog.listener()
	async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
		if payload.member.id == self.bot.user.id:
			return

		try:
			for emoji_role in self.binds[f"{payload.channel_id}/{payload.message_id}"]:
				emoji_id_or_name, role_id = emoji_role.split(";")
				assert emoji_id_or_name and role_id
				if emoji_id_or_name in [payload.emoji.name, str(payload.emoji.id)]:
					await payload.member.add_roles(self.bot.LP_SERVER.get_role(int(role_id)))
		except KeyError:
			pass  # no reaction role bind found

	# self role remove
	@commands.Cog.listener()
	async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
		try:
			for emoji_role in self.binds[f"{payload.channel_id}/{payload.message_id}"]:
				emoji_id_or_name, role_id = emoji_role.split(";")
				assert emoji_id_or_name and role_id
				if emoji_id_or_name in [payload.emoji.name, str(payload.emoji.id)]:
					await (await self.bot.LP_SERVER.fetch_member(payload.user_id)).remove_roles(self.bot.LP_SERVER.get_role(int(role_id)))
		except KeyError:
			pass  # no reaction role bind found

	@commands.command(
		aliases=["rr", ],
		help="Add reactions for self role to a message.",
		usage="""- `MESSAGE_PATH` can be `CHANNEL_ID`/`MESSAGE_ID` or a message jump url.

Add reaction role bind to `MESSAGE` in `CHANNEL` where reacting with `EMOJI_1` gives `ROLE_1` and `EMOJI_2` gives `ROLE_2`, etc.
> {prefix}{command} <add or a> `MESSAGE_PATH` `EMOJI_1` `ROLE_1` `EMOJI_2` `ROLE_2`

Remove (`EMOJI_1` -> `ROLE_1`) and (`EMOJI_2` -> `ROLE_2`) bind from reaction role message.
> {prefix}{command} <remove or r> `MESSAGE_PATH` `EMOJI_1` `ROLE_1` `EMOJI_2` `ROLE_2`"""
	)
	@util.must_be_admin()
	async def reactrole(self, ctx, mode, channel_id_or_message_path, *emojis_and_or_roles):
		# parse arguments
		_mode = None  # 0: create, 1: edit
		if mode in ["add", "a"]:
			_mode = 0
		elif mode in ["remove", "r"]:
			_mode = 1
		else:
			raise discord.ext.commands.errors.BadArgument

		# parse url/path
		flag = 0
		try:
			# remove trailing slash(es) if it's a url
			while True:
				if channel_id_or_message_path[-1] == "/":
					channel_id_or_message_path = channel_id_or_message_path[:-1]
				else:
					break
			# get "CHANNEL/MESSAGE" part of the input
			message_path = re.findall(r"\d+/\d+", channel_id_or_message_path[::-1])[0][::-1]
			channel_id, message_id = message_path.split("/")
			flag = 1
			channel: discord.TextChannel = await self.bot.fetch_channel(channel_id)
			flag = 2
			message: discord.Message = await channel.fetch_message(message_id)
		except Exception:
			title = "parsing message path"
			if flag == 1:
				title = "fetching channel"
			if flag == 2:
				title = "fetching message"

			await ctx.send(embed=discord.Embed(
				title=f"Error while {title}!",
				description="Are you sure the inputs are correct?"
			))
			raise discord.ext.commands.errors.ArgumentParsingError

		# if the pair doesn't match (if it's not odd number)
		if len(emojis_and_or_roles) % 2:
			raise discord.ext.commands.errors.BadArgument

		# /parse arguments

		async def group_emojis_and_roles():
			# group list by groups of 2 (https://stackoverflow.com/a/1751478/12979111)
			try:
				emojis_and_roles_parsed = []
				emoji_and_role_ids = []
				for emoji_raw, role_raw in [emojis_and_or_roles[i:i + 2] for i in range(0, len(emojis_and_or_roles), 2)]:
					emoji_id = emoji_raw if "<" not in emoji_raw else int(re.findall(r"\d+", emoji_raw)[0])
					role_id = int(re.findall(r"\d+", role_raw)[0])

					emoji = emoji_raw if emoji_id == emoji_raw else self.bot.get_emoji(emoji_id)
					role = self.bot.LP_SERVER.get_role(role_id)
					# todo: role higher than bot's
					assert emoji, "emoji"
					assert role, "role"

					emoji_and_role_ids.append([emoji_id, role_id])
					emojis_and_roles_parsed.append([emoji, role])
			except AssertionError as err:
				await ctx.send(embed=discord.Embed(
					title=f"Error while parsing {err}!",
					description="""{one} {two} might not a valid {three} that can be used by the bot.
Are you sure it's not a {three} from other server?""".format(one=str(err).title(), two=emoji_raw if err == "emoji" else role_raw, three=err)
				))
				raise discord.ext.commands.errors.BadArgument
			return emojis_and_roles_parsed, emoji_and_role_ids

		if _mode == 0:  # add bind
			if message_path not in self.binds.keys():
				self.binds[message_path] = []

			emojis_and_roles_parsed, emoji_and_role_ids = await group_emojis_and_roles()

			# add what's not already in the binds
			self.binds[message_path] += list({f"{emoji};{role}" for emoji, role in emoji_and_role_ids} - set(self.binds[message_path]))
			# push to firebase
			self.bot.llama_firebase.write("vars", "selfrole_messages", message_path, self.binds[message_path])
			# add reaction
			for emoji, _ in emojis_and_roles_parsed:
				await message.add_reaction(emoji)
		elif _mode == 1:  # remove bind
			if message_path not in self.binds.keys():
				await ctx.send(embed=discord.Embed(
					title="No bind found on message.",
					description=f"There's no enabled reaction role emoji found on that [message]({message.jump_url})"
				))

			# todo: confirm (remove all reaction or not?)
			emojis_and_roles_parsed, emoji_and_role_ids = await group_emojis_and_roles()

			# remove binds
			for i in [f"{emoji};{role}" for emoji, role in emoji_and_role_ids]:
				self.binds[message_path].remove(i)

			# remove list if empty
			if not self.binds[message_path]:
				self.binds.pop(message_path)
				self.bot.llama_firebase.delete("vars", "selfrole_messages", message_path)
			else:
				self.bot.llama_firebase.write("vars", "selfrole_messages", message_path, self.binds[message_path], False)

			for emoji, _ in emojis_and_roles_parsed:
				await message.remove_reaction(emoji, self.bot.user)


def setup(bot):
	bot.add_cog(SelfRole(bot))
