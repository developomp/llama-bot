import cogs._util as util
from datetime import datetime

import discord
from discord.ext import commands


class Util(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        help="Calculates of when a discord ID (aka snowflake) was created.",
        usage="""> {prefix}{command} <snowflake>
ex:
> {prefix}{command} 501277805540147220""",
    )
    async def snowflake(self, ctx, snowflake_to_parse):
        try:
            datetime_data = util.snowflake_to_datetime(snowflake_to_parse).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        except ValueError:
            await ctx.send(
                embed=discord.Embed(
                    description="Input must be a valid discord snowflake (i.e. a number)"
                )
            )
            return
        await ctx.send(
            embed=discord.Embed(
                description=f"snowflake `{snowflake_to_parse}` was created in: `{datetime_data}`"
            )
        )

    @commands.command(
        help="Measures communication delay (latency) in 1/1000 of a second, also known as millisecond (ms).",
    )
    async def ping(self, ctx):
        message_latency = int(
            (datetime.now() - ctx.message.created_at).microseconds / 1000
        )
        embed = (
            discord.Embed(description="**TR1GGERED**")
            .add_field(name="Message latency", value=f"{message_latency}ms")
            .add_field(name="API latency", value=f"{int(self.bot.latency * 1000)}ms")
        )
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Util(bot))
