import cogs._util as util
import json

import discord
from discord.ext import commands


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.allowed_channels: list[discord.TextChannel] = [
            self.bot.LP_SERVER.get_channel(int(self.bot.VARS["channels"]["ADMIN_BOT"])),
        ]

        self.draft_common_message = "required to create a new draft"

    def draft_id_required_error_message(self, draft_id):
        """checks if draft id is passed in draft command"""
        if not draft_id:
            raise discord.ext.commands.errors.MissingRequiredArgument(
                "draft id is" + self.draft_common_message
            )

    def draft_ids_are_required_error_message(self, draft_id, draft_id2):
        """checks if draft id 1 and 2 are passed in draft command"""
        if not (draft_id and draft_id2):
            raise discord.ext.commands.errors.MissingRequiredArgument(
                "draft ids are" + self.draft_common_message
            )

    async def error_if_not_in_admin_channel(self, ctx: discord.ext.commands.Context):
        if ctx.message.channel not in self.allowed_channels:
            allowed_in = ", ".join(
                [channel_id.mention for channel_id in self.allowed_channels]
            )
            raise util.NotAdminChannel(
                f"Admin commands can only be executed in: {allowed_in}"
            )

    @commands.command(
        aliases=[
            "m",
        ],
        help="Send and edit messages so other mods can change rules and stuff",
        usage="""Build and edit messages using the draft feature.
Type `{prefix}help draft` for more information.
> {prefix}{command} <operation> <selector> <message draft id>
selector: message url, `CHANNEL_ID/MESSAGE_ID` path, channel id, channel mention, channel url
message draft id: type `{prefix}draft list` to list available ids

Sending message:
> {prefix}{command} <send/create/s/c> <channel selector> <message draft id>

Deleting message:
> {prefix}{command} <delete/remove/d> <message selector> <message draft id>

Replacing message:
> {prefix}{command} <replace/r> <message selector> <message draft id>
""",
    )
    @util.must_be_admin()
    async def message(self, ctx, msg_or_channel_path: str = None, draft_id: str = None):
        await self.error_if_not_in_admin_channel(ctx)

        await ctx.send(
            embed=discord.Embed(
                title="Not ready yet",
                description="This feature is not implemented yet.",
            )
        )

    @commands.command(
        aliases=[
            "d",
            "drafts",
        ],
        help="Create and edit message drafts for the `message` command",
        usage="""> {prefix}{command} <operation> <draft id 1> <draft id 2>
draft ids: string with no space (preferably separated by underscores `_`).

Creating new draft:
> {prefix}{command} <create/new/c/n> <draft id>

Removing draft:
> {prefix}{command} <remove/delete/del> <draft id>

Editing draft:
> {prefix}{command} <edit/e> <draft id>

Duplicating draft:
> {prefix}{command} <duplicate/copy/cp> <source draft id> <new draft id>

Renaming draft:
> {prefix}{command} <rename/rn> <old draft id> <new draft id>

Previewing draft:
> {prefix}{command} <preview/p> <draft id>

View raw data of a draft
> {prefix}{command} <view/v> <draft id>

Listing available drafts:
> {prefix}{command} <list/l>
""",
    )
    @util.must_be_admin()
    async def draft(
        self, ctx, operation: str, draft_id: str = None, draft_id2: str = None
    ):
        """https://discord.com/developers/docs/resources/channel#embed-object"""
        await self.error_if_not_in_admin_channel(ctx)

        if operation in ["create", "new", "c", "n"]:
            self.draft_id_required_error_message(draft_id)

            try:  # check if draft already exists
                if self.bot.VARS["drafts"][draft_id]:
                    await ctx.send(
                        embed=discord.Embed(
                            title="Draft already exists",
                            description="A draft with the same id was found. Edit it, or delete and create a new one.",
                        )
                    )
                    return
            except KeyError:
                pass  # draft does not exist. Can create a new one.

            # create new embed with default values
            new_embed_data = dict()
            new_embed_data["title"] = "title"
            new_embed_data["description"] = "description"
            new_embed_data["color"] = 0
            new_embed_data["fields"] = [
                {"name": "name1", "value": "value1", "inline": True},
                {"name": "name2", "value": "value2", "inline": True},
            ]

            # update local and database vars
            json_embed_data = json.dumps(new_embed_data)
            self.bot.VARS["drafts"][draft_id] = json_embed_data
            self.bot.llama_firebase.create("vars", "drafts", draft_id, json_embed_data)

            # feedback
            await ctx.send(
                embed=discord.Embed(
                    title="Success!",
                    description=f"New draft `{draft_id}` has been created.",
                )
            )
        elif operation in ["remove", "delete", "del"]:
            self.draft_id_required_error_message(draft_id)

            try:
                # delete draft from local variable
                del self.bot.VARS["drafts"][draft_id]
            except KeyError:  # when draft id is not found
                await ctx.send(
                    embed=discord.Embed(
                        title="Draft does not exist",
                        description=f"A draft with the id `{draft_id}` was not found. You're trying to delete a draft that does not exist.",
                    )
                )
                return

            # delete if it's not found in local variable
            self.bot.llama_firebase.delete("vars", "drafts", draft_id)

            # feedback
            await ctx.send(
                embed=discord.Embed(
                    title="Success!",
                    description=f"Draft `{draft_id}` has been successfully removed.",
                )
            )
        elif operation in ["edit", "e"]:
            self.draft_id_required_error_message(draft_id)

            try:  # check if draft exists
                self.bot.VARS["drafts"][draft_id]
            except KeyError:  # draft does not exist. Show error message.
                await ctx.send(
                    embed=discord.Embed(
                        title="Draft does not exists",
                        description=f"A draft with the id {draft_id} was not found. Create it first.",
                    )
                )
                return

            # create new embed with default values
            new_embed_data = json.loads(self.bot.VARS["drafts"][draft_id])
            new_embed_data["title"] = "title"
            new_embed_data["description"] = "description"
            new_embed_data["color"] = 0
            new_embed_data["fields"] = [
                {"name": "name1", "value": "value1", "inline": True},
                {"name": "name2", "value": "value2", "inline": True},
            ]

            # update local and database vars
            json_embed_data = json.dumps(new_embed_data)
            self.bot.VARS["drafts"][draft_id] = json_embed_data
            self.bot.llama_firebase.write("vars", "drafts", draft_id, json_embed_data)

            # feedback
            await ctx.send(
                embed=discord.Embed(
                    title="Success!",
                    description=f"Draft `{draft_id}` has been successfully edited.",
                )
            )
        elif operation in ["duplicate", "copy", "cp"]:
            self.draft_ids_are_required_error_message(draft_id, draft_id2)

            try:  # check if draft id is available
                if self.bot.VARS["drafts"][draft_id2]:
                    await ctx.send(
                        embed=discord.Embed(
                            title="Name not available",
                            description=f"A draft with the id `{draft_id2}` already exists. Choose another id.",
                        )
                    )
                    return
            except KeyError:
                pass  # draft id is available. Can create a copy.

            # update local and database vars
            self.bot.VARS["drafts"][draft_id2] = self.bot.VARS["drafts"][draft_id]
            self.bot.llama_firebase.create(
                "vars", "drafts", draft_id2, self.bot.VARS["drafts"][draft_id2]
            )

            # feedback
            await ctx.send(
                embed=discord.Embed(
                    title="Success!",
                    description=f"New draft `{draft_id2}` has been created from `{draft_id}`.",
                )
            )
        elif operation in ["rename", "rn"]:
            self.draft_ids_are_required_error_message(draft_id, draft_id2)

            try:  # check if draft id is available
                if self.bot.VARS["drafts"][draft_id2]:
                    await ctx.send(
                        embed=discord.Embed(
                            title="Name not available",
                            description=f"A draft with the id `{draft_id2}` already exists. Choose another id.",
                        )
                    )
                    return
            except KeyError:
                pass  # draft id is available. Can rename draft.

            # update local and database vars
            self.bot.VARS["drafts"][draft_id2] = self.bot.VARS["drafts"][draft_id]
            del self.bot.VARS["drafts"][draft_id]
            self.bot.llama_firebase.delete("vars", "drafts", draft_id)
            self.bot.llama_firebase.create(
                "vars", "drafts", draft_id2, self.bot.VARS["drafts"][draft_id2]
            )

            # feedback
            await ctx.send(
                embed=discord.Embed(
                    title="Success!",
                    description=f"Draft `{draft_id}` has been renamed to`{draft_id2}`.",
                )
            )
        elif operation in ["preview", "p"]:
            self.draft_id_required_error_message(draft_id)

            try:
                await ctx.send(
                    f"> preview of draft **{draft_id}**",
                    embed=discord.Embed.from_dict(
                        json.loads(self.bot.VARS["drafts"][draft_id])
                    ),
                )
            except KeyError:
                await ctx.send(
                    embed=discord.Embed(
                        title="Cannot find draft",
                        description=f"draft `{draft_id}` was not found in the draft database.",
                    )
                )
        elif operation in ["view", "v"]:
            self.draft_id_required_error_message(draft_id)

            await ctx.send(
                embed=discord.Embed(
                    title=draft_id,
                    description="```%s```"
                    % json.dumps(
                        json.loads(self.bot.VARS["drafts"][draft_id]), indent=4
                    ),
                )
            )
        elif operation in ["list", "l"]:
            await ctx.send(
                embed=discord.Embed(
                    title="List of drafts",
                    description="Nothing found"
                    if not self.bot.VARS["drafts"]
                    else "".join([f"\n- **{i}**" for i in self.bot.VARS["drafts"]]),
                )
            )


def setup(bot):
    bot.add_cog(Admin(bot))
