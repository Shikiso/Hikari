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

class Player:
    def __init__(self):
        self.cards = []
        self.count = 0

    def deal_card(self, card): # [1] = num, [0] = suit
        self.cards.append(card)
        if card[1] > 10: # if card is a picture card set the value back to 10
            self.count += 10
        else:
            self.count += card[1]
    
    def check_cards(self):
        # Check for blackjack
        if self.cards[0][1] > 10 and self.cards[1][1] == 1 or self.cards[1][1] > 10 and self.cards[0][1] == 1:
            return 1
        
        # Check if player went over 21
        if self.count > 21:
            return 2

        return 0

    def get_cards_string(self):
        text = ""
        temp = ""

        for card in self.cards:
            if card[1] == 1:
                temp = f"A{card[0]} "
            elif card[1] == 11:
                temp = f"J{card[0]} "
            elif card[1] == 12:
                temp = f"Q{card[0]} "
            elif card[1] == 13:
                temp = f"K{card[0]} "
            else:
                temp = f"{str(card[1])}{card[0]} "
            text += temp
        return text

async def ban(member):
        try:
            await member.ban(reason="BlackJack")
        except Exception as e:
            print("Error!", e)

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
    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel

    player = Player()
    dealer = Player()

    cards = [1,2,3,4,5,6,7,8,9,10,11,12,13] # 0 = Ace, 11 = Jack, 12 = Queen, 13 = King
    diamond = ":large_blue_diamond:"
    heart = ":heart:"
    spade = ":spades:"
    club = ":clubs:"
    suits = [diamond, heart, spade, club]

    await ctx.send(f"{member.mention} has been chosen for BlackJack!\nBeat the dealer to win! :partying_face:")
    
    # inital dealing
    player.deal_card((choice(suits), choice(cards)))
    dealer.deal_card((choice(suits), choice(cards)))
    player.deal_card((choice(suits), choice(cards)))

    if player.check_cards() == 1:
        await ctx.send("Player has BlackJack!")
        dealer.deal_card((choice(suits), choice(cards)))
        if dealer.check_cards() == 1:
            await ctx.send("Dealer also has BlackJack!\nNo one wins ;(")
        else:
            await ctx.send("Player wins!")
     
    # Game loop
    while 1:
        await ctx.send(f"Dealer has {str(dealer.count)} ({dealer.get_cards_string()})")
        await ctx.send(f"Player has {str(player.count)} ({player.get_cards_string()})")
        if player.count == 21:
            break
        await ctx.send(f"{member.mention} would you like to hit or stay?")

        try:
            message = await bot.wait_for("message", check=check, timeout=60.0)
            if message.content.lower() == "hit":
                player.deal_card((choice(suits), choice(cards)))
                if player.check_cards() == 2:
                    await ctx.send("Player has bust! Later nerd...")
                    await ban(member)
                    break

            elif message.content.lower() == "stay":
                break

        except asyncio.TimeoutError:
            await ctx.send(f"{member.mention} has failed to reply!")
            await ban(member)
    
    if player.count < 22:
        while dealer.count < 17:
            dealer.deal_card((choice(suits), choice(cards)))

        await ctx.send(f"Dealer has {str(dealer.count)} ({dealer.get_cards_string()})")
        if dealer.check_cards() == 2:
            await ctx.send("Dealer has bust! Player wins!")
        elif dealer.count > player.count:
            await ctx.send("Dealer beats player! Loser get banned")
            await ban(member)
        else:
            await ctx.send("Player has won!")


# Run the bot with your token
bot.run(os.getenv("DISCORD_TOKEN"))

