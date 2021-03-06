import discord
from discord.ext import commands
import json
from discord.ext.commands.cooldowns import BucketType
import random

cards = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]


class Blackjack(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.info = {}  # {"player_id": {"player_hand": [card1, card2], "dealer_hand": [card1, card2], "bet": bet}

    def deal(self, id, person):
        person = f"{person}_hand"
        self.info[str(id)][person] = [random.choice(cards), random.choice(cards)]
        return self.info[str(id)][person]

    def hitHand(self, id, person):
        person = f"{person}_hand"
        self.info[str(id)][person].append(random.choice(cards))
        return self.info[str(id)][person]

    def total(self, hand):
        value = 0
        for card in hand:
            if card.isnumeric():
                value += int(card)
            elif card in ["J", "Q", "K"]:
                value += 10
            elif card == "A":
                if value < 11:
                    value += 11
                else:
                    value += 1
        return value

    async def blackJackCheck(self, ctx):
        playerHand, dealerHand = self.info[str(ctx.author.id)]["player_hand"], self.info[str(ctx.author.id)]["dealer_hand"]
        if self.total(playerHand) == 21 or self.total(dealerHand) == 21:
            playerDisplayHand = "".join(f"`{i}` " for i in playerHand)
            dealerDisplayHand = "".join(f"`{i}` " for i in dealerHand)
            embed = discord.Embed(title=f"{ctx.author.display_name}'s blackjack game:")
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            embed.add_field(name=f"**{ctx.author.display_name}**:\nCards ==> {playerDisplayHand}",
                            value=f"Total ==> `{self.total(playerHand)}`", inline=True)
            embed.add_field(name=f"**Hurb**:\nCards ==> {dealerDisplayHand}",
                            value=f"Total ==> `{self.total(dealerHand)}`", inline=True)
            if self.total(playerHand) == 21:
                if self.total(dealerHand) == 21:
                    embed.add_field(name="It's a tie! You both got blackjack!", value="Your balance stayed the same.", inline=False)
                    self.info.pop(str(ctx.author.id))
                else:
                    if len(self.info[str(ctx.author.id)]["player_hand"]) == 2:
                        embed.add_field(name="You won! You got a blackjack!", value=f"You won ${int(self.info[str(ctx.author.id)]['bet']) * 1.5}!", inline=False)
                        storage = json.load(open("servers.json"))
                        players = storage["players"]
                        players[str(ctx.author.id)]['money'] += self.info[str(ctx.author.id)]['bet'] * 1.5
                        self.info.pop(str(ctx.author.id))
                    else:
                        embed.add_field(name="You won! You reached 21 before the dealer!", value=f"You won ${int(self.info[str(ctx.author.id)]['bet'])}!", inline=False)
                        storage = json.load(open("servers.json"))
                        players = storage["players"]

                        players[str(ctx.author.id)]['money'] += self.info[str(ctx.author.id)]['bet']
                        self.info.pop(str(ctx.author.id))
                    storage["players"] = players
                    json.dump(storage, open("servers.json", "w"), indent=4)
                return True

            elif self.total(dealerHand) == 21:
                embed.add_field(name="The dealer reached 21 before you did. You lost.",
                                value=f"You lost ${self.info[str(ctx.author.id)]['bet']}.",
                                inline=False)
                storage = json.load(open("servers.json"))
                players = storage["players"]
                storage["players"] = players
                json.dump(storage, open("servers.json", "w"), indent=4)
                self.info.pop(str(ctx.author.id))
                return True
            await ctx.send(embed=embed)

        else:
            return False

    async def checkBust(self, ctx):
        playerHand = self.info[str(ctx.author.id)]["player_hand"]
        dealerHand = self.info[str(ctx.author.id)]["dealer_hand"]
        if self.total(playerHand) > 21 or self.total(dealerHand) > 21:
            playerDisplayHand = ""
            for i in playerHand:
                playerDisplayHand += f"`{i}` "
            dealerDisplayHand = ""
            for i in dealerHand:
                dealerDisplayHand += f"`{i}` "
            playerTotal = self.total(playerHand)
            dealerTotal = self.total(dealerHand)
            if self.total(playerHand) > 21:
                embed = discord.Embed(title=f"{ctx.author.display_name}'s blackjack game:", color=discord.Color.red())
                embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
                embed.add_field(name=f"**{ctx.author.display_name}**:\nCards ==> {playerDisplayHand}",
                                value=f"Total ==> `{playerTotal}`", inline=True)
                embed.add_field(name=f"**Hurb**:\nCards ==> {dealerDisplayHand}",
                                value=f"Total ==> `{dealerTotal}`", inline=True)
                embed.add_field(name="You busted! You lost.",
                                value=f"You lost ${self.info[str(ctx.author.id)]['bet']}.", inline=False)
                storage = json.load(open("servers.json"))
                players = storage["players"]

                players[str(ctx.author.id)]['money'] -= int(self.info[str(ctx.author.id)]["bet"])
                storage["players"] = players
                json.dump(storage, open("servers.json", "w"), indent=4)
                await ctx.send(embed=embed)
                self.info.pop(str(ctx.author.id))
                return True

            elif self.total(dealerHand) > 21:
                embed = discord.Embed(title=f"{ctx.author.display_name}'s blackjack game:", color=discord.Color.green())
                embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
                embed.add_field(name=f"**{ctx.author.display_name}**:\nCards ==> {playerDisplayHand}",
                                value=f"Total ==> `{playerTotal}`", inline=True)
                embed.add_field(name=f"**Hurb**:\nCards ==> {dealerDisplayHand}",
                                value=f"Total ==> `{dealerTotal}`", inline=True)
                embed.add_field(name="The dealer busted! You won!",
                                value=f"You won ${self.info[str(ctx.author.id)]['bet']}.", inline=False)

                storage = json.load(open("servers.json"))
                players = storage["players"]

                players[str(ctx.author.id)]['money'] += self.info[str(ctx.author.id)]['bet']
                storage["players"] = players
                json.dump(storage, open("servers.json", "w"), indent=4)
                await ctx.send(embed=embed)
                self.info.pop(str(ctx.author.id))
                return True

        else:
            return False

    @commands.command(aliases=["h"])
    async def hit(self, ctx):
        if str(ctx.author.id) in self.info.keys():
            self.hitHand(ctx.author.id, "player")
            if not await self.blackJackCheck(ctx):
                if not await self.checkBust(ctx):
                    await self.game(ctx)
        else:
            embed = discord.Embed(title=f"You are not playing a game of blackjack, {ctx.author.display_name}!",
                                  color=discord.Color.red())
            await ctx.send(embed=embed)

    @commands.command(aliases=["s"])
    async def stand(self, ctx):
        if str(ctx.author.id) in self.info.keys():
            self.hitHand(str(ctx.author.id), "dealer")
            while self.total(self.info[str(ctx.author.id)]["dealer_hand"]) < 17:
                self.hitHand(str(ctx.author.id), "dealer")
            if not await self.checkBust(ctx):
                await self.score(ctx)
        else:
            embed = discord.Embed(title=f"You are not playing a game of blackjack, {ctx.author.display_name}!",
                                  color=discord.Color.red())
            await ctx.send(embed=embed)

    @commands.command(aliases=["dd"])
    async def doubledown(self, ctx):
        if str(ctx.author.id) in self.info.keys():
            storage = json.load(open("servers.json"))
            players = storage["players"]

            if int(self.info[str(ctx.author.id)]['bet']) * 2 > int(players[str(ctx.author.id)]['money']):
                await ctx.send(embed=discord.Embed(
                    description=f"You do not have enough money to double down {ctx.author.mention}!",
                    color=discord.Color.red()))
            else:
                self.hitHand(ctx.author.id, "player")
                self.info[str(ctx.author.id)]['bet'] = int(self.info[str(ctx.author.id)]['bet'])
                self.info[str(ctx.author.id)]['bet'] *= 2
                while self.total(self.info[str(ctx.author.id)]["dealer_hand"]) < 17:
                    self.hitHand(ctx.author.id, "dealer")
                if not await self.checkBust(ctx):
                    await self.score(ctx)
        else:
            embed = discord.Embed(title=f"You are not playing a game of blackjack, {ctx.author.display_name}!",
                                  color=discord.Color.red())
            await ctx.send(embed=embed)

    async def score(self, ctx):
        playerHand = self.info[str(ctx.author.id)]["player_hand"]
        dealerHand = self.info[str(ctx.author.id)]["dealer_hand"]
        playerDisplayHand = "".join([f"`{i}` " for i in playerHand])
        dealerDisplayHand = "".join([f"`{i}` " for i in dealerHand])
        playerTotal = self.total(playerHand)
        dealerTotal = self.total(dealerHand)
        if dealerTotal > playerTotal:
            embed = discord.Embed(title=f"{ctx.author.display_name}'s blackjack game:", color=discord.Color.red())
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            embed.add_field(name=f"**{ctx.author.display_name}**:\nCards ==> {playerDisplayHand}",
                            value=f"Total ==> `{playerTotal}`", inline=True)
            embed.add_field(name=f"**Hurb**:\nCards ==> {dealerDisplayHand}",
                            value=f"Total ==> `{dealerTotal}`", inline=True)
            embed.add_field(name="The dealer got a higher value than you. You lost.",
                            value=f"You lost ${self.info[str(ctx.author.id)]['bet']}.",
                            inline=False)
            storage = json.load(open("servers.json"))
            players = storage["players"]

            players[str(ctx.author.id)]['money'] -= self.info[str(ctx.author.id)]['bet']
            storage["players"] = players
            json.dump(storage, open("servers.json", "w"), indent=4)
            self.info.pop(str(ctx.author.id))
            await ctx.send(embed=embed)
        elif playerTotal > dealerTotal:
            embed = discord.Embed(title=f"{ctx.author.display_name}'s blackjack game:", color=discord.Color.green())
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            embed.add_field(name=f"**{ctx.author.display_name}**:\nCards ==> {playerDisplayHand}",
                            value=f"Total ==> `{playerTotal}`", inline=True)
            embed.add_field(name=f"**Hurb**:\nCards ==> {dealerDisplayHand}",
                            value=f"Total ==> `{dealerTotal}`", inline=True)
            embed.add_field(name="You won! Your score was higher than the dealer's!",
                            value=f"You won ${self.info[str(ctx.author.id)]['bet']}!",
                            inline=False)
            storage = json.load(open("servers.json"))
            players = storage["players"]

            players[str(ctx.author.id)]['money'] += self.info[str(ctx.author.id)]['bet']
            storage["players"] = players
            json.dump(storage, open("servers.json", "w"), indent=4)
            self.info.pop(str(ctx.author.id))
            await ctx.send(embed=embed)
        elif playerTotal == dealerTotal:
            embed = discord.Embed(title=f"{ctx.author.display_name}'s blackjack game:", color=discord.Color.gold())
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            embed.add_field(name=f"**{ctx.author.display_name}**:\nCards ==> {playerDisplayHand}",
                            value=f"Total ==> `{playerTotal}`", inline=True)
            embed.add_field(name=f"**Hurb**:\nCards ==> {dealerDisplayHand}",
                            value=f"Total ==> `{dealerTotal}`", inline=True)
            embed.add_field(name="It's a tie! Your score was the same as the dealer's",
                            value="Your balance stayed the same.", inline=False)
            self.info.pop(str(ctx.author.id))
            await ctx.send(embed=embed)

    async def game(self, ctx):
        playerHand = self.info[str(ctx.author.id)]["player_hand"]
        dealerHand = self.info[str(ctx.author.id)]["dealer_hand"]
        playerDisplayHand = "".join([f"`{i}` " for i in playerHand])
        dealerDisplayHand = f"`{dealerHand[0]}`"
        playerTotal = self.total(playerHand)
        embed = discord.Embed(title=f"{ctx.author.display_name}'s blackjack game:", color=discord.Color.dark_green())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        embed.add_field(name=f"**{ctx.author.display_name}**:\nCards ==> {playerDisplayHand}",
                        value=f"Total ==> `{playerTotal}`", inline=True)
        embed.add_field(name=f"**Hurb**:\nCards ==> {dealerDisplayHand}",
                        value=f"Total ==> `?`", inline=True)
        embed.set_footer(text=f"Your options are: %hit, %stand, or %doubledown.")
        await ctx.send(embed=embed)

    @commands.cooldown(1, 5, BucketType.user)
    @commands.command(aliases=["bj"])
    async def blackjack(self, ctx, bet):
        if await self.tooMuchCheck(ctx, bet):
            if str(ctx.author.id) in self.info.keys():
                embed = discord.Embed(
                    title=f"You are already playing a game of blackjack, {ctx.author.display_name}! Please don't break me :(",
                    color=discord.Color.red())
                await ctx.send(embed=embed)
            else:
                self.info[str(ctx.author.id)] = {"player_hand": [], "dealer_hand": [], "bet": int(bet)}
                self.deal(ctx.author.id, "player")
                self.deal(ctx.author.id, "dealer")

                if not await self.blackJackCheck(ctx):
                    await self.game(ctx)

    async def tooMuchCheck(self, ctx, bet: int):
        storage = json.load(open("servers"))
        players = storage["players"]

        if int(bet) > int(players[str(ctx.author.id)]['money']):
            embed = discord.Embed(title=f"Bro, don't try to bet more than you have. I don't want to break ;(")
            await ctx.send(embed=embed)
            return False
        elif int(bet) <= 0:
            embed = discord.Embed(title=f"{ctx.author.display_name}'s blackjack game:", color=discord.Color.green())
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            embed.add_field(name=f"**{ctx.author.display_name}**:\nCards ==> `A` `K`",
                            value=f"Total ==> `BLACKJACK!!!`", inline=True)
            embed.add_field(name=f"**Hurb**:\nCards ==> `2` `2`",
                            value=f"Total ==> `4`", inline=True)
            embed.add_field(name="You won! You got a BlackJack!", value=f"You won ${bet}!",
                            inline=False)
            await ctx.send(embed=embed)
            players[str(ctx.author.id)]['money'] += int(bet)
            storage["players"] = players
            json.dump(storage, open("servers", "w"), indent=4)
            return False

        else:
            return True


def setup(bot):
    bot.add_cog(Blackjack(bot))

