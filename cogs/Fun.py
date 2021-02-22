import os
import nekos
import random
import os.path
import requests
from PIL import Image, ImageDraw
from io import BytesIO

import discord
from discord.ext import commands


def crop_circle(pil_img: Image.Image):
	# I can't get transparent background to work

	# crop center square
	new_size = min(pil_img.size)
	img_width, img_height = pil_img.size
	pil_img = pil_img.crop((
		(img_width - new_size) // 2,
		(img_height - new_size) // 2,
		(img_width + new_size) // 2,
		(img_height + new_size) // 2
	))

	# create circle mask
	mask = Image.new("L", pil_img.size)
	draw = ImageDraw.Draw(mask)
	draw.ellipse(
		(
			0,
			0,
			pil_img.width,
			pil_img.height
		),
		fill=255
	)
	pil_img.putalpha(mask)

	# resize and return
	final_size = 160
	return pil_img.resize((final_size, final_size))


class Fun(commands.Cog):
	# todo: cum command
	# 	https://discord.com/channels/457373827073048604/764013857634516992/801661523721977866
	# todo: touch command
	# 	https://discord.com/channels/457373827073048604/764013857634516992/783877444549345302
	# 	https://discord.com/channels/457373827073048604/764013857634516992/783877453855588423
	# todo: gang <cri> <njoi>* command

	def __init__(self, bot):
		self.bot = bot

		self.quotes = self.bot.VARS["settings"]["quotes"]
		random.shuffle(self.quotes)
		self.quote_index = 0

		self.fuck_template_image: Image.Image = Image.open(os.path.abspath("res/fuck.png"))
		self.fuck_hair_template_image: Image.Image = Image.open(os.path.abspath("res/fuck_hair.png"))

	@commands.command(
		aliases=["quote", ],
		help="Shows a random llama quote.",
	)
	async def llama(self, ctx):
		# the reason why I don't use random.choice is because it may give two of the same result consecutively.
		quote = self.quotes[self.quote_index]
		await ctx.send(embed=discord.Embed(title="Llama quote that'll make your day", description=quote))

		self.quote_index += 1  # get next quote next time this command is called
		if self.quote_index > (len(self.quotes) - 1):  # reshuffle and reset index
			random.shuffle(self.quotes)
			self.quote_index = 0

	@commands.command(
		aliases=["pp", ],
		help="""Detects user's penis length and arranges them from largest to smallest.
This is 101% accurate.""",
		usage="""> {prefix}{command} *<user>
ex:
Show penis length of <@501277805540147220> and <@641574882382970891>
> {prefix}{command} <@501277805540147220> <@641574882382970891>
"""
	)
	async def penis(self, ctx, *users: discord.Member):
		dongs = {}
		msg = ""
		state = random.getstate()

		for user in users:
			random.seed(user.id)
			random_size = random.randint(0, 30)
			dongs[user] = ["8{}D".format("=" * random_size), random_size]

		if not users:
			random.seed(ctx.author.id)
			random_size = random.randint(0, 30)
			dongs[ctx.author] = ["8{}D".format("=" * random_size), random_size]

		random.setstate(state)
		dongs = sorted(dongs.items(), key=lambda x: x[1][1])

		for user, dong in dongs:
			msg += "**%s's size: ( %s )**\n%s\n" % (user.mention, dong[1], dong[0])

		await ctx.send(embed=discord.Embed(
			title="Here's your pp list",
			description=msg
		))

	@commands.command(
		help="Shows an image of someone getting fucked",
		usage="""> {prefix}{command} <user>

user can be a discord ID or a mention (ping)."""
	)
	@commands.is_nsfw()
	async def fuck(self, ctx: discord.ext.commands.Context, victim: discord.Member):
		# todo: says fuck you <user mention>
		# todo: furry image for furry role
		# 	https://discord.com/channels/457373827073048604/764013857634516992/783869713737711666
		# 	https://discord.com/channels/457373827073048604/764013857634516992/783877435758215169
		image = self.fuck_template_image.copy()
		image.alpha_composite(
			crop_circle(Image.open(BytesIO(requests.get(victim.avatar_url).content))),
			(320, 170)
		)
		image.alpha_composite(self.fuck_hair_template_image)

		with BytesIO() as img_byte_arr:
			image.save(img_byte_arr, format="PNG", quality=100)
			img_byte_arr.seek(0)

			await ctx.send(
				file=discord.File(
					fp=img_byte_arr,
					filename=f"fuck_{ctx.author.id}_{victim.id}.png"
				),
				embed=discord.Embed(
					title="F U C K",
					description=f"fucking {victim.mention}"
				)
			)

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
				embed=discord.Embed(
					title="Oops",
					description="Image category you're looking for doesn't exist. Here's all we got:"
				)
				.add_field(name="NSFW", value=f"`{'`, `'.join(nsfw)}`", inline=False)
				.add_field(name="non NSFW", value=f"`{'`, `'.join(non_nsfw)}`", inline=False)
			)
			return

		if in_nsfw and not ctx.message.channel.is_nsfw():
			raise discord.ext.commands.errors.NSFWChannelRequired

		image_url = nekos.img(target.lower())
		await ctx.send(
			embed=discord.Embed(
				title="Image",
				description=f"requested by: {ctx.message.author.mention}\n**[Link if you don't see the image]({image_url})**"
			)
			.set_image(url=image_url)
			.set_footer(text=f"powered by nekos.life")
		)

	@commands.command(
		help="Shows useless facts.",
	)
	async def fact(self, ctx):
		await ctx.send(embed=discord.Embed(title="Fact of the day", description=nekos.fact()))


def setup(bot):
	bot.add_cog(Fun(bot))
