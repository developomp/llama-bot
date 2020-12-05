import datetime
from threading import Timer

import discord
from discord.ext import commands


class Logging(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

		self.clear_edit()
		self.clear_del()

		self.duration: float = 120.0

	def clear_del(self):
		self.last_del_message = None
		self.last_del_time = None

	def clear_edit(self):
		self.last_edit_before = None
		self.last_edit_after = None

	@commands.Cog.listener()
	async def on_message_edit(self, before, after):
		self.last_edit_before = before
		self.last_edit_after = after
		self.edit_timer = Timer(interval=self.duration, function=self.clear_edit, args=(self,))

	@commands.Cog.listener()
	async def on_message_delete(self, message):
		self.last_del_message = message
		self.last_del_time = datetime.datetime.utcnow()
		self.del_timer = Timer(interval=self.duration, function=self.clear_del, args=(self,))

	@commands.command(
		help="Shows the most recently deleted message and its content. Memory gets wiped after some time.",
		usage="""> {prefix}{command}
Use it after someone edited/deleted their message."""
	)
	async def snipe(self, ctx):
		if not self.last_del_message:
			await ctx.send(f"There's no message deleted in the last {self.duration} seconds!")
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
		usage="""> {prefix}{command}
Use it after someone edited their message."""
	)
	async def editsnipe(self, ctx):
		if not self.last_edit_after:
			await ctx.send(f"There's no message edited in the last {self.duration} seconds!")
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
