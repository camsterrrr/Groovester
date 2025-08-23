"""
`   Author: Cameron Oakley (Camsterrr)
    Date: Aug 2025
    Description: This file is a test cog which allows us to seperate the
        application logic. Most of the skeleton was provided by Discord.py
        documentation. Follow link for official documentation:
"""

import logging as log

import discord
from discord import app_commands
from discord.ext import commands


log.getLogger(__name__)


class TestCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        """
        TestCog constructor, links the bot object to the class instance.
        """
        self.bot = bot

        return

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """
        This event listener indicates when the cog has been loaded. Really
            just used for logging purposes and is optional.
        """
        log.debug("Successfully loaded the `TestCog` command cog!")

        return

    # @app_commands.command(name="test_cog", description="Test that cog was loaded as intended.")
    # async def test_cog(self, interaction: discord.Interaction) -> None:
    @commands.command()
    async def test_cog(self, ctx: commands.Context) -> None:
        """
        This command tests that the cog successfully synced with the application.
        """
        # await interaction.response.send_message("Testing cog loaded successfully!")
        try:
            await ctx.send("Cog test message! 😉")
            log.debug("Groovester sucessfully responded to test_cog.")

        except discord.HTTPException as http_err:
            log.error(
                f"Network error encountered when attempting to send a message: {http_err}"
            )

        except discord.Forbidden as f_err:
            log.error(
                f"Groovester does not have appropriate permissions to respond in channel: {f_err}"
            )

        except Exception as err:
            log.error(f"General exception caught unexpectedly: {err}")

        return

    @commands.command()
    async def connected(self, ctx: commands.Context) -> None:
        print(f"Groovester is coconnected to a voice channel: {is_connected(ctx)}")

        return

# import os
# from dotenv import load_dotenv

# load_dotenv()
# guild_id = discord.Object(
#     id=int(os.getenv("guild_id"))
# )  # Unique identifier of the server.

# async def setup(bot: commands.Bot) -> None:
#     await bot.add_cog(Hello(bot), guilds=[discord.Object(id=guild_id)])

#     return
