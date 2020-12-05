import random
import nekos

import discord
from discord.ext import commands


class Fun(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(
		aliases=["quote", ],
		help="Shows a random llama quote.",
		usage="> {prefix}{command}"
	)
	async def llama(self, ctx):
		# the reason why I don't use random.choice is because it may give two of the same result consecutively.
		await ctx.send(embed=discord.Embed(title="Llama quote that'll make your day", description=self.bot.quote))

	@commands.command(
		help="""Detects user's penis length.
This is 101% accurate.""",
		usage="""> {prefix}{command} *<user>
ex:
> {prefix}{command} <@501277805540147220> <@641574882382970891>"""
	)
	async def penis(self, ctx, *users: discord.Member):
		dongs = {}
		msg = ""
		state = random.getstate()

		for user in users:
			random.seed(user.id)
			dongs[user] = "8{}D".format("=" * random.randint(0, 30))

		if not users:
			random.seed(ctx.author.id)
			dongs[ctx.author] = "8{}D".format("=" * random.randint(0, 30))

		random.setstate(state)
		dongs = sorted(dongs.items(), key=lambda x: x[1])

		for user, dong in dongs:
			msg += "**{}'s size:**\n{}\n".format(user.mention, dong)

		await ctx.send(msg)

	@commands.command(
		help="Owoifies your message. OwO",
		usage="""> {prefix}{command} <text>
ex:
> {prefix}{command} hello there my old friend"""

	)
	async def owo(self, ctx, *text):
		await ctx.send(nekos.owoify(" ".join(text)))

	@commands.command(
		help="Shows image matching search term",
		usage="""> {prefix}{command} <target>
Can chose from:
**NSFW**:
`feet`, `yuri`, `trap`, `futanari`, `hololewd`, `lewdkemo`, `solog`, `feetg`, `cum`, `erokemo`, `les`, `wallpaper`, `lewdk`, `tickle`, `lewd`, `eroyuri`, `eron`, `cum_jpg`, `bj`, 'nsfw_neko_gif', `solo`, `kemonomimi`, `nsfw_avatar`, `gasm`, `anal`, `hentai`, `avatar`, `erofeet`, `holo`, `keta`, `blowjob`, `pussy`, `tits`, `holoero`, `pussy_jpg`, `pwankg`, `classic`, `kuni`, `kiss`, `femdom`, `neko`, `spank`, `erok`, `boobs`, `random_hentai_gif`, `smallboobs`, `ero`
**non NSFW**:
`feed`, `gecg`, `poke`, `slap`, `lizard`, `waifu`, `pat`, `8ball`, `cuddle`, `fox_girl`, `hug`, `smug`, `goose`, `baka`, `woof`

ex:
> {prefix}{command} neko"""
	)
	async def img(self, ctx, target: str):
		non_nsfw = [
			"feed", "gecg", "poke", "slap", "lizard", "waifu", "pat", "8ball", "cuddle", "fox_girl", "hug", "smug",
			"goose", "baka", "woof"
		]
		nsfw = [
			"feet", "yuri", "trap", "futanari", "hololewd", "lewdkemo", "solog", "feetg",
			"cum", "erokemo", "les", "wallpaper", "lewdk", "tickle", "lewd", "eroyuri", "eron",
			"cum_jpg", "bj", 'nsfw_neko_gif', "solo", "kemonomimi", "nsfw_avatar", "gasm", "anal",
			"hentai", "avatar", "erofeet", "holo", "keta", "blowjob", "pussy", "tits", "holoero", "pussy_jpg",
			"pwankg", "classic", "kuni", "kiss", "femdom", "neko", "spank", "erok", "boobs", "random_hentai_gif",
			"smallboobs", "ero"
		]
		in_nsfw = target in nsfw
		in_non_nsfw = target in non_nsfw
		if not (in_nsfw or in_non_nsfw):
			await ctx.send(
				embed=
				discord.Embed(
					title="Oops",
					description="Image category you're looking for doesn't exist. Here's all we got:"
				)
				.add_field(name="NSFW", value=f"`{'`, `'.join(nsfw)}`", inline=False)
				.add_field(name="non NSFW", value=f"`{'`, `'.join(non_nsfw)}`", inline=False)
			)
			return

		if in_nsfw and not ctx.message.channel.is_nsfw():
			await ctx.send(embed=discord.Embed(title=":lock: This command is not available in non NSFW channel"))
			return

		image_url = nekos.img(target.lower())
		await ctx.send(
			embed=
			discord.Embed(
				title="Image",
				description=f"requested by: {ctx.message.author.mention}\n**[Link if you don't see the image]({image_url})**"
			)
			.set_image(url=image_url)
			.set_footer(text=f"powered by nekos.life")
		)

	@commands.command(
		help="Shows you useless fact.",
		usage="> {prefix}{command}"
	)
	async def fact(self, ctx):
		await ctx.send(embed=discord.Embed(title="Fact of the day", description=nekos.fact()))


def setup(bot):
	bot.add_cog(Fun(bot))
