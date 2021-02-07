# I'm aware that I can use @commands.bot_has_permissions. It's a choice.
import re

import discord
from discord.ext import commands


def must_be_admin():
	"""Discord bot command decorator.
	Put it under @discord.ext.commands.command()
	"""

	async def predicate(ctx: discord.ext.commands.Context):
		if ctx.message.author.guild_permissions.administrator:
			return True
		await ctx.send(embed=discord.Embed(description=f"You need to be a server administrator to issue the command. Aborting."))
		return False

	return commands.check(predicate)


def lists_has_intersection(list1: list, list2: list) -> bool:
	"""Checks if any of the roles in roles1 is in roles2
	"""
	return any(element in list1 for element in list2)


def url_from_str(string: str) -> list:
	# https://daringfireball.net/2010/07/improved_regex_for_matching_urls
	url = re.findall(
		r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))",
		string
	)
	return [x[0] for x in url]
