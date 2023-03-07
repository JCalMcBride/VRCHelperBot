import discord
from discord.ext.commands import command, Cog, has_permissions


class Misc(Cog):
    def __init__(self, bot):
        self.bot = bot

    @has_permissions(manage_messages=True)
    @command(name='reload')
    async def reload(self, ctx, module: str):
        """Reloads a module."""
        try:
            try:
                await self.bot.unload_extension(f"lib.cogs.{module.title()}")
            except Exception as e:
                pass

            await self.bot.load_extension(f"lib.cogs.{module.title()}")

            await ctx.send("The " + module.title() + " module has been successfully reloaded.")
        except Exception as e:
            print(e)
            await ctx.send(
                "The " + module.title() + " module has not been reloaded, check your spelling and try again.")

    @has_permissions(manage_messages=True)
    @command(name='sync_slash')
    async def sync_slash(self, ctx):
        """Syncs slash commands."""
        try:
            await self.bot.tree.sync(guild=discord.Object(id=780376195182493707))
            await self.bot.tree.sync()

            await ctx.send("Slash commands successfully synced.")
        except Exception as e:
            await ctx.send(
                f"Slash commands could not be synced, try again later, exception: {e}")

    @has_permissions(manage_guild=True)
    @command(name='shutdown')
    async def shutdown_bot(self, ctx):
        """
        Shuts down the bot entirely, can only be restarted by manually starting it again.
        """
        await self.bot.close()

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("Misc")


async def setup(bot):
    await bot.add_cog(Misc(bot))
