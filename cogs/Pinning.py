# Original code from: https://github.com/aurzen/pinbot
import re
import traceback

import discord
from discord.ext import commands


class Pinning(commands.Cog):
	# todo: check if emoji is usable by bot
	# todo: add/remove pin reaction emoji
	# todo: check message2embed

	def __init__(self, bot):
		self.bot = bot

		self.pin_emojis: set[discord.PartialEmoji] = set()
		for emoji_raw in self.bot.VARS["pinbot"]["pin_reaction"]:  # either unicode or int (emoji name or emoji id)
			emoji_raw: str = emoji_raw.strip()
			try:  # test if data is int
				emoji_id: int = int(emoji_raw)
				emoji: discord.Emoji = self.bot.get_emoji(emoji_id)
				if not emoji:
					print(f"Cannot convert {emoji_raw} to discord Emoji.")
					return
				self.pin_emojis.add(discord.PartialEmoji(name=emoji.name, animated=emoji.animated, id=emoji_id))
			except ValueError:  # if data is not int
				self.pin_emojis.add(discord.PartialEmoji(name=emoji_raw))

		self.recently_pinned_ids: set[discord.Message] = set()  # Messages in this list can't be pinned.
		self.channel_maps: set = self.channel_maps_read()  # Collection of source and destination channels where the pins will be mapped.
		self.pinnable_channels: set = self.pinnable_channels_read()  # Channels with reaction pinning enabled.

		self.help_msg = ""
		self.main_help_fields = [
			[
				"Pinning",
				f"""Add one of these reactions to pin a message: {' | '.join(map(str, self.pin_emojis))}
You'll need at least one of the following roles to use this feature: {' | '.join([role.mention for role in self.bot.PIN_PERMISSIONS])}"""
			],
		]

	def channel_maps_read(self) -> set[tuple]:
		res: set[tuple] = set()
		self.bot.VARS["pinbot"] = self.bot.llama_firebase.read("vars", "pinbot")
		for map_str in self.bot.VARS["pinbot"]["maps"]:
			try:
				map_ids = map_str.split(",")
				assert len(map_ids) == 2
				source_channel_id, destination_channel_id = map(int, map_ids)
				source_channel = self.bot.get_channel(source_channel_id)
				destination_channel = self.bot.get_channel(destination_channel_id)
				assert source_channel
				assert destination_channel
				res.add((source_channel, destination_channel))
			except (AssertionError, ValueError):
				traceback.print_exc()

		return res

	def channel_maps_write(self):
		self.bot.llama_firebase.write("vars", "pinbot", "maps", [u"%s,%s" % (i[0].id, i[1].id) for i in self.channel_maps])

	def pinnable_channels_read(self) -> set[discord.abc.Messageable]:
		res: set[discord.abc.Messageable] = set()
		self.bot.VARS["pinbot"] = self.bot.llama_firebase.read("vars", "pinbot")
		for channel_id in self.bot.VARS["pinbot"]["allowed_channels"]:
			try:
				channel = self.bot.get_channel(int(channel_id))
				assert channel
				res.add(channel)
			except (AssertionError, ValueError):
				traceback.print_exc()

		return res

	def pinnable_channels_write(self):
		self.bot.llama_firebase.write("vars", "pinbot", "allowed_channels", [u"%s" % i.id for i in self.pinnable_channels])

	async def message2embed(self, ctx: discord.ext.commands.Context, message: discord.Message):
		# todo: videos/images
		# todo: check if suppress_embeds flag is set

		has_video = False
		new_embed = discord.Embed()
		new_embed.description = message.content[:1900] + ("..." if len(message.content) > 1900 else "")
		new_embed.add_field(name="pin info", value=f"channel: {message.channel.mention}\n[Jump to message]({message.jump_url})", inline=False)

		if message.embeds:
			original_embed = message.embeds[0]
			if not original_embed.video:
				new_embed.title = original_embed.title
				new_embed.colour = original_embed.colour
				new_embed.url = original_embed.url

				if original_embed.description:
					new_embed.add_field(name="content", value=original_embed.description, inline=False)
				for field in original_embed.fields:
					new_embed.add_field(name=field.name, value=field.value, inline=field.inline)
				if original_embed.image:
					new_embed.set_image(url=original_embed.image.url)
				if original_embed.thumbnail:
					new_embed.set_thumbnail(url=original_embed.thumbnail.url)
				if original_embed.footer:
					new_embed.set_footer(text=original_embed.footer.text, icon_url=original_embed.footer.icon_url)
			else:
				has_video = True

		files = [await attachment.to_file(spoiler=attachment.is_spoiler()) for attachment in message.attachments]
		if has_video:
			await ctx.send("\n".join(self.bot.url_from_str(message.content)), files=files)
		else:
			await ctx.send(embed=new_embed, files=files)

	# reaction pinning
	@commands.Cog.listener()
	async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
		# todo: cannot pin same message in 10s
		if payload.emoji not in self.pin_emojis:
			return

		channel: discord.abc.Messageable = self.bot.get_channel(payload.channel_id)
		message: discord.Message = await channel.fetch_message(payload.message_id)
		assert channel
		assert message

		if channel not in self.pinnable_channels:
			return

		original_message_content = f"pinning [a message]({message.jump_url}) as requested by: {payload.member.mention}"
		original_message = await channel.send(embed=discord.Embed(description=original_message_content))

		if not self.bot.lists_has_intersection(self.bot.PIN_PERMISSIONS, payload.member.roles):
			await original_message.edit(embed=discord.Embed(description=original_message_content + f"\n:exclamation: FAILED\nTo pin a message, you need at lest one of the following roles:" + ("\n-".join([role.mention for role in self.bot.PIN_PERMISSIONS]))))
			return
		if message.pinned:
			await original_message.edit(embed=discord.Embed(description=original_message_content + "\n:pushpin: Already pinned!"))
			return

		try:
			await message.pin()
		except Exception:
			await original_message.edit(embed=discord.Embed(description=original_message_content + "\n:exclamation: FAILED (check bot permission) :exclamation:"))
			return

		await original_message.edit(embed=discord.Embed(description=original_message_content + "\nsuccess!"))

	@commands.command(
		aliases=["rp", ],
		help="Enables or Disables reaction pinning for given channels",
		usage="""> {prefix}{command} <enable|disable> *<channel ID|channel mention>
ex:
- Enabling reaction pinning in <#761546616036524063> and <#764367748125949952>
> {prefix}{command} enable <#761546616036524063> <#764367748125949952>
or
> {prefix}{command} e <#761546616036524063> <#764367748125949952>

- Disabling reaction pinning for <#761546616036524063> and <#764367748125949952>
> {prefix}{command} disable <#761546616036524063> <#764367748125949952>
or
> {prefix}{command} d <#761546616036524063> <#764367748125949952>"""
	)
	@commands.has_permissions(administrator=True)
	async def reactionpin(self, ctx: discord.ext.commands.Context, operation: str, *raw_channels: str):
		channels: set = set()
		for channel_str in raw_channels:
			try:
				channel = self.bot.LP_SERVER.get_channel(int(re.findall(r"\d+", channel_str)[0]))
				assert channel
				channels.add(channel)
			except (ValueError, IndexError, AssertionError):
				await ctx.send(embed=discord.Embed(title="Oops!", description=f"The bot wasn't able to find valid channel ID in `{channel_str}`"))
				return

		if not channels:
			await ctx.send(embed=discord.Embed(title="No channels were given", description="No channels were given as input. Aborting."))
			return

		if operation in ["enable", "e"]:
			self.pinnable_channels.update(channels)
			self.pinnable_channels_write()
			await ctx.send(embed=discord.Embed(title="Enabled Reaction pinning!", description=f"People can now react in {' | '.join([channel.mention for channel in channels])} with {' | '.join(map(str, self.pin_emojis))} to pin a message!"))
		elif operation in ["disable", "d"]:
			self.pinnable_channels.difference_update(channels)
			self.pinnable_channels_write()
			await ctx.send(embed=discord.Embed(title="Disabled Reaction pinning!", description=f"Adding reactions to messages in {' | '.join([channel.mention for channel in channels])} wil **NOT** pin them now."))
		else:
			raise discord.ext.commands.ArgumentParsingError

	@commands.command(
		help="Shows channels with reaction pinning enabled.",
		usage="""> {prefix}{command}"""
	)
	async def pinnable(self, ctx: discord.ext.commands.Context):
		# todo: show categories
		description = "\n- "+"\n- ".join([channel.mention for channel in self.pinnable_channels]) if self.pinnable_channels else "No channels have reaction pinning enabled yet."
		await ctx.send(embed=discord.Embed(title="Channels with reaction pinning enabled", description=description))

	@commands.command(
		help="Creates pin map from from source channel to destination channel.",
		usage="""> {prefix}{command} <source_channel> <destination_channel>
ex:
- Using channel mentions
> {prefix}{command} <#761546616036524063> <#764029864033779732>

- Using channel ids
> {prefix}{command} 761546616036524063 764029864033779732
"""
	)
	@commands.has_permissions(administrator=True)
	async def map(self, ctx: discord.ext.commands.Context, source_channel_raw: str, destination_channel_raw: str):
		try:
			source_channel = self.bot.LP_SERVER.get_channel(int(re.findall(r'\d+', source_channel_raw)[0]))
			destination_channel = self.bot.LP_SERVER.get_channel(int(re.findall(r'\d+', destination_channel_raw)[0]))
		except (ValueError, IndexError):
			raise discord.ext.commands.errors.BadArgument

		if not (source_channel or destination_channel):
			await ctx.send(embed=discord.Embed(title="Smh", description="That source and destination channel doesn't exist"))
			return
		if not source_channel:
			await ctx.send(embed=discord.Embed(title="Oopsies!", description="That source channel doesn't exist!"))
			return
		if not destination_channel:
			await ctx.send(embed=discord.Embed(title="Nope!", description="That destination channel doesn't exist!"))
			return

		self.channel_maps.add((source_channel, destination_channel))
		await ctx.send(embed=discord.Embed(title="Pin map registered/updated!", description=f"{source_channel.mention} ⟶ {destination_channel.mention}"))
		self.channel_maps_write()

	@commands.command(
		help="Removes pin map from source channel to destination channel.",
		usage="""> {prefix}{command} <source_channel> <destination_channel>
ex:
- Using channel mentions
> {prefix}{command} <#761546616036524063> <#764029864033779732>`

- Using channel ids
> {prefix}{command} 761546616036524063 764029864033779732
"""
	)
	@commands.has_permissions(administrator=True)
	async def unmap(self, ctx: discord.ext.commands.Context, source_channel_to_remove_raw: str, destination_channel_to_remove_raw: str):
		try:
			source_channel_to_remove = self.bot.LP_SERVER.get_channel(int(re.findall(r'\d+', source_channel_to_remove_raw)[0]))
			destination_channel_to_remove = self.bot.LP_SERVER.get_channel(int(re.findall(r'\d+', destination_channel_to_remove_raw)[0]))
		except (ValueError, IndexError):
			raise discord.ext.commands.errors.BadArgument

		self.channel_maps.discard((source_channel_to_remove, destination_channel_to_remove))
		self.channel_maps_write()
		await ctx.send(embed=discord.Embed(title="Unmapped!", description=f"Map {source_channel_to_remove.mention} ⟶ {destination_channel_to_remove.mention} was successfully removed"))

	@commands.command(
		help="Shows list of pin source and destination channels.",
		usage="> {prefix}{command}"
	)
	async def maps(self, ctx: discord.ext.commands.Context):
		description = ""

		if self.channel_maps:
			for source_channel, destination_channel in self.channel_maps:
				description += f"{source_channel.mention} ⟶ {destination_channel.mention}\n"
		else:
			description = "No maps yet."

		await ctx.send(
			embed=discord.Embed(
				title="Pin maps",
				description=description
			)
		)


def setup(bot: discord.ext.commands.Bot):
	bot.add_cog(Pinning(bot))
