import datetime
import discord
import re
import time

from cogs import converters
from cogs.checks import is_staff, check_staff_id
from cogs.database import DatabaseCog
from discord.ext import commands


class KickBan(DatabaseCog):
    """
    Kicking and banning users.
    """

    async def cog_check(self, ctx):
        if ctx.guild is None:
            raise commands.NoPrivateMessage()
        return True

    async def meme(self, beaner: discord.Member, beaned: discord.Member, action: str, channel: discord.TextChannel, reason: str):
        await channel.send(f"Seriously? What makes you think it's okay to try and {action} another staff or helper like that?")
        msg = f"{beaner.mention} attempted to {action} {beaned.mention}|{beaned} in {channel.mention} "
        if reason != "":
            msg += "for the reason " + reason
        await self.bot.channels['meta'].send(msg + (" without a reason" if reason == "" else ""))

    @is_staff("HalfOP")
    @commands.command(name="kick")
    async def kick_member(self, ctx, member: converters.SafeMember, *, reason=""):
        """Kicks a user from the server. Staff only."""
        if await check_staff_id(ctx, 'Helper', member.id):
            await self.meme(ctx.author, member, "kick", ctx.channel, reason)
            return
        msg = f"You were kicked from {ctx.guild.name}."
        if reason != "":
            msg += " The given reason is: " + reason
        msg += "\n\nYou are able to rejoin the server, but please read the rules in #welcome-and-rules before participating again."
        try:
            await member.send(msg)
        except (discord.errors.Forbidden, discord.errors.HTTPException):
            pass  # don't fail in case user has DMs disabled for this server, or blocked the bot
        try:
            self.bot.actions.append("uk:" + str(member.id))
            await member.kick(reason=reason)
        except discord.errors.Forbidden:
            await ctx.send("💢 I don't have permission to do this.")
            return
        await ctx.send(f"{self.bot.help_command.remove_mentions(member.name)} is now gone. 👌")
        msg = f"👢 **Kick**: {ctx.author.mention} kicked {member.mention} | {member}\n🏷 __User ID__: {member.id}"
        if reason != "":
            msg += "\n✏️ __Reason__: " + reason
        await self.bot.channels['server-logs'].send(msg)
        await self.bot.channels['mod-logs'].send(msg + ("\nPlease add an explanation below. In the future, it is recommended to use `.kick <user> [reason]` as the reason is automatically sent to the user." if reason == "" else ""))

    @is_staff("OP")
    @commands.command(name="ban")
    async def ban_member(self, ctx, member: converters.SafeMember, *, reason=""):
        """Bans a user from the server. OP+ only."""
        if await check_staff_id(ctx, 'Helper', member.id):
            await self.meme(ctx.author, member, "ban", ctx.channel, reason)
            return
        msg = f"You were banned from {ctx.guild.name}."
        if reason != "":
            msg += " The given reason is: " + reason
        msg += "\n\nThis ban does not expire."
        try:
            await member.send(msg)
        except (discord.errors.Forbidden, discord.errors.HTTPException):
            pass  # don't fail in case user has DMs disabled for this server, or blocked the bot
        try:
            self.bot.actions.append("ub:" + str(member.id))
            await member.ban(delete_message_days=0)
        except discord.errors.Forbidden:
            await ctx.send("💢 I don't have permission to do this.")
            return
        await ctx.send(f"{self.bot.help_command.remove_mentions(str(member))} is now b&. 👍")
        msg = f"⛔ **Ban**: {ctx.author.mention} banned {member.mention} | {member}\n🏷 __User ID__: {member.id}"
        if reason != "":
            msg += "\n✏️ __Reason__: " + reason
        await self.bot.channels['server-logs'].send(msg)
        await self.bot.channels['mod-logs'].send(msg + ("\nPlease add an explanation below. In the future, it is recommended to use `.ban <user> [reason]` as the reason is automatically sent to the user." if reason == "" else ""))

    @is_staff("OP")
    @commands.command(name="banid")
    async def banid_member(self, ctx, userid: int, *, reason=""):
        """Bans a user id from the server. OP+ only."""
        try:
            user = await self.bot.fetch_user(userid)
        except discord.errors.NotFound:
            await ctx.send(f"No user associated with ID {userid}.")
        if await check_staff_id(ctx, 'Helper', user.id):
            await ctx.send("You can't ban another staffer with this command!")
            return
        try:
            self.bot.actions.append("ub:" + str(user.id))
            await ctx.guild.ban(user, delete_message_days=0)
        except discord.errors.Forbidden:
            await ctx.send("💢 I don't have permission to do this.")
            return
        await ctx.send(f"User {user.id} | {user.name} is now b&. 👍")
        msg = f"⛔ **Ban**: {ctx.author.mention} banned ID {user.id}"
        if reason != "":
            msg += "\n✏️ __Reason__: " + reason
        await self.bot.channels['server-logs'].send(msg)
        await self.bot.channels['mod-logs'].send(msg + ("\nPlease add an explanation below. In the future, it is recommended to use `.banid <userid> [reason]` as the reason is automatically sent to the user." if reason == "" else ""))

    @is_staff("OP")
    @commands.command(name="silentban", hidden=True)
    async def silentban_member(self, ctx, member: converters.SafeMember, *, reason=""):
        """Bans a user from the server, without a notification. OP+ only."""
        if await check_staff_id(ctx, 'Helper', member.id):
            await self.meme(ctx.author, member, "ban", ctx.channel, reason)
            return
        try:
            self.bot.actions.append("ub:" + str(member.id))
            await member.ban(delete_message_days=0)
        except discord.errors.Forbidden:
            await ctx.send("💢 I don't have permission to do this.")
            return
        await ctx.send(f"{self.bot.help_command.remove_mentions(member)} is now b&. 👍")
        msg = f"⛔ **Silent ban**: {ctx.author.mention} banned {member.mention} | {member}\n🏷 __User ID__: {member.id}"
        if reason != "":
            msg += "\n✏️ __Reason__: " + reason
        await self.bot.channels['server-logs'].send(msg)
        await self.bot.channels['mod-logs'].send(msg + ("\nPlease add an explanation below. In the future, it is recommended to use `.silentban <user> [reason]`." if reason == "" else ""))

    @is_staff("OP")
    @commands.command(name="bandel")
    async def bandelete_member(self, ctx, member: converters.SafeMember, *, reason=""):
        """Bans a user from the server deleting messsage from last 7 days."""
        if await check_staff_id(ctx, 'Helper', member.id):
            await self.meme(ctx.author, member, "ban", ctx.channel, reason)
            return
        try:
            self.bot.actions.append("ub:" + str(member.id))
            await member.ban(delete_message_days=7)
        except discord.errors.Forbidden:
            await ctx.send("💢 I don't have permission to do this.")
            return
        await ctx.send(f"{self.bot.help_command.remove_mentions(member)} is now b&. 👍")
        msg = f"⛔ **Delete ban**: {ctx.author.mention} banned {member.mention} | {member}\n🏷 __User ID__: {member.id}"
        if reason != "":
            msg += "\n✏️ __Reason__: " + reason
        await self.bot.channels['server-logs'].send(msg)
        await self.bot.channels['mod-logs'].send(msg + (
            "\nPlease add an explanation below. In the future, it is recommended to use `.silentban <user> [reason]`." if reason == "" else ""))

    @is_staff("OP")
    @commands.command(name="timeban")
    async def timeban_member(self, ctx, member: converters.SafeMember, length, *, reason=""):
        """Bans a user for a limited period of time. OP+ only.\n\nLength format: #d#h#m#s"""
        if await check_staff_id(ctx, 'Helper', member.id):
            await self.meme(ctx.author, member, "timeban", ctx.channel, reason)
            return
        # thanks Luc#5653
        units = {
            "d": 86400,
            "h": 3600,
            "m": 60,
            "s": 1
        }
        seconds = 0
        match = re.findall("([0-9]+[smhd])", length)  # Thanks to 3dshax server's former bot
        if match is None:
            return None
        for item in match:
            seconds += int(item[:-1]) * units[item[-1]]
        timestamp = datetime.datetime.now()
        delta = datetime.timedelta(seconds=seconds)
        unban_time = timestamp + delta
        unban_time_string = unban_time.strftime("%Y-%m-%d %H:%M:%S")
        msg = f"You were banned from {ctx.guild.name}."
        if reason != "":
            msg += " The given reason is: " + reason
        msg += f"\n\nThis ban expires {unban_time_string} {time.tzname[0]}."
        try:
            await member.send(msg)
        except (discord.errors.Forbidden, discord.errors.HTTPException):
            pass  # don't fail in case user has DMs disabled for this server, or blocked the bot
        try:
            self.bot.actions.append("ub:" + str(member.id))
            await member.ban(reason=reason)
        except discord.errors.Forbidden:
            await ctx.send("💢 I don't have permission to do this.")
            return
        await self.add_timed_restriction(member.id, unban_time_string, 'timeban')
        await ctx.send(f"{self.bot.help_command.remove_mentions(member)} is now b& until {unban_time_string} {time.tzname[0]}. 👍")
        msg = f"⛔ **Time ban**: {ctx.author.mention} banned {member.mention} until {unban_time_string} | {member}\n🏷 __User ID__: {member.id}"
        if reason != "":
            msg += "\n✏️ __Reason__: " + reason
        await self.bot.channels['server-logs'].send(msg)
        await self.bot.channels['mod-logs'].send(msg + ("\nPlease add an explanation below. In the future, it is recommended to use `.timeban <user> <length> [reason]` as the reason is automatically sent to the user." if reason == "" else ""))

    @is_staff("OP")
    @commands.command(name="softban")
    async def softban_member(self, ctx, member: converters.SafeMember, *, reason):
        """Soft-ban a user. OP+ only.\n\nThis "bans" the user without actually doing a ban on Discord. The bot will instead kick the user every time they join. Discord bans are account- and IP-based."""
        if await check_staff_id(ctx, 'Helper', member.id):
            await self.meme(ctx.author, member, "softban", ctx.channel, reason)
            return
        if not await self.add_softban(member.id, ctx.author.id, reason):
            await ctx.send('User is already softbanned!')
        msg = f"This account is no longer permitted to participate in {ctx.guild.name}. The reason is: {reason}"
        await member.send(msg)
        try:
            await member.kick(reason=reason)
        except discord.errors.Forbidden:
            await ctx.send("💢 I don't have permission to do this.")
            return
        await ctx.send(f"{self.bot.help_command.remove_mentions(member)} is now b&. 👍")
        msg = f"⛔ **Soft-ban**: {ctx.author.mention} soft-banned {member.mention} | {member}\n🏷 __User ID__: {member.id}\n✏️ __Reason__: {reason}"
        await self.bot.channels['mod-logs'].send(msg)
        await self.bot.channels['server-logs'].send(msg)

    @is_staff("OP")
    @commands.command(name="softbanid")
    async def softbanid_member(self, ctx, user_id: int, *, reason):
        """Soft-ban a user based on ID. OP+ only.\n\nThis "bans" the user without actually doing a ban on Discord. The bot will instead kick the user every time they join. Discord bans are account- and IP-based."""
        if await check_staff_id(ctx, 'Helper', user_id):
            await ctx.send("You can't softban another staffer with this command!")
            return
        user = await self.bot.fetch_user(user_id)
        if not await self.add_softban(user_id, ctx.author.id, reason):
            await ctx.send('User is already softbanned!')
            return
        await ctx.send(f"ID {user_id} is now b&. 👍")
        msg = f"⛔ **Soft-ban**: {ctx.author.mention} soft-banned ID {user}\n✏️ __Reason__: {reason}"
        await self.bot.channels['mod-logs'].send(msg)
        await self.bot.channels['server-logs'].send(msg)

    @is_staff("OP")
    @commands.command(name="unsoftban")
    async def unsoftban_member(self, ctx, user_id: int):
        """Un-soft-ban a user based on ID. OP+ only."""
        await self.remove_softban(user_id)
        user = await self.bot.fetch_user(user_id)
        await ctx.send(f"{self.bot.help_command.remove_mentions(user.name)} has been unbanned!")
        msg = f"⚠️ **Un-soft-ban**: {ctx.author.mention} un-soft-banned {self.bot.help_command.remove_mentions(user.name)}"
        await self.bot.channels['mod-logs'].send(msg)


def setup(bot):
    bot.add_cog(KickBan(bot))
