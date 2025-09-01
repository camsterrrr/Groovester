

THere is a difference betweem


author is discord.member.Member type


    #! TODO: Remove because Discord.py doesn't support slash commands with
    #!  cog structure.
    # # Push offered slash commands to Discord servers.
    # try:
    #     await bot.tree.sync(guild=guild_id)
    #     log.info(f"Successfully synced the slash commands with the server!")

    # except Exception as err:
    #     log.error(
    #         f"General exception, failed to sync the slash commands with the server: {err}"
    #     )



     @app_commands.command(name="greet")
    async def greet_command(self, interaction: discord.Interaction):
        """Greets the user!"""
        await interaction.response.send_message("Hello from your bot!")
        message = await interaction.original_response()
        print(f"Interaction response message content: {message.content}")
        print(f"Interaction response message ID: {message.id}")