# [llama bot](https://github.com/developomp/llama-bot)

<div align="center">
<a href="https://opensource.org/licenses/MIT"><img alt="MIT License" src="https://img.shields.io/github/license/developomp/llama-bot?style=flat-square" /></a>
<a href="https://www.python.org/downloads/release/python-395"><img alt="Python version 3.9" src="https://img.shields.io/badge/python-3.9-blue?style=flat-square" /></a>
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code style-black-000000.svg?style=flat-square"></a>
<a href="https://dsc.gg/llama"> <img alt="Discord" src="https://img.shields.io/discord/457373827073048604?style=flat-square"></a>
</div>

![llama logo](.github/logo.png)

> **WARNING: THIS REPOSITORY CONTAINS NSFW CONTENT**

This repository contains source code for the llama bot.<br />

- Discord bot made for the [LP discord server](https://dsc.gg/llama). Making it work on other servers will need some work.
- Invitation of this bot to other server is blocked due to potential server performance issue. You wll have to host the bot yourself if you want it on your discord server.
- The bot requires Python version 3.9 or greater.
- local configuration file and database does not exist. Everything is stored in google firebase.

![example image of bot usage](.github/example.png)

# Setting up locally

Required knowledge:

- python
- firebase
- discord bots

Steps:

1. Clone this repo
   - `git clone --depth 1 https://github.com/developomp/llama-bot.git` (`--depth 1` is to save storage space)
2. Open [`bot`](./bot) directory
3. create `secrets` directory
4. Create a new discord bot
   - https://discord.com/developers/applications
5. Create a firebase project and enable firestore database
   - https://console.firebase.google.com
6. Generate and download service account key from firebase, rename it to `firebase-adminsdk.json`, and put it in `secrets` directory.
   - https://console.firebase.google.com/project/_/settings/serviceaccounts/adminsdk
7. create `secret.json` in `secrets` directory and put the discord bot token
   ```json
   {
     "token": "<TOKEN>"
   }
   ```
8. Install dependencies ([requirements.txt](./requirements.txt) is in project root)

   - `pip install -r requirements.txt`

9. Start the bot

   - `python llama.py`

More info:

- discord developers documentation: https://discord.com/developers/docs
- [discord.py](https://github.com/Rapptz/discord.py) documentation: https://discordpy.readthedocs.io
- firebase admin sdk documentation: https://firebase.google.com/docs/admin/setup#initialize-sdk

# contributing

- Usage of [vscode](https://code.visualstudio.com) is highly recommended
- Format python code using the [black](https://github.com/psf/black) formatter
- Format markdown file(s) with [prettier](https://prettier.io) formatter

# Special thanks

- `Davidisacookie#9888 (265697563280146433)` for making the bot avatar

# Contacting

Feel free:

- To submit an issue in the [github issue page](https://github.com/developomp/llama-bot/issues)
- To DM me in [discord](https://discord.com) (developomp#0001, 501277805540147220)
- To send an email (developomp@gmail.com)

Any feedback is welcomed.
