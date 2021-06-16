from llama_firebase import LlamaFirebase
import cogs._util as util

import discord
from discord.ext import commands

from os import listdir
from os.path import isfile, join, splitext, dirname, abspath
from time import time
import traceback
import json


def resolve_path(relative_path: str):
    """
    Converts relative path to absolute path for when the bot was executed in arbitrary path
    """
    return abspath(join(dirname(__file__), relative_path))


class Llama(commands.Bot):
    def __init__(self, firebase_cred_path: str, prefix: str = "-"):
        super().__init__(
            help_command=None,  # to overwrite with custom help command
            command_prefix=prefix,
            case_insensitive=True,  # allow mix of lower cae and upper case for commands
        )

        # my own firestore interface
        self.llama_firebase: LlamaFirebase = LlamaFirebase(firebase_cred_path)

        # read all variables in the beginning to save time later
        self.VARS = self.llama_firebase.read_collection("vars")

        self.server_id = 457373827073048604

        # IDs of users who can run owners only commands
        self.owner_ids: set = {501277805540147220, 396333737148678165}
        # Pinged/DMed when there's an issue with the bot
        self.fixer_ids: set = {501277805540147220}

    # ----- [ DISCORD.PY STUFF ] -----

    async def on_ready(self):
        """https://discordpy.readthedocs.io/en/latest/api.html#discord.on_ready
        Called when the client is done preparing the data received from Discord.
        Usually after login is successful and the Client.guilds and co. are filled up.

        **WARNING**:
        This function is not guaranteed to be the first event called.
        Likewise, this function is not guaranteed to only be called once.
        Discord.py implements reconnection logic and thus will end up calling this event whenever a RESUME request fails.
        """

        # Prevents bot from running in server other than LP's
        self.LP_SERVER: discord.Guild = next(
            (guild for guild in self.guilds if guild.id == self.server_id), None
        )
        if not self.LP_SERVER:
            print("----------[ The bot is not in LP server! ]----------")
            exit(-6969)

        # load roles
        self.HIGHEST_ORDER = self.get_role_from_vars("HIGHEST_ORDER")
        self.LPWB_MEMBER = self.get_role_from_vars("LPWB_MEMBER")
        self.SILK_PERMISSION = self.get_role_from_vars("SILK_PERMISSION")
        self.PYJAMAS = self.get_role_from_vars("PYJAMAS")

        # define roles with access to special features
        self.LLAMA_PERMS = [
            getattr(self, i) for i in self.VARS["settings"]["LLAMA_PERM"]
        ]
        self.PIN_PERMISSIONS = [
            getattr(self, i) for i in self.VARS["settings"]["PIN_PERM"]
        ]

        # load cogs at the very last moment as some of them require data from the database
        # load all cogs that does not begin with a underscore
        cogs_dir = resolve_path("./cogs")
        for cog in [
            f"cogs.{splitext(f)[0]}"
            for f in listdir(cogs_dir)
            if isfile(join(cogs_dir, f)) and not f[0] == "_"
        ]:
            print(f"loading cog: {cog}")
            self.load_extension(cog)

        # to show bot uptime
        self.start_time = time()
        print(f"{self.user} is up and ready!")

    async def on_command_error(
        self,
        ctx: discord.ext.commands.Context,
        error: discord.ext.commands.CommandError,
    ):
        """Gets executed when the bot encounters an error."""

        error_message = str(error)

        # When command that is only meant to be called in admin channels are called elsewhere
        if isinstance(error, util.NotAdminChannel):
            await ctx.send(
                embed=discord.Embed(
                    title="<:hinkies:766672386132934666> Not in admin channel!",
                    description=error_message,
                )
            )

        # When NSFW commands are called in non NSFW channels
        if isinstance(error, discord.ext.commands.errors.NSFWChannelRequired):
            await ctx.send(
                embed=discord.Embed(
                    title=":lock: This command is not available in non NSFW channel"
                )
            )

        # When the bot doesn't have permissions it requires to run a command
        if isinstance(error, discord.ext.commands.errors.BotMissingPermissions):
            missing_perms_list = "".join([f"- {i}\n" for i in error.missing_perms])
            await ctx.send(
                embed=discord.Embed(
                    title="Aw man",
                    description=f"The bot require following permissions to run command `{ctx.message.content}`.\n{missing_perms_list}",
                )
            )

        # When a command that can only be called by the owners are called
        if isinstance(error, discord.ext.commands.errors.NotOwner):
            await ctx.send(
                embed=discord.Embed(
                    title="Oops!",
                    description=f"You have to be a bot owner to run command `{ctx.message.content}`.",
                )
            )

        # When argument(s) required by the command is not passed
        if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
            await ctx.send(
                embed=discord.Embed(
                    title="Error!",
                    description=f"Command `{ctx.message.content}` is missing required argument(s).\nConsider using `{self.command_prefix}help {ctx.command}` to learn how to use it.",
                )
            )

        # When invalid argument is passed
        if isinstance(
            error,
            (
                discord.ext.commands.errors.BadArgument,
                discord.ext.commands.ArgumentParsingError,
            ),
        ):
            await ctx.send(
                embed=discord.Embed(
                    title="Hol up!",
                    description=f"command `{ctx.message.content}` is given invalid argument(s).\nConsider using `{self.command_prefix}help {ctx.command}` to learn how to use it.",
                )
            )

        # When user id doesn't correspond to anyone in the server
        if isinstance(error, discord.ext.commands.errors.MemberNotFound):
            await ctx.send(
                embed=discord.Embed(
                    title="Hmm...",
                    description=f"Member {error.argument} was not found in this server.",
                )
            )

        # When command failed to complete
        if isinstance(error, discord.ext.commands.errors.CommandInvokeError):
            await ctx.send(
                embed=discord.Embed(
                    title="Error!",
                    description="Command Failed to complete. This is most likely a problem on the bot's side.",
                )
            )

        # Log details in terminal
        print("")
        print("=" * 30)
        print(type(error))
        print("Cog:", ctx.cog)
        print("Author:", ctx.author, ctx.author.id)
        # show message that actually caused the error
        print("Content:", ctx.message.content)
        print("Channel:", ctx.message.channel, ctx.message.channel.id)
        print("URL:", ctx.message.jump_url)
        print("")
        traceback.print_exception(type(error), error, error.__traceback__)
        print("=" * 30)
        print("")

    # ----- [ BOT METHODS ] -----

    def get_role_from_vars(self, name):
        """Get discord role by name"""
        return discord.utils.get(self.LP_SERVER.roles, id=int(self.VARS["roles"][name]))

    def get_channel_from_vars(self, name) -> discord.abc.GuildChannel:
        """Get discord channel by name"""
        return self.LP_SERVER.get_channel(int(self.VARS["channels"][name]))


def main():
    with open(resolve_path("./config.json"), "rt") as f:
        config = json.loads(f.read())

    with open(resolve_path("./secrets/secret.json"), "rt") as f:
        secret = json.loads(f.read())

    llama_bot = Llama(
        resolve_path("./secrets/firebase-adminsdk.json"),
        # set default prefix to "-" if not specified
        config["prefix"] if config["prefix"] else "-",
    )

    llama_bot.run(secret["token"])


if __name__ == "__main__":
    main()
