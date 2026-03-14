import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from random import choice, randint
import asyncio

load_dotenv()

# Define the bot's command prefix and intents
intents = discord.Intents.default()
intents.message_content = True  # Enable the message content intent
bot = commands.Bot(command_prefix='!', intents=intents)

# Event handler for when the bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')

# Command handler for the 'ping' command
@bot.command()
async def ping(ctx):
    """Responds with 'Pong!' and the bot's latency."""
    latency = round(bot.latency * 1000) # Latency in milliseconds
    await ctx.send(f'Pong! {latency}ms')

@bot.command()
async def slots(ctx, member:discord.Member):
    await ctx.send(f"{member.mention} has been chosen for Slots!\nThree hits in a row and they survive!")

    determined_range = 5
    selected_number = randint(0,determined_range)
    hits = 0
    for _ in range(3):
        random_number = randint(0, determined_range)
        if random_number == selected_number:
            hits+=1
            await ctx.send(f"HIT! :dart:")
        else:
            await ctx.send(f"MISS! :cry:")

    if hits == 3:
        await ctx.send(f"{member.mention} has survied! :fireworks:")
    else:
        await ctx.send(f"{member.mention} lost the gamble! :skull:")
        try:
            await member.ban(reason="Slots")
        except Exception as e:
            print("Error!", e)

@bot.command()
async def blackjack(ctx, member:discord.Member):
    dealers_count = 0
    players_count = 0
    cards = [0,1,2,3,4,5,6,7,8,9,10,11,12,13] # 0 = Ace, 11 = Jack, 12 = Queen, 13 = King
    diamond = ":large_blue_diamond:"
    heart = ":heart:"
    spade = ":spades:"
    club = ":clubs:"
    suits = [diamond, heart, spade, club]

    await ctx.send(f"{member.mention} has been chosen for BlackJack!\nBeat the dealer to win! :partying_face:")
    
    # inital dealing
    players_count += choice(cards)
    dealers_count += choice(cards)
    players_count += choice(cards)
    
    while 1:
        await ctx.send(f"Player has {str(players_count)}")
        await ctx.send(f"Dealer has {str(dealers_count)}")

        await ctx.send(f"{member.mention} would you like to hit or stay?")
        try:
            message = await bot.wait_for("message", timeout=60.0)
            if message.content == "hit":
                players_count += choice(cards)
                if players_count > 21:
                    await ctx.send(f"Player has {str(players_count)}")
                    await ctx.send("Player has bust!")
                    break
            elif message.content == "stay":
                break
        except asyncio.TimeoutError:
            await ctx.send(f"{member.mention} has failed to reply!")
            await member.ban(reason="Blackjack timeout")
    
    if players_count < 22:
        while dealers_count < 17:
            dealers_count += choice(cards)
            await ctx.send(f"Dealer has {str(dealers_count)}")
        if dealers_count > 21:
            await ctx.send("Dealer busts Player wins!")
        elif dealers_count > players_count:
            await ctx.send("Dealer wins!")
        elif dealers_count < players_count:
            await ctx.send("Player wins!")
        else:
            await ctx.send("Draw")


# Run the bot with your token
bot.run(os.getenv("DISCORD_TOKEN"))

