import os

import discord
from discord.ext import commands
from dotenv import load_dotenv


##########################################################################
###########################   CONFIGURATION   ############################
##########################################################################

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
# * Note that the command prefix was removed in recent versions. This
# *  doesn't do anything.

# * Read environment variables.
# * Guild ID represents the servers unique ID.
# * Bot token is the unique authentication token to interact with Discord
# *     API.
load_dotenv()
guild_id = discord.Object(
    id=int(os.getenv("guild_id"))
)  # Unique identifier of the server.
bot_token = os.getenv("bot_token")


##########################################################################
##############################   GETTERS   ###############################
##########################################################################

def get_bot() -> commands.Bot:
    """
    Getter that returns a reference to the bot object.
    
    Returns:
        commands.Bot:
    """
    return bot


def get_bot_token() -> int:
    """
    Getter that returns the bot token specified in the .env file.

    Returns:
        int: the bot's authentication token.
    """
    return bot_token


def get_guild_id() -> discord.Object:
    """
    Getter that returns a reference to the Guild ID specified in the .env
        file.
        
    Returns:
        discord.Object:
    """
    return guild_id
