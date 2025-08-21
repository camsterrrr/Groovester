import discord
from discord import app_commands
from discord.ext import commands

class Hello(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_ready(self) -> None:
        log.debug("Successfully loaded the `clear` command cog!")
        
    @app_commands.command(name="helloo", description="say hello", guild=guild_id)
    async def hello(interaction: discord.Interaction) -> None:
        await interaction.response.send_message("Hellow cog!")
        
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Hello(bot), guilds=[discord.Object(id="984963250238140426")])