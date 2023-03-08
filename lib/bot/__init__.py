import asyncio
import logging
import os
from asyncio import sleep
from glob import glob

import discord
from discord import Intents, Forbidden, HTTPException, NotFound, app_commands
from discord.ext.commands import Bot as BotBase, CommandNotFound, BadArgument, MissingRequiredArgument, \
    CommandOnCooldown, MissingPermissions, MissingRole, when_mentioned_or
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import utc

OWNER_IDS = [585035501929758721]
COGS = [path.split(os.sep)[-1][:-3] for path in glob(f".{os.sep}lib{os.sep}cogs{os.sep}*.py")]
IGNORE_EXCEPTIONS = (BadArgument, SyntaxError, MissingRequiredArgument)


class Ready(object):
    def __init__(self):
        for cog in COGS:
            setattr(self, cog, False)

    def ready_up(self, cog):
        setattr(self, cog, True)
        print(f" {cog} cog ready")

    def all_ready(self):
        return all([getattr(self, cog) for cog in COGS])


def get_prefix(bot, message):
    prefix_list = ['v!']
    if not message.guild:
        prefix_list.append('')

    return when_mentioned_or(*prefix_list)(bot, message)


class Bot(BotBase):
    def __init__(self):
        self.stdout = None
        self.ready = False
        self.cogs_ready = Ready()
        self.scheduler = AsyncIOScheduler(timezone=utc)

        super().__init__(
            command_prefix=get_prefix,
            owner_ids=OWNER_IDS,
            intents=Intents.all()
        )

        self.tree.on_error = self.on_tree_error

    def setup(self):
        for cog in COGS:
            asyncio.run(self.load_extension(f"lib.cogs.{cog}"))
            print(f" {cog} cog loaded")

        print("Setup complete.")

    def run(self):
        print("Running setup.")
        self.setup()

        with open("./lib/bot/token", "r", encoding="utf-8") as tf:
            self.TOKEN = tf.read()

        print("Running bot.")
        super().run(self.TOKEN, reconnect=True)

    async def on_connect(self):
        print("Bot connected.")

    async def on_disconnect(self):
        print("Bot disconnected.")

    async def on_error(self, err, *args, **kwargs):
        raise

    async def message_delete_handler(self, original_message, message, channel, delete_delay=15, delete_original=True):
        if message.guild:
            if delete_original:
                try:
                    await original_message.delete(delay=1)
                except NotFound:
                    pass
                except Forbidden:
                    pass
                except HTTPException:
                    pass

            if channel.name != "bot-spam":
                await sleep(delete_delay)
                try:
                    await message.delete()
                except NotFound:
                    pass
                except Forbidden:
                    pass
                except HTTPException:
                    pass

    def mdh(self, original_message, message, channel, delete_delay=15, delete_original=True):
        bot.ct(self.message_delete_handler(original_message, message, channel, delete_delay, delete_original))

    async def on_command_error(self, ctx, exc):
        if any([isinstance(exc, error) for error in IGNORE_EXCEPTIONS]):
            pass
        elif isinstance(exc, CommandNotFound):
            pass
        elif isinstance(exc, CommandOnCooldown):
            message = await ctx.send("Command is currently on cooldown, try again later.")
            self.mdh(ctx.message, message, ctx.channel, 5)
        elif isinstance(exc, MissingPermissions):
            message = await ctx.send("You lack the permissions to use this command.")
            self.mdh(ctx.message, message, ctx.channel, 5)
        elif isinstance(exc, MissingRole):
            message = await ctx.send("You lack the role required to use this command.")
            self.mdh(ctx.message, message, ctx.channel, 5)
        elif hasattr(exc, "original"):
            if isinstance(exc.original, SyntaxError):
                message = await ctx.send("Something is wrong with the syntax of that command.")
                self.mdh(ctx.message, message, ctx.channel, 5)
            elif isinstance(exc, HTTPException):
                message = await ctx.send("Unable to send message.")
                self.mdh(ctx.message, message, ctx.channel, 5)
            elif isinstance(exc, Forbidden):
                message = await ctx.send("I do not have permission to do that.")
                self.mdh(ctx.message, message, ctx.channel, 5)
            else:
                raise exc.original
        else:
            raise exc

    async def on_tree_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            return await interaction.response.send_message(
                f"Command is currently on cooldown! Try again in **{error.retry_after:.2f}** seconds!")
        else:
            raise error

    async def on_ready(self):
        if not self.ready:
            self.scheduler.start()
            self.ct = bot.loop.create_task

            while not self.cogs_ready.all_ready():
                await sleep(0.5)

            self.ready = True
            print("Bot ready.")
        else:
            print("Bot reconnected.")

    async def on_message(self, message):
        if not message.author.bot:
            await self.process_commands(message)

    async def process_commands(self, message):
        if message.author.bot:
            return

        ctx = await self.get_context(message)
        if ctx.command is not None:
            logging.info(f"{ctx.author.id} used command: {ctx.command} in {ctx.channel}"
                         f"{f' in guild {ctx.guild}' if ctx.guild is not None else ''}")

        await self.invoke(ctx)


bot = Bot()
