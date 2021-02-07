import cogs._util as util

import discord
from discord.ext import commands


class Admin(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

		self.allowed_channels: list[discord.TextChannel] = [
			self.bot.LP_SERVER.get_channel(int(self.bot.VARS["channels"]["ADMIN_BOT"])),
		]

	async def error_if_not_in_admin_channel(self, ctx: discord.ext.commands.Context):
		if ctx.message.channel not in self.allowed_channels:
			raise util.NotAdminChannel(f"Admin commands can only be executed in: {', '.join([channel_id.mention for channel_id in self.allowed_channels])}")

	@commands.command(
		aliases=["m", ],
		help="Send and edit messages so other mods can change rules and stuff",
		usage="""Build and edit messages using the draft feature.
Type `{prefix}draft` for more information.
> {prefix}{command} <operation> <path> <message draft id 1>
operation: send, s, remove, delete, d, replace, r
path: message url, `CHANNEL_ID/MESSAGE_ID` path, channel id, channel mention, channel url
message draft id: `{prefix}draft list` to list ids

Sending message:
> {prefix}{command} send <path> <message draft id>

Deleting message:
> {prefix}{command} delete <message path> <message draft id>

Editing message:
> {prefix}{command} replace <message path> <message draft id>
"""
	)
	@util.must_be_admin()
	async def message(self, ctx, msg_or_channel_path: str = None, draft_id: str = None):
		await self.error_if_not_in_admin_channel(ctx)

		await ctx.send(
			embed=discord.Embed(title="Not ready yet", description="This feature is not implemented yet.")
		)

	@commands.command(
		aliases=["d", "drafts", ],
		help="Create and edit messages drafts for message command",
		usage="""> {prefix}{command} <operation> <message draft id 1> <message draft id 2>
operation: create, c, remove, r, edit, e, duplicate, d, rename, n, list, l
path: message url, `CHANNEL_ID/MESSAGE_ID` path, channel id, channel mention, channel url
message draft id: `{prefix}{command} list` to list ids or type with no space to create a new one (preferably separated by underscore `_`).

ex:
Creating new draft:
> {prefix}{command} create rules

Removing draft:
> {prefix}{command} remove server_invite

Editing draft:
> {prefix}{command} edit self_role

Duplicate draft:
> {prefix}{command} duplicate rules new_rules

Rename draft:
> {prefix}{command} rename self_role reaction_role

List available drafts:
> {prefix}{command} list
"""
	)
	@util.must_be_admin()
	async def draft(self, ctx, operation: str = None, draft_id: str = None):
		await self.error_if_not_in_admin_channel(ctx)

		await ctx.send(
			embed=discord.Embed(title="Not ready yet", description="This feature is not implemented yet.")
		)


def setup(bot):
	bot.add_cog(Admin(bot))
