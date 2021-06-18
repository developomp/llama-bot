import datetime

import discord
from discord.ext import commands


class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.log_edit = True
        self.remember_how_many = 3  # how many messages it will remember

        # {CHANNEL_ID: [MSG_UPDATE, ...], ..}
        self.edits: dict[int, list[discord.RawMessageUpdateEvent]] = dict()
        # {CHANNEL_ID: [[DELETE_TIME, MSG_DELETE], ...], ...}
        self.deletes: dict[
            int, list[list[datetime.datetime, discord.RawMessageDeleteEvent]]
        ] = dict()
        # {CHANNEL_ID: [[DELETE_TIME, MSG_BULK_DELETE], ...], ...}
        self.bulk_deletes: dict[
            int, list[list[datetime.datetime, discord.RawBulkMessageDeleteEvent]]
        ] = dict()
        # {AUTHOR_ID: {CHANNEL_ID: [MSG_UPDATE, ...], ...}, ...}

        # {AUTHOR_ID: {CHANNEL_ID: [MSG_UPDATE, ...], ...}, ...}
        self.edits_per_user: dict[
            int, dict[int, list[discord.RawMessageUpdateEvent]]
        ] = dict()
        # {AUTHOR_ID: {CHANNEL_ID: [MSG_DELETE, ...], ...}, ...}
        self.deletes_per_user: dict[
            int, dict[int, list[discord.RawMessageDeleteEvent]]
        ] = dict()

    @commands.Cog.listener()
    async def on_raw_message_edit(self, payload: discord.RawMessageUpdateEvent):
        # channel level
        if payload.channel_id not in self.edits.keys():
            self.edits[payload.channel_id] = []

        self.edits[payload.channel_id].append(payload)

        if len(self.edits[payload.channel_id]) > self.remember_how_many:
            del self.edits[payload.channel_id][0]

        # user level
        try:
            author_id: int = int(payload.data["author"]["id"])
        except KeyError:
            return

        if author_id not in self.edits_per_user.keys():
            self.edits_per_user[author_id] = dict()

        if payload.channel_id not in self.edits_per_user[author_id].keys():
            self.edits_per_user[author_id][payload.channel_id] = []

        self.edits_per_user[author_id][payload.channel_id].append(payload)

        if (
            len(self.edits_per_user[author_id][payload.channel_id])
            > self.remember_how_many
        ):
            # todo: queue task to prevent timing issue causing the deletion of the same message
            del self.edits_per_user[author_id][payload.channel_id][0]

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload: discord.RawMessageDeleteEvent):
        # channel level
        if payload.channel_id not in self.deletes.keys():
            self.deletes[payload.channel_id] = []

        self.deletes[payload.channel_id].append([datetime.datetime.utcnow(), payload])

        if len(self.deletes[payload.channel_id]) > self.remember_how_many:
            del self.deletes[payload.channel_id][0]

        # user level
        if payload.cached_message:
            author_id = payload.cached_message.author.id
            if author_id not in self.deletes_per_user.keys():
                self.deletes_per_user[author_id] = dict()

            if payload.channel_id not in self.deletes_per_user[author_id].keys():
                self.deletes_per_user[author_id][payload.channel_id] = []

            self.deletes_per_user[author_id][payload.channel_id].append(payload)

            if (
                len(self.deletes_per_user[author_id][payload.channel_id])
                > self.remember_how_many
            ):
                # todo: queue task to prevent timing issue causing the deletion of the same message
                del self.deletes_per_user[author_id][payload.channel_id][0]

    @commands.Cog.listener()
    async def on_raw_bulk_message_delete(
        self, payload: discord.RawBulkMessageDeleteEvent
    ):
        if payload.channel_id not in self.bulk_deletes.keys():
            self.bulk_deletes[payload.channel_id] = []

        self.bulk_deletes[payload.channel_id].append(
            [datetime.datetime.utcnow(), payload]
        )

        if len(self.bulk_deletes[payload.channel_id]) > self.remember_how_many:
            del self.bulk_deletes[0]

    async def log_edit(
        self, channel: discord.TextChannel, payload: discord.RawMessageUpdateEvent
    ):
        await channel.send(
            embed=discord.Embed(
                title="Message Edited",
                description=f"""**@<PLAYER> Edited their message in: <#CHANNEL>
[jump to message](URL)**""",
            )
            .add_field(
                name="before", value=payload.cached_message.content, inline=False
            )
            .add_field(name="after", value=payload.data["content"], inline=False)
        )

    async def log_delete(
        self, channel: discord.TextChannel, payload: discord.RawMessageDeleteEvent
    ):
        await channel.send(embed=discord.Embed(title="Message Deleted", description=""))

    async def log_bulk_delete(
        self, channel: discord.TextChannel, payload: discord.RawBulkMessageDeleteEvent
    ):
        await channel.send(
            embed=discord.Embed(title="Bulk Message Deletion", description="")
        )


'''
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
'''


def setup(bot):
    bot.add_cog(Logging(bot))
