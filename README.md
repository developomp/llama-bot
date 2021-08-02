# [llama bot](https://github.com/developomp/llama-bot)

<div align="center">
   <a href="https://opensource.org/licenses/MIT"><img alt="MIT License" src="https://img.shields.io/github/license/developomp/llama-bot?style=flat-square" /></a>
   <a href="https://www.python.org/downloads/release/python-395"><img alt="Python version 3.9" src="https://img.shields.io/badge/python-3.9-blue?style=flat-square" /></a>
   <a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code style-black-000000.svg?style=flat-square"></a>
   <br />
   <br />
   <img alt="llama logo" src=".github/logo.png" />
</div>

> **WARNING: THIS REPOSITORY CONTAINS NSFW CONTENT**

llama bot is a [discord](https://discord.com) bot made for the LP community [server](https://discord.gg/2fsar34APa).<br />

- Invitation of this bot to other server is blocked. You wll have to host the bot yourself if you want it on your discord server.
- The bot requires Python version 3.9 or greater.
- local configuration file and database does not exist. Everything is stored in google firebase. Portability ftw!

Example:
![example image of bot usage](.github/example.png)

# Setting up locally

Steps:

1. Clone this repository
   - `git clone https://github.com/developomp/llama-bot.git`
2. Install dependencies ([requirements.txt](./requirements.txt) is in project root)

   - `pip install -r requirements.txt`

3. create `secrets` directory under `bot` directory
4. Create a new discord bot
   - https://discord.com/developers/applications
5. Create a firebase project and create firestore database (production mode is highly recommended)
   - https://console.firebase.google.com
6. Generate and download service account key from firebase ([instruction](https://firebase.google.com/docs/admin/setup#initialize-sdk)), rename it to `firebase-adminsdk.json`, and put it in `secrets` directory.
   - https://console.firebase.google.com/project/_/settings/serviceaccounts/adminsdk
7. create `secret.json` in `secrets` directory and put the discord bot token
   ```json
   {
     "token": "<TOKEN>"
   }
   ```
8. Start the bot (working directory must be set to `bot` directory)

   - `python llama.py`

More info:

- discord developers documentation: https://discord.com/developers/docs
- [discord python API](https://github.com/Rapptz/discord.py) documentation: https://discordpy.readthedocs.io
- firebase admin sdk documentation: https://firebase.google.com/docs

# contributing

- Usage of [vscode](https://code.visualstudio.com) is highly recommended
- Format python code using the [black](https://github.com/psf/black) formatter
- Format markdown file(s) with [prettier](https://prettier.io) formatter

# Special thanks

- `Davidisacookie#9888 (265697563280146433)` for making the bot icon
