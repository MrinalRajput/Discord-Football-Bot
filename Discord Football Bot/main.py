
import random
import discord
from discord.ext import commands
from discord.ui import Button ,View
from datetime import datetime
import asyncio

from discord.member import Member

with open("config.json", "r") as f:
    config = eval(f.read())

DEFAULT_PREFIX = config["prefix"]
Token = config["token"]

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix=DEFAULT_PREFIX, case_insensitive=True, intents=intents, help_command=None)

@bot.event
async def on_ready():
    print("I am Ready!")
    await bot.tree.sync()
    print("Synced")


@bot.hybrid_command(name="penalty", with_app_command=True, description="Start the Penalty Football Game")
async def penalty(ctx):
    participants = []
    players = { }

    gameRound = 0
    for rounds in range(4):
        gameRound+=1
        timeRemain = 20

        botChoice = random.choice(["p1", "p2", "p3", "p4", "p5", "p6"])
        print(f"Bot Chose: {botChoice}")

        Buttons = []
        for i in range(6):
            Buttons.append(Button(label=f"P{i+1}", custom_id=f"p{i+1}"))

        async def shoot_callback(interaction: discord.Interaction):
            btn_id = interaction.data["custom_id"]

            if gameRound==1:
                if interaction.user.id not in players.keys() and interaction.user.id not in participants:
                    participants.append(interaction.user.id)
                    players[interaction.user.id] = "none"
                                 
            else:
                if interaction.user.id not in participants:
                    await interaction.response.send_message(f"You cannot Join in the Middle of the Game!", ephemeral=True)
                elif interaction.user.id not in players.keys() and interaction.user.id in participants:
                    await interaction.response.send_message("You Already Lose this Game!", ephemeral=True)
                
            if interaction.user.id in players.keys():
                if players[interaction.user.id] == "none":
                    await interaction.response.send_message(f"{interaction.user.name} Chose {btn_id}", ephemeral=True)
                    players[interaction.user.id] = btn_id
                else:
                    await interaction.response.send_message(f"You have already chose one of them!", ephemeral=True)

            print(participants)
            print(players)
            

        # you can make 2 buttons for lock/unlock channel and if u want to send embeds or send messages from buttons just type : interaction.response.send_message(the message with "")
    
        view = View()

        for btn in Buttons:
            btn.callback = shoot_callback
            view.add_item(btn)

        file = discord.File("images/main.png", filename="main.png")
        gameEmbed = discord.Embed(title=f"Penalties - Round {gameRound} Begins", description=f"Round {gameRound} \n Players: `{len(list(players.keys()))}`\n Time Remaining: `{timeRemain}` Seconds", color=discord.Color.green())
        gameEmbed.set_image(url="attachment://main.png")
        gamemsg = await ctx.send(embed=gameEmbed, file=file, view=view)
        for k in range(20):
            await asyncio.sleep(1)
            timeRemain-=1
            gameEmbed.description = f"Round {gameRound} \n Players: `{len(list(players.keys()))}`\n Time Remaining: `{timeRemain}` Seconds"
            await gamemsg.edit(embed=gameEmbed)
        else:
            gameEmbed.description = f"Round {gameRound} \n Players: `{len(list(players.keys()))}`\n Time Remaining: `Over`"
            await gamemsg.edit(embed=gameEmbed)
        
        roundLosers = []
        currentPlayers = len(players.keys())
        for plays in list(players.keys()):
            print(list(players.keys()))
            if players[plays] == botChoice or players[plays] == "none":
                
                roundLosers.append(bot.get_user(plays).name)
                del players[plays]
                print("One Player Out!")
            else:
                players[plays] = "none"

        if len(roundLosers) != 0:
            roundLosers = ", ".join(roundLosers)
        else:
            roundLosers = "No One"
        roundEmbed = discord.Embed(title=f"Penalties - Round {gameRound} Over", description=f"Players Left: `{len(players.keys())}`\nRound Losers: {roundLosers}", color=discord.Color.red())
        file = discord.File(f"images/{botChoice.upper()}.png", filename=f"{botChoice.upper()}.png")
        roundEmbed.set_image(url=f"attachment://{botChoice.upper()}.png")
        roundEmbed.set_footer(text=f"The GoalKeeper Dodged towards {botChoice.upper()} Side")
        await ctx.send(embed=roundEmbed, file=file)
        if len(list(players.keys())) == 0:
            await ctx.send("No more Players Left!")
            return
        elif len(list(players.keys())) == 1:
            await ctx.send(f"{bot.get_user(list(players.keys())[0]).name} is the Only Winner!")
            return
        else:
            await asyncio.sleep(2)

        # await ctx.send("```Round Losers: '\n'.join()```")
    gameWinners = []
    for plays in players.keys():
        gameWinners.append(bot.get_user(plays).name)
    players = "\n".join(gameWinners)
    await ctx.send(f"The Game Winners are:\n```\n{players}```")

@bot.hybrid_command(name="help", with_app_command=True, description="Get help!")
async def help(ctx):
    helpEmbed = discord.Embed(title="Help", color=discord.Color.green())
    helpEmbed.add_field(name="Commands", value=f"{', '.join(bot.all_commands)}", inline=False)
    helpEmbed.set_footer(icon_url=ctx.author.display_avatar.url, text=f"Requested by {ctx.author.name}")

    await ctx.reply(embed=helpEmbed)

bot.run(Token)