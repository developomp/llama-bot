from llama import Llama
from . import _util as util

import discord
from discord.ext import commands


class DM(commands.Cog):
    def __init__(self, bot):
        self.bot: Llama = bot

        self.emojis: set[discord.PartialEmoji] = set()

        for emoji_raw in self.bot.VARS["dm"]["emojis"]:
            self.emojis.add(util.convert_to_partial_emoji(emoji_raw, self.bot))

    async def cog_check(self, ctx: commands.Context):
        if exception_or_bool := await util.on_pm(ctx.message, self.bot):
            raise exception_or_bool
        return not exception_or_bool

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        await util.on_pm(message, self.bot)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.guild_id or (payload.emoji not in self.emojis):
            return

        user: discord.User = await self.bot.fetch_user(payload.user_id)
        if not user.dm_channel:
            await user.create_dm()
        channel: discord.DMChannel = user.dm_channel
        message: discord.Message = await channel.fetch_message(payload.message_id)
        if message.author == self.bot.user:
            await message.delete()


def setup(bot):
    bot.add_cog(DM(bot))
