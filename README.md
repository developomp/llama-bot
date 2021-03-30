# llama bot

[![License](https://img.shields.io/github/license/developomp/llama-bot?style=flat-square)](https://opensource.org/licenses/MIT)

![llama logo](logo.png)

> **WARNING: THIS REPOSITORY CONTAINS NSFW CONTENT**

This repository contains source code for the llama bot.
A general purpose, open source discord bot.

- Discord bot made for [one specific server](https://dsc.gg/llama). It will be open to the public when it becomes mature enough.
- Invitation of this bot to other server is blocked as of the moment. You'll have to host the bot yourself if you want it on your discord server.
- It was not originally designed with ease of use for others in mind. Documentations will come soon.
- The bot is still under construction, so you may find a ton of inconsistencies and missing features. Feel free to create a github issue.
- WarBrokers feature is completely unavailable for the public, and it wil stay that way.
- The bot requires Python version 3.9 or greater.
- local configuration file and database does not exist. Everything is stored in firebase as of the moment.

![example](example.png)

# Usage (for server admins)

The bot is not ready for multiple servers. Invitation will be enabled when it's ready. Documentations will be made too.

# Setting up locally (for developers)

Required knowledge:

- python
- firebase
- discord bots
- linux

Steps:

> assumes you already know how to use firebase, python, and discord bots

1. Clone this repo
   - `git clone --depth 1 https://github.com/developomp/llama-bot.git` (`--depth 1` is to save storage space)
2. create `secrets` directory in the cloned directory
3. Create a new discord bot
   - https://discord.com/developers/applications
4. Create a firebase project and enable firestore database
   - https://console.firebase.google.com
5. Generate and download service account key from firebase, rename it to `firebase-adminsdk.json`, and put it in `secrets` directory.
   - https://console.firebase.google.com/project/_/settings/serviceaccounts/adminsdk
6. create `secret.json` in `secrets` directory and put your bot token
   ```json
   {
     "token": "<TOKEN>"
   }
   ```
7. Install dependencies

   - `pip install -r requirements.txt`

8. Start the bot
   - `python llama.py`

More info:

- discord developers documentation: https://discord.com/developers/docs
- [discord.py](https://github.com/Rapptz/discord.py) documentation: https://discordpy.readthedocs.io
- firebase admin sdk documentation: https://firebase.google.com/docs/admin/setup#initialize-sdk

# contributing

To make sure that the code style is consistent throughout the project, we use code formatters. Pull requests that are not formatted correctly will not be accepted.

> Usage of [vscode](https://code.visualstudio.com) is highly recommended

- Python: [black](https://github.com/psf/black)
- markdown: [prettier](https://prettier.io)

P.S. Black code formatter does not support tab indentation btw

# Special thanks

- `Davidisacookie#9888 (265697563280146433)` for making the bot avatar

# Contacting

Feel free:

- To submit an issue in the [github issue page](https://github.com/developomp/llama-bot/issues)
- To DM me in [discord](https://discord.com) (developomp#0001)
- To send an email (developomp@gmail.com)

Any feedback is welcomed.
