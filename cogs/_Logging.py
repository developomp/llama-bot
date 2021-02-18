import datetime

import discord
from discord.ext import commands


class Logging(commands.Cog):
	# todo: better message deletion and edit logging (for #public-shaming)
	# todo: highlight content difference for deleted and edited messages
	# todo: separate snipe per channel
	# todo: depth in snipe (3 in queue)
	# todo: admin logging

	def __init__(self, bot):
		self.bot = bot

		self.remember_how_many = 3  # how many messages it will remember
		self.deletes = dict()
		self.edits = dict()

		self.last_del_message = None
		self.last_del_time = None

	@commands.Cog.listener()
	async def on_raw_message_edit(self, payload: discord.RawMessageUpdateEvent):
		"""
		{'type': 0, 'tts': False, 'timestamp': '2021-01-15T14:53:13.921000+00:00', 'pinned': False, 'mentions': [], 'mention_roles': [], 'mention_everyone': False, 'member': {'roles': ['752815735801118720', '680414683089469450', '457374385314201610', '457374509897613322', '733272327646871594', '784703868411969546', '750933652476788756', '500833792328466454', '457379204988665887'], 'premium_since': None, 'pending': False, 'nick': 'pompeii', 'mute': False, 'joined_at': '2019-07-01T10:17:03.040000+00:00', 'is_pending': False, 'hoisted_role': '784703868411969546', 'deaf': False}, 'id': '799652420710826035', 'flags': 0, 'embeds': [], 'edited_timestamp': '2021-01-15T15:05:53.352538+00:00', 'content': 'edit test test', 'channel_id': '528022645904769055', 'author': {'username': 'developomp', 'public_flags': 256, 'id': '501277805540147220', 'discriminator': '4447', 'avatar': '1074e4ef1f6a779b31f7ba41a1205c5e'}, 'attachments': [], 'guild_id': '457373827073048604'}

		{'type': 0, 'tts': False, 'timestamp': '2021-01-15T15:25:37.279000+00:00', 'pinned': True, 'mentions': [], 'mention_roles': [], 'mention_everyone': False, 'member': {'roles': ['457374509897613322', '457375740921380865', '500833792328466454', '680414683089469450'], 'premium_since': None, 'pending': False, 'nick': None, 'mute': False, 'joined_at': '2018-11-09T14:26:28.004000+00:00', 'is_pending': False, 'hoisted_role': '457374509897613322', 'deaf': False, 'user': {'username': 'jc.', 'id': 164159885267697664, 'avatar': '672d29df724d9710c44bed8f950e3e8c', 'discriminator': '7976', 'bot': False}}, 'id': '799660571745452062', 'flags': 0, 'embeds': [], 'edited_timestamp': None, 'content': '', 'channel_id': '457383745838776353', 'author': {'username': 'jc.', 'public_flags': 128, 'id': '164159885267697664', 'discriminator': '7976', 'avatar': '672d29df724d9710c44bed8f950e3e8c'}, 'attachments': [{'width': 550, 'url': 'https://cdn.discordapp.com/attachments/457383745838776353/799660566385000504/c6d2f74.png', 'size': 336183, 'proxy_url': 'https://media.discordapp.net/attachments/457383745838776353/799660566385000504/c6d2f74.png', 'id': '799660566385000504', 'height': 493, 'filename': 'c6d2f74.png'}], 'guild_id': '457373827073048604'}
		{'id': '799660702402084895', 'embeds': [{'type': 'rich', 'timestamp': '2021-01-15T15:25:37.279000+00:00', 'image': {'width': 550, 'url': 'https://cdn.discordapp.com/attachments/457383745838776353/799660566385000504/c6d2f74.png', 'proxy_url': 'https://media.discordapp.net/attachments/457383745838776353/799660566385000504/c6d2f74.png', 'height': 493}, 'footer': {'text': '#llama-drama-room | Sent at 2021-01-15 at 15:25:37'}, 'description': '[Jump to message](https://discord.com/channels/457373827073048604/457383745838776353/799660571745452062)', 'author': {'url': 'https://discord.com/channels/457373827073048604/457383745838776353/799660571745452062', 'proxy_icon_url': 'https://images-ext-2.discordapp.net/external/Y3ereyzaLU3rm04Ck8HImQFu2lpuhM-NEXTLHzjEwwk/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/164159885267697664/672d29df724d9710c44bed8f950e3e8c.webp', 'name': 'jc.', 'icon_url': 'https://cdn.discordapp.com/avatars/164159885267697664/672d29df724d9710c44bed8f950e3e8c.webp?size=1024'}}], 'channel_id': '511182634744020993', 'guild_id': '457373827073048604'}
		{'type': 0, 'tts': False, 'timestamp': '2021-01-15T15:25:37.279000+00:00', 'pinned': False, 'mentions': [], 'mention_roles': [], 'mention_everyone': False, 'member': {'roles': ['457374509897613322', '457375740921380865', '500833792328466454', '680414683089469450'], 'premium_since': None, 'pending': False, 'nick': None, 'mute': False, 'joined_at': '2018-11-09T14:26:28.004000+00:00', 'is_pending': False, 'hoisted_role': '457374509897613322', 'deaf': False, 'user': {'username': 'jc.', 'id': 164159885267697664, 'avatar': '672d29df724d9710c44bed8f950e3e8c', 'discriminator': '7976', 'bot': False}}, 'id': '799660571745452062', 'flags': 0, 'embeds': [], 'edited_timestamp': None, 'content': '', 'channel_id': '457383745838776353', 'author': {'username': 'jc.', 'public_flags': 128, 'id': '164159885267697664', 'discriminator': '7976', 'avatar': '672d29df724d9710c44bed8f950e3e8c'}, 'attachments': [{'width': 550, 'url': 'https://cdn.discordapp.com/attachments/457383745838776353/799660566385000504/c6d2f74.png', 'size': 336183, 'proxy_url': 'https://media.discordapp.net/attachments/457383745838776353/799660566385000504/c6d2f74.png', 'id': '799660566385000504', 'height': 493, 'filename': 'c6d2f74.png'}], 'guild_id': '457373827073048604'}
		{'id': '799663271253639188', 'embeds': [{'type': 'rich', 'timestamp': '2021-01-15T15:33:03.969000+00:00', 'fields': [{'value': "That's pretty unfortunate. You lost **⏣ 3,965,194**, and you also lost 1 <:fidgetspinner:573150030030962699> **Fidget Spinner**.", 'name': 'You died!', 'inline': False}], 'description': 'Grouped under `death`', 'color': 10395294}], 'channel_id': '576422815431917569', 'guild_id': '457373827073048604'}
		{'type': 0, 'tts': False, 'timestamp': '2021-01-15T15:31:53.566000+00:00', 'pinned': True, 'mentions': [], 'mention_roles': [], 'mention_everyone': False, 'member': {'roles': ['457374509897613322', '457375740921380865', '500833792328466454', '680414683089469450'], 'premium_since': None, 'pending': False, 'nick': None, 'mute': False, 'joined_at': '2018-11-09T14:26:28.004000+00:00', 'is_pending': False, 'hoisted_role': '457374509897613322', 'deaf': False, 'user': {'username': 'jc.', 'id': 164159885267697664, 'avatar': '672d29df724d9710c44bed8f950e3e8c', 'discriminator': '7976', 'bot': False}}, 'id': '799662150007783454', 'flags': 0, 'embeds': [], 'edited_timestamp': None, 'content': '', 'channel_id': '457383745838776353', 'author': {'username': 'jc.', 'public_flags': 128, 'id': '164159885267697664', 'discriminator': '7976', 'avatar': '672d29df724d9710c44bed8f950e3e8c'}, 'attachments': [{'width': 1795, 'url': 'https://cdn.discordapp.com/attachments/457383745838776353/799662146237235290/58f08ff.png', 'size': 1171304, 'proxy_url': 'https://media.discordapp.net/attachments/457383745838776353/799662146237235290/58f08ff.png', 'id': '799662146237235290', 'height': 1615, 'filename': '58f08ff.png'}], 'guild_id': '457373827073048604'}
		{'type': 0, 'tts': False, 'timestamp': '2021-01-15T15:31:53.566000+00:00', 'pinned': False, 'mentions': [], 'mention_roles': [], 'mention_everyone': False, 'member': {'roles': ['457374509897613322', '457375740921380865', '500833792328466454', '680414683089469450'], 'premium_since': None, 'pending': False, 'nick': None, 'mute': False, 'joined_at': '2018-11-09T14:26:28.004000+00:00', 'is_pending': False, 'hoisted_role': '457374509897613322', 'deaf': False, 'user': {'username': 'jc.', 'id': 164159885267697664, 'avatar': '672d29df724d9710c44bed8f950e3e8c', 'discriminator': '7976', 'bot': False}}, 'id': '799662150007783454', 'flags': 0, 'embeds': [], 'edited_timestamp': None, 'content': '', 'channel_id': '457383745838776353', 'author': {'username': 'jc.', 'public_flags': 128, 'id': '164159885267697664', 'discriminator': '7976', 'avatar': '672d29df724d9710c44bed8f950e3e8c'}, 'attachments': [{'width': 1795, 'url': 'https://cdn.discordapp.com/attachments/457383745838776353/799662146237235290/58f08ff.png', 'size': 1171304, 'proxy_url': 'https://media.discordapp.net/attachments/457383745838776353/799662146237235290/58f08ff.png', 'id': '799662146237235290', 'height': 1615, 'filename': '58f08ff.png'}], 'guild_id': '457373827073048604'}
		{'id': '799663472697933885', 'embeds': [{'type': 'rich', 'timestamp': '2021-01-15T15:31:53.566000+00:00', 'image': {'width': 1795, 'url': 'https://cdn.discordapp.com/attachments/457383745838776353/799662146237235290/58f08ff.png', 'proxy_url': 'https://media.discordapp.net/attachments/457383745838776353/799662146237235290/58f08ff.png', 'height': 1615}, 'footer': {'text': '#llama-drama-room | Sent at 2021-01-15 at 15:31:53'}, 'description': '[Jump to message](https://discord.com/channels/457373827073048604/457383745838776353/799662150007783454)', 'author': {'url': 'https://discord.com/channels/457373827073048604/457383745838776353/799662150007783454', 'proxy_icon_url': 'https://images-ext-2.discordapp.net/external/Y3ereyzaLU3rm04Ck8HImQFu2lpuhM-NEXTLHzjEwwk/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/164159885267697664/672d29df724d9710c44bed8f950e3e8c.webp', 'name': 'jc.', 'icon_url': 'https://cdn.discordapp.com/avatars/164159885267697664/672d29df724d9710c44bed8f950e3e8c.webp?size=1024'}}], 'channel_id': '511182634744020993', 'guild_id': '457373827073048604'}
		"""
		# print(payload.data)
		if payload.channel_id not in self.edits.keys():
			self.edits[payload.channel_id] = []
		self.edits[payload.channel_id].append(["before, after"])
		if len(self.edits) > self.remember_how_many:
			self.edits.pop(0)  # remove oldest message if the list gets long

	@commands.Cog.listener()
	async def on_message_delete(self, message):
		self.last_del_message = message
		self.last_del_time = datetime.datetime.utcnow()

	@commands.command(
		help="Shows recently deleted messages and its content. Memory does NOT get wiped after some time.",
		usage="""> {prefix}{command} {?depth}
Use it after someone deleted their message.

Show most recently deleted message
> {prefix}{command}

Show second most recently deleted message
> {prefix}{command} 2"""
	)
	async def snipe(self, ctx, depth=1):
		if not self.last_del_message:
			await ctx.send(f"There's no message deleted since last reboot!")
			return

		author = self.last_del_message.author
		await ctx.send(
			embed=discord.Embed(description=f"**Message deleted in:** <#{self.last_del_message.channel.id}> [Jump to Message]({self.last_del_message.jump_url})")
			.set_thumbnail(url=author.avatar_url)
			.add_field(name="Author", value=f"{author.mention} ({author})", inline=False)
			.add_field(name="Content", value=self.last_del_message.content, inline=False)
			.set_footer(text=f"Deleted at: {self.last_del_time.strftime('%Y-%m-%d %H:%M:%S')} UTC")
		)

	@commands.command(
		help="Shows most recently edited message and it's content before and after the edit. Memory gets wiped after some time.",
		usage="""> {prefix}{command} {?depth}
Use it after someone edited their message."""
	)
	async def editsnipe(self, ctx, depth=1):
		if not self.last_edit_after:
			await ctx.send(f"There's no message edited since last reboot!")
			return

		author = self.last_edit_after.author
		await ctx.send(
			embed=discord.Embed(description=f"**Message Edited in:** <#{self.last_edit_after.channel.id}> [Jump to Message]({self.last_edit_after.jump_url})")
			.set_thumbnail(url=author.avatar_url)
			.add_field(name="Author", value=f"{author.mention} ({author})", inline=False)
			.add_field(name="Before", value=self.last_edit_before.content, inline=False)
			.add_field(name="After", value=self.last_edit_after.content, inline=False)
			.set_footer(text=f"Edited at: {self.last_edit_after.edited_at.strftime('%Y-%m-%d %H:%M:%S')} UTC")
		)


def setup(bot):
	bot.add_cog(Logging(bot))
