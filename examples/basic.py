import discord
from discord.ext import commands
from discord_components import Button, ButtonStyle

from discord_slash_components_bridge import SlashCommand

bot = commands.Bot('your prefix')
slash = SlashCommand(bot)

@slash.slash(name='button')
async def button(ctx):
    components = [
        Button(label='CLICK ME!', custom_id='button1', style=ButtonStyle.red)
    ]

    await ctx.send('Buttons!', components=components)

    interaction = await bot.wait_for('button_click')
    await interaction.send('Clicked!')

bot.run('your token')
