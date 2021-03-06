import datetime
import os
import random
import traceback

import asyncio
import discord
from discord.ext import commands
from discord import TextChannel


import utils.json_loader

class Config(commands.Cog):
    """Server configuration commands."""
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    @commands.command(
        name="prefix",
        aliases=["changeprefix", "setprefix"],
        description="Change your guilds prefix!",
        usage="[prefix]",
    )
    @commands.has_guild_permissions(manage_guild=True)
    async def prefix(self, ctx, *, prefix="py."):
        """Change your guild prefix"""
        await self.bot.config.upsert({"_id": ctx.guild.id, "prefix": prefix})
        await ctx.send(
            f"The guild prefix has been set to `{prefix}`. Use `{prefix}prefix [prefix]` to change it again!"
        )

    @commands.command(
        name="deleteprefix", aliases=["dp"], description="Delete your guilds prefix!"
    )
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def deleteprefix(self, ctx):
        """Delete the current guild prefix"""
        await self.bot.config.unset({"_id": ctx.guild.id, "prefix": 1})
        await ctx.send("This guilds prefix has been set back to the default")


    @commands.command(
        name="blacklist", description="Blacklist a user from the bot", usage="<user>"
    )
    @commands.is_owner()
    async def blacklist(self, ctx, user: discord.Member):
        if ctx.message.author.id == user.id:
            await ctx.send("Hey, you cannot blacklist yourself!")
            return

        self.bot.blacklisted_users.append(user.id)
        data = utils.json_loader.read_json("blacklist")
        data["blacklistedUsers"].append(user.id)
        utils.json_loader.write_json(data, "blacklist")
        await ctx.send(f"Hey, I have blacklisted {user.name} for you.")

    @commands.command(
        name="unblacklist",
        description="Unblacklist a user from the bot",
        usage="<user>",
    )
    @commands.is_owner()
    async def unblacklist(self, ctx, user: discord.Member):
        """
        Unblacklist someone from the bot
        """
        self.bot.blacklisted_users.remove(user.id)
        data = utils.json_loader.read_json("blacklist")
        data["blacklistedUsers"].remove(user.id)
        utils.json_loader.write_json(data, "blacklist")
        await ctx.send(f"Hey, I have unblacklisted {user.name} for you.")

    @commands.command(
        name="logout",
        aliases=["disconnect", "close", "stopbot"],
        description="Log the bot out of discord!",
    )
    @commands.is_owner()
    async def logout(self, ctx):
        await ctx.send(f"Hey {ctx.author.mention}, I am now logging out :wave:")
        await self.bot.logout()


    @commands.command(aliases=["sc"])
    @commands.has_guild_permissions(manage_channels=True)
    async def setsuggestionchannel(self, ctx, channel: discord.TextChannel):
        guild_ID = ctx.guild.id
        data = utils.json_loader.read_json("suggestionc")
        data[str(guild_ID)] = {"suggestionC": None, "ownerID": None}
        utils.json_loader.write_json(data, "suggestionc")
        await ctx.send("Guild ID stored successfully")
        data = utils.json_loader.read_json("suggestionc")
        data[str(ctx.guild.id)]["ownerID"] = ctx.guild.owner.id
        data[str(ctx.guild.id)]["suggestionC"] = channel.id
        utils.json_loader.write_json(data, "suggestionc")
        await ctx.send("Suggestions channel setup successfully")



    @commands.command(aliases=["sg"])
    async def suggest(self, ctx, *, message):
        data = utils.json_loader.read_json("suggestionc")
        guild_ID = ctx.guild.id
        suggestions = self.bot.get_channel(data[str(guild_ID)]["suggestionC"])
        await ctx.message.delete()
        await ctx.send("Suggestion sent.")  
        embed = discord.Embed(title='Suggestion', description=f'Suggested by: {ctx.author.mention}', color=discord.Color.dark_purple())
        embed.set_author(name=f"{ctx.author}", icon_url=f"{ctx.author.avatar_url}")
        embed.add_field(name="Suggestion:", value=str(message))
        embed.timestamp = datetime.datetime.utcnow()
        embed.set_footer(text="Vote for this suggestion!")
        poo = await suggestions.send(embed=embed)
        await poo.add_reaction("☑️")
        await poo.add_reaction("✖️")

    @suggest.error
    async def suggest_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(description='❌ Please make sure to include your suggestion:\n```!suggest <suggestion>```', color=discord.Color.dark_red())
            embed.set_author(name=f"{ctx.author}", icon_url=f"{ctx.author.avatar_url}")
            await ctx.channel.send(embed=embed)

def setup(bot):
    bot.add_cog(Config(bot))