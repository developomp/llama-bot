from llama_firebase import LlamaFirebase
import cogs._util as util

import discord
from discord.ext import commands

from os import listdir, path
from time import time
from typing import Union
import traceback
import json


def resolve_path(relative_path: str):
    """
    Converts relative path to absolute path for when the bot was executed in arbitrary path
    """
    return path.abspath(path.join(path.dirname(__file__), relative_path))


class Llama(commands.Bot):
    # the server the bot is intended to run on. It's useful to have this reference available.
    LP_SERVER: discord.Guild
    server_id: int = 457373827073048604

    # IDs of users who can run owners only commands
    owner_id: int = 501277805540147220
    owner_ids: set = {owner_id, 396333737148678165}

    def __init__(self, firebase_cred_path: str, prefix: str = "-"):
        super().__init__(
            help_command=None,  # to overwrite with custom help command
            command_prefix=prefix,
            case_insensitive=True,  # allow mix of lower cae and upper case for commands
        )

        # create firestore interface
        self.llama_firebase: LlamaFirebase = LlamaFirebase(firebase_cred_path)

        # read all configs and data for better responsiveness
        self.VARS = self.llama_firebase.read_collection("vars")

    # ----- [ DISCORD.PY STUFF ] -----

    async def on_ready(self):
        """
        variables in this function are checked if they exist before getting defined (reading from firebase which takes time)
        because the function on_ready() can be called multiple times as mentined in the discord.py documentaton:
        https://discordpy.readthedocs.io/en/latest/api.html#discord.on_ready
        """

        # Prevents bot from running in server other than LP's
        if not hasattr(self, "LP_SERVER"):
            self.LP_SERVER: discord.Guild = next(
                (guild for guild in self.guilds if guild.id == self.server_id), None
            )

        if not self.LP_SERVER:
            print("----------[ The bot is not in LP server! ]----------")
            exit(69)

        # load roles
        if not hasattr(self, "self.HIGHEST_ORDER"):
            self.HIGHEST_ORDER = self.get_role_from_vars("HIGHEST_ORDER")

        if not hasattr(self, "self.LPWB_MEMBER"):
            self.LPWB_MEMBER = self.get_role_from_vars("LPWB_MEMBER")

        if not hasattr(self, "self.SILK_PERMISSION"):
            self.SILK_PERMISSION = self.get_role_from_vars("SILK_PERMISSION")

        if not hasattr(self, "self.PYJAMAS"):
            self.PYJAMAS = self.get_role_from_vars("PYJAMAS")

        # define roles with access to special features
        self.LLAMA_PERMS = [
            getattr(self, i) for i in self.VARS["settings"]["LLAMA_PERM"]
        ]
        self.PIN_PERMISSIONS = [
            getattr(self, i) for i in self.VARS["settings"]["PIN_PERM"]
        ]

        # load cogs at the very last moment as some of them require data from the database
        # load all cogs that do not begin with a underscore
        cogs_dir = resolve_path("./cogs")
        for cog in [
            f"cogs.{path.splitext(f)[0]}"
            for f in listdir(cogs_dir)
            if path.isfile(path.join(cogs_dir, f)) and not f[0] == "_"
        ]:
            print(f"loading cog: {cog}")
            try:
                self.load_extension(cog)
            except commands.ExtensionAlreadyLoaded:
                print(f"Extension {cog} was already loaded. Skipping.")

        # to show bot uptime
        if not hasattr(self, "start_time"):
            self.start_time = time()

        print(f"{self.user} is up and ready!")

    async def on_command_error(
        self,
        ctx: commands.Context,
        error: commands.CommandError,
    ):
        """
        Gets executed when the bot encounters an error.
        """

        err_title: str = ""
        err_description: str = f"Command: {ctx.message.content.split()[0]}"

        if isinstance(error, util.NotAdminChannel):
            err_title = ":lock: Not in admin channel"
            err_description = f"This command can only be called in admins channels."

        if isinstance(error, commands.errors.NSFWChannelRequired):
            err_title = ":lock: Not in nsfw channel"
            err_description = "This command can only be called in NSFW channels."

        if isinstance(error, commands.errors.NotOwner):
            err_title = f":lock: Not a bot owner"
            err_description = "Only the bot owner(s) can call that command."

        if isinstance(error, commands.errors.BotMissingPermissions):
            missing_perms = "".join([f"- {i}\n" for i in error.missing_perms])
            err_title = ":exclamation: Missing Permission(s)"
            err_description = f"missing the following permissions:\n{missing_perms}"

        if isinstance(error, commands.errors.MissingRequiredArgument):
            err_title = f":exclamation: Missing required argument(s)"
            err_description = f"Consider using the `{self.command_prefix}help {ctx.command}` command to learn how to use it."

        if isinstance(
            error,
            (
                commands.errors.BadArgument,
                commands.ArgumentParsingError,
            ),
        ):
            err_title = f":exclamation: Invalid argument(s)"
            err_description = f"`Consider using the `{self.command_prefix}help {ctx.command}` command to learn how to use it."

        if isinstance(error, commands.errors.MemberNotFound):
            err_title = f":exclamation: Member not found"
            err_description = f"Member {error.argument} was not found in this server."

        # When command failed to complete
        if isinstance(error, commands.errors.CommandInvokeError):
            err_title = ":exclamation: Command Failed to complete"
            err_description = "Encountered an unknown error."

        await ctx.send(
            embed=discord.Embed(
                title=err_title,
                description=err_description,
            )
            .add_field(name="Channel", value=ctx.message.channel.mention)
            .add_field(name="Author", value=ctx.author.mention)
            .add_field(name="Message", value=f"[Message URL]({ctx.message.jump_url})")
            .add_field(name="Content", value=ctx.message.content[:1024], inline=False)
        )

        # Log details in terminal
        print("")
        print("=" * 30)
        print(type(error))
        print("Cog:", ctx.cog)
        print("Author:", ctx.author, ctx.author.id)
        print("Content:", ctx.message.content)
        print("Channel:", ctx.message.channel, ctx.message.channel.id)
        print("URL:", ctx.message.jump_url)
        print("")
        traceback.print_exception(type(error), error, error.__traceback__)
        print("=" * 30)
        print("")

    # ----- [ BOT METHODS ] -----

    def get_role_from_vars(self, name) -> Union[discord.Role, None]:
        """
        Get discord role by name
        """
        return discord.utils.get(self.LP_SERVER.roles, id=int(self.VARS["roles"][name]))

    def get_channel_from_vars(self, name) -> discord.abc.GuildChannel:
        """
        Get discord channel by name
        """
        return self.LP_SERVER.get_channel(int(self.VARS["channels"][name]))


def main():
    try:
        with open(resolve_path("./config.json"), "rt") as f:
            config = json.loads(f.read())
    except FileNotFoundError:
        # ignore if config.json does not exist
        pass

    with open(resolve_path("./secrets/secret.json"), "rt") as f:
        secret = json.loads(f.read())

    # set default prefix if it exists
    prefix = (
        (config["prefix"] if "prefix" in config else None)
        if "config" in locals()
        else None
    )
    firebase_path = resolve_path("./secrets/firebase-adminsdk.json")

    llama_bot = Llama(firebase_path, prefix) if prefix else Llama(firebase_path)
    llama_bot.run(secret["token"])


if __name__ == "__main__":
    main()
