from llama import Llama
from . import _util as util

import discord
from discord.ext import commands

import sys
from time import time
from datetime import timedelta, datetime


class Core(commands.Cog):
    def __init__(self, bot):
        self.bot: Llama = bot

        # remove any potential existing help command to prevent collision
        self.bot.remove_command("help")

    async def cog_check(self, ctx: commands.Context):
        if exception_or_bool := await util.on_pm(ctx.message, self.bot):
            raise exception_or_bool
        return not exception_or_bool

    @commands.command(
        help="Shows very basic information about the bot.",
    )
    async def about(self, ctx):
        uptime = str(timedelta(seconds=int(round(time() - self.bot.start_time))))
        bot_created_time = datetime.utcfromtimestamp(
            ((int(self.bot.user.id) >> 22) + 1420070400000) / 1000
        )
        bot_created_delta = datetime.now() - bot_created_time

        await ctx.send(
            embed=discord.Embed(title="About llama bot")
            .set_thumbnail(url=self.bot.user.avatar_url)
            .add_field(
                name="Python version",
                value=sys.version.split()[0],
            )
            .add_field(
                name="Discord.py version",
                value=discord.__version__,
            )
            .add_field(name="Bot ID", value=f"{self.bot.user.id}")
            .add_field(
                name="Created in (UTC)",
                value=f"{bot_created_time.strftime('%Y-%m-%d %H:%M:%S')} ({bot_created_delta.days} days ago)",
            )
            .add_field(name="Uptime", value=uptime, inline=False)
            .add_field(
                name="Source Code",
                value="https://github.com/developomp/llama-bot",
                inline=False,
            )
        )

    @commands.command(
        aliases=[
            "h",
        ],
        help="Shows list of helpful information about a command or a cog.",
        usage="""> {prefix}{command} <cog | command | None>
ex:
List cogs:
> {prefix}{command}

List commands in the `core` cog:
> {prefix}{command} core

Shows info about `ping` command:
> {prefix}{command} ping""",
    )
    async def help(self, ctx, cog_str=None):
        if not cog_str:  # when no argument is passed
            help_embed = discord.Embed(
                title="Help",
                description=f"Use `{self.bot.command_prefix}help <cog>` command to get more information on a cog. (case insensitive)",
            )

            for cog_name in self.bot.cogs:
                # Show command to get help for a cog
                help_embed.add_field(
                    name=cog_name,
                    value=f"`{self.bot.command_prefix}help {cog_name.lower()}`",
                )

            for cog_name in self.bot.cogs:
                # fields that will be shown in main help embed
                try:
                    for field in self.bot.get_cog(cog_name).main_help_fields:
                        help_embed.add_field(
                            name=field[0], value=field[1], inline=False
                        )
                except AttributeError:
                    # cog doesn't have main_help_fields
                    pass

            await ctx.send(embed=help_embed)
        else:  # when searching for a specific cog
            cogs = list(self.bot.cogs.keys())
            lower_cogs = [cog.lower() for cog in cogs]
            lower_cog_str = cog_str.lower()  # lower case string of cog

            if lower_cog_str in lower_cogs:  # when a cog has been found
                cog = self.bot.get_cog(cogs[lower_cogs.index(lower_cog_str)])

                await ctx.send(
                    embed=discord.Embed(
                        title=f'"{lower_cog_str}" commands',
                        description=f"Use `{self.bot.command_prefix}help <command>` to get more information about a command. (case insensitive)\n\n"
                        # keep cog_help empty if cog.help_msg does not exist
                        + (cog.help_msg + ("\n\n" if cog.help_msg else ""))
                        if hasattr(cog, "help_msg")
                        else ""
                        + f"**Commands:**\n `{'`, `'.join([command.name for command in cog.get_commands()])}`",
                    )
                )
            else:  # when a cog has not been found
                command: discord.ext.commands.Command = discord.utils.get(
                    self.bot.commands, name=cog_str
                )

                if not command:  # when command was not found
                    await ctx.send(
                        embed=discord.Embed(
                            description=f"Cannot find cog/command **{cog_str}**.\nUse the `{self.bot.command_prefix}help` command to list all enabled cogs."
                        )
                    )
                else:  # when a command has been found
                    await ctx.send(
                        embed=discord.Embed(
                            title=f"{self.bot.command_prefix}{command.name}",
                            description=(
                                f"**Aliases:** `{'`, `'.join(command.aliases)}`"
                                if command.aliases
                                else ""
                            )
                            + "\n\n**Description:**\n"
                            + (
                                command.help
                                if command.help
                                else "Under construction..."
                            )
                            + "\n\n**Usage:**\n"
                            + (
                                command.usage
                                if command.usage
                                else "> {prefix}{command}"
                            ).format(
                                prefix=self.bot.command_prefix, command=command.name
                            ),
                        )
                    )


def setup(bot):
    bot.add_cog(Core(bot))
