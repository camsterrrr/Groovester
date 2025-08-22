"""
Sample cog provided by Discord.py documentation.
"""

import logging as log
import os

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv


load_dotenv()
guild_id = discord.Object(id=int(os.getenv("guild_id"))) # Unique identifier of the server.

log.getLogger(__name__)


class TestCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        """
        """
        self.bot = bot
        
        return


    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """
        
        """
        log.debug("Successfully loaded the `Test` command cog!")
        
        return


    # @app_commands.command(name="test_cog", description="Test that cog was loaded as intended.")
    # async def test_cog(self, interaction: discord.Interaction) -> None:
    @commands.command()
    async def test_cog(self, ctx: commands.Context) -> None:
        """
        
        """
        # await interaction.response.send_message("Testing cog loaded successfully!")
        await ctx.send("Testing cog loaded successfully!")
        
        return


# async def setup(bot: commands.Bot) -> None:
#     await bot.add_cog(Hello(bot), guilds=[discord.Object(id=guild_id)])
    
#     return