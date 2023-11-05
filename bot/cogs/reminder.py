import discord
from discord.ext import commands
import asyncio
import re
from datetime import datetime, timedelta
import itertools

def parse_duration(duration_str):
    # This regular expression will match days, hours, minutes, and seconds
    duration_regex = re.compile(r'((?P<days>\d+?)d)?((?P<hours>\d+?)h)?((?P<minutes>\d+?)m)?((?P<seconds>\d+?)s)?')
    parts = duration_regex.match(duration_str)
    if not parts:
        return None
    parts = parts.groupdict()
    time_params = {}
    for (name, param) in parts.items():
        if param:
            time_params[name] = int(param)
    return timedelta(**time_params)

class Reminder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reminders = {}
        self.id_counter = itertools.count()
        self.bot.loop.create_task(self.check_reminders())

    async def add_reminder(self, ctx, delay, message):
        reminder_id = next(self.id_counter)
        reminder_time = datetime.now() + delay
        self.reminders[reminder_id] = (reminder_time, message, ctx.author, ctx.channel)
        await ctx.send(f"Reminder set for {reminder_time.strftime('%Y-%m-%d %H:%M:%S')}. (ID: {reminder_id})")


    async def delete_reminder(self, ctx, reminder_id):
        if reminder_id in self.reminders:
            del self.reminders[reminder_id]
            await ctx.send(f"Reminder ID {reminder_id} has been deleted.")
        else:
            await ctx.send(f"Reminder ID {reminder_id} does not exist.")

    async def check_reminders(self):
        while True:
            current_time = datetime.now()
            for reminder_id, (reminder_time, message, author, channel) in list(self.reminders.items()):
                if current_time >= reminder_time:
                    await channel.send(f"{author.mention}, here is your reminder: {message}")
                    del self.reminders[reminder_id]
            await asyncio.sleep(60)  # Check every minute

    @commands.command()
    async def remindme(self, ctx, time_str, *, message):
        # Parse the time string into a timedelta object
        duration = self.parse_duration(time_str)
        if not duration:
            await ctx.send("Invalid time format. Please specify the time like '10m', '1h', '2d', or combinations thereof.")
            return
        await self.add_reminder(ctx, duration, message)

    async def deletereminder(self, ctx, reminder_id: int):
        await self.delete_reminder(ctx, reminder_id)

async def setup(bot):
    await bot.add_cog(Reminder(bot))
