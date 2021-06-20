from llama import Llama
from . import _util as util

import discord
from discord.ext import commands

import re


class SelfRole(commands.Cog):
    def __init__(self, bot):
        self.bot: Llama = bot

        # {"CHANNEL_ID/MESSAGE_ID": ["EMOJI_ID_OR_NAME;ROLE_ID", ...], ...}
        self.binds: dict = self.bot.llama_firebase.read("vars", "selfrole_messages")

        self.help_msg = ""
        self.main_help_fields = [
            ["Self role", "Only admins can create self role message"],
        ]

    async def cog_check(self, ctx: commands.Context):
        if exception_or_bool := await util.on_pm(ctx.message, self.bot):
            raise exception_or_bool
        return not exception_or_bool

    # self role add
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if (
            payload.member.id == self.bot.user.id
        ):  # ignore if the user who added the reaction is this bot
            return

        try:  # try to add get and add reaction
            for emoji_role in self.binds[f"{payload.channel_id}/{payload.message_id}"]:
                emoji_id_or_name, role_id = emoji_role.split(";")
                assert emoji_id_or_name and role_id
                if emoji_id_or_name in [payload.emoji.name, str(payload.emoji.id)]:
                    await payload.member.add_roles(
                        self.bot.LP_SERVER.get_role(int(role_id))
                    )
        except KeyError:
            pass  # no reaction role bind found

    # self role remove
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        try:  # try to get and remove reaction
            for emoji_role in self.binds[f"{payload.channel_id}/{payload.message_id}"]:
                emoji_id_or_name, role_id = emoji_role.split(";")
                assert emoji_id_or_name and role_id
                if emoji_id_or_name in [payload.emoji.name, str(payload.emoji.id)]:
                    await (
                        await self.bot.LP_SERVER.fetch_member(payload.user_id)
                    ).remove_roles(self.bot.LP_SERVER.get_role(int(role_id)))
        except KeyError:
            pass  # no reaction role bind found

    @commands.command(
        aliases=[
            "rr",
        ],
        help="Add reactions for self role to a message.",
        usage="""`MESSAGE_PATH`: can be `CHANNEL_ID`/`MESSAGE_ID` or a message jump url.

Add (`EMOJI_1` -> `ROLE_1`) and (`EMOJI_2` -> `ROLE_2`) binds from reaction role message.
> {prefix}{command} <add or a> `MESSAGE_PATH` `EMOJI_1` `ROLE_1` `EMOJI_2` `ROLE_2`

Remove (`EMOJI_1` -> `ROLE_1`) and (`EMOJI_2` -> `ROLE_2`) binds from reaction role message.
> {prefix}{command} <remove or r> `MESSAGE_PATH` `EMOJI_1` `ROLE_1` `EMOJI_2` `ROLE_2`""",
    )
    @util.must_be_admin()
    async def reactrole(
        self, ctx, mode, channel_id_or_message_path, *emojis_and_or_roles
    ):
        _mode = None  # 0: create, 1: remove
        if mode in ["add", "a"]:
            _mode = 0
        elif mode in ["remove", "r"]:
            _mode = 1
        else:
            raise discord.ext.commands.errors.BadArgument(
                f"Invalid input {mode}. Type `-help reactrole` for more information."
            )

        # parse url or message path
        flag = 0
        try:
            while True:  # remove trailing slash(es)
                if channel_id_or_message_path[-1] == "/":
                    channel_id_or_message_path = channel_id_or_message_path[:-1]
                else:
                    break

            # get "CHANNEL_ID/MESSAGE_ID" part of the input
            # regex: get the last two number/number pattern.
            # regex returns the first pattern that it finds so I had to flip the input with [::-1] and flip it back.
            # I know. Big brain.
            message_path = re.findall(r"\d+/\d+", channel_id_or_message_path[::-1])[0][
                ::-1
            ]
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

            await ctx.send(
                embed=discord.Embed(
                    title=f"Error while {title}!",
                    description="Are you sure the inputs are correct?",
                )
            )
            raise discord.ext.commands.errors.ArgumentParsingError

        # If can't pair emojis and roles in groups of 2
        if len(emojis_and_or_roles) % 2:
            raise discord.ext.commands.errors.BadArgument(
                "Failed to group emojis and roles. Number of emojis doesn't match the number of roles."
            )

        async def group_emojis_and_roles():
            """Pair list by groups of 2.
            From: https://stackoverflow.com/a/1751478/12979111
            """

            try:
                emojis_and_roles_parsed = []
                emoji_and_role_ids = []
                for emoji_raw, role_raw in [
                    emojis_and_or_roles[i : i + 2]
                    for i in range(0, len(emojis_and_or_roles), 2)
                ]:
                    # convert raw emoji input to integer if it's a custom emoji. Leave it alone otherwise.
                    # only custom emojis have "<". (<:emojis_name:emoji_id>)
                    emoji_id = (
                        emoji_raw
                        if "<" not in emoji_raw
                        else int(re.findall(r"\d+", emoji_raw)[0])
                    )
                    role_id = int(re.findall(r"\d+", role_raw)[0])

                    # check if role and emojis are valid
                    emoji = (
                        emoji_raw
                        if emoji_id == emoji_raw
                        else self.bot.get_emoji(emoji_id)
                    )
                    role = self.bot.LP_SERVER.get_role(role_id)
                    # todo: check if role is higher than bot
                    assert emoji, "emoji"
                    assert role, "role"

                    emoji_and_role_ids.append([emoji_id, role_id])
                    emojis_and_roles_parsed.append([emoji, role])
            except AssertionError as err:
                err_msg = """{one} {two} might not a valid {three} that can be used by the bot.
Are you sure it's not a {three} from other server?""".format(
                    one=str(err).title(),
                    two=emoji_raw if err == "emoji" else role_raw,
                    three=err,
                )

                await ctx.send(
                    embed=discord.Embed(
                        title=f"Error while parsing {err}!", description=err_msg
                    )
                )
                raise discord.ext.commands.errors.BadArgument(err_msg)
            return emojis_and_roles_parsed, emoji_and_role_ids

        if _mode == 0:  # add bind
            if message_path not in self.binds.keys():
                self.binds[message_path] = []

            emojis_and_roles_parsed, emoji_and_role_ids = await group_emojis_and_roles()

            # add what's not already in the binds
            self.binds[message_path] += list(
                {f"{emoji};{role}" for emoji, role in emoji_and_role_ids}
                - set(self.binds[message_path])
            )
            # push to firebase
            self.bot.llama_firebase.write(
                "vars", "selfrole_messages", message_path, self.binds[message_path]
            )
            # add reaction
            for emoji, _ in emojis_and_roles_parsed:
                await message.add_reaction(emoji)
        elif _mode == 1:  # remove bind
            if message_path not in self.binds.keys():
                await ctx.send(
                    embed=discord.Embed(
                        title=":no_entry_sign: Message does not have any reaction role emojis.",
                        description=f"No reaction role bind was found in the [message]({message.jump_url})",
                    )
                )

            # todo: confirm (clear all existing reactions too or leave them?)
            emojis_and_roles_parsed, emoji_and_role_ids = await group_emojis_and_roles()

            # remove binds
            for emoji, role in emoji_and_role_ids:
                emoji_role = f"{emoji};{role}"
                if emoji_role not in self.binds[message_path]:
                    await ctx.send(
                        embed=discord.Embed(
                            title=":no_entry_sign: Reaction role does not exist",
                            description="Bind (%s -> %s) was not found in the [message](%s)"
                            % (
                                self.bot.get_emoji(emoji),
                                self.bot.LP_SERVER.get_role(int(role)),
                                message.jump_url,
                            ),
                        )
                    )
                    continue

                self.binds[message_path].remove(emoji_role)

                await message.remove_reaction(emoji, self.bot.user)
                await ctx.send(
                    embed=discord.Embed(
                        title=":white_check_mark: Reaction role bind removed!",
                        description="Reaction role bind (%s -> %s) has been successfully removed from the [message](%s)!"
                        % (
                            self.bot.get_emoji(emoji),
                            self.bot.LP_SERVER.get_role(int(role)),
                            message.jump_url,
                        ),
                    )
                )

            # remove list if empty
            if not self.binds[message_path]:
                self.binds.pop(message_path)
                self.bot.llama_firebase.delete(
                    "vars", "selfrole_messages", message_path
                )
            else:
                self.bot.llama_firebase.write(
                    "vars",
                    "selfrole_messages",
                    message_path,
                    self.binds[message_path],
                    False,
                )


def setup(bot):
    bot.add_cog(SelfRole(bot))
