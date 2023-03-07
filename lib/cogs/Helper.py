import json

import discord
from discord import ButtonStyle, NotFound
from discord.ext.commands import command, Cog


class PageButtons(discord.ui.View):
    def __init__(self, embeds):
        self.embeds = embeds
        self.max_page = len(embeds) - 1
        self.current_page = 0
        super().__init__()
        self.thumbs_up_button.disabled = True
        self.previous_page_button.disabled = True

    def button_handler(self):
        if self.current_page == self.max_page:
            self.next_page_button.disabled = True
            self.thumbs_up_button.disabled = False
        elif self.current_page == 0:
            self.previous_page_button.disabled = True
        else:
            self.next_page_button.disabled = False
            self.previous_page_button.disabled = False
            self.thumbs_up_button.disabled = True

    @discord.ui.button(
        label="Previous Page",
        style=ButtonStyle.green,
        custom_id=f"previous_page"
    )
    async def previous_page_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page - 1 < 0:
            pass
        else:
            self.current_page -= 1

        self.button_handler()

        try:
            await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)
        except NotFound:
            self.stop()

    @discord.ui.button(
        label="Next Page",
        style=ButtonStyle.green,
        custom_id=f"next_page"
    )
    async def next_page_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page + 1 > self.max_page:
            return
        else:
            self.current_page += 1

        self.button_handler()

        try:
            await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)
        except NotFound:
            self.stop()

    @discord.ui.button(
        emoji="👍",
        style=ButtonStyle.green,
        custom_id=f"thumbs_up"
    )
    async def thumbs_up_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        for item in self.children:
            item.disabled = True

        await interaction.user.add_roles(discord.Object(id=1082476391615955046),
                                         reason="User has completed the introduction.")

        await interaction.response.edit_message(content="Welcome to the server!", embed=None, view=self)


class EmbedSpawner(discord.ui.View):
    def __init__(self):
        self.embed_data = None
        with open('data/embed_data.json', 'r', encoding='utf-8') as f:
            self.embed_data = json.load(f)
        super().__init__()

    @discord.ui.button(
        label="Begin Tutorial",
        style=ButtonStyle.green,
        custom_id=f"begin_tutorial"
    )
    async def begin_tutorial_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        embeds = []
        for page_num, description in enumerate(self.embed_data['introduction']):
            embed = discord.Embed()
            embed.set_author(name="Server Introduction", icon_url=interaction.client.user.display_avatar.url)

            embed.description = description

            if str(page_num) in self.embed_data['images']['introduction']:
                embed.set_image(url=self.embed_data['images']['introduction'][str(page_num)])

            embed.set_footer(text=f"Page {page_num + 1}/{len(self.embed_data['introduction'])}")

            embeds.append(embed)

        view = PageButtons(embeds)

        await interaction.response.send_message(embed=embeds[0], view=view, ephemeral=True)


class Helper(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name='setup', aliases=['s'])
    async def setup_embed(self, ctx):
        """Sets up the embed spawner."""
        view = EmbedSpawner()
        await ctx.send("Welcome to the Vaulted Relic Community server, please follow the steps shown in this tutorial. "
                       "Start by clicking begin tutorial.", view=view)

    @command(name='reload_embeds', aliases=['re'])
    async def reload_embed_info(self, ctx):
        """Reloads embed info."""
        with open('data/embed_data.json', 'r', encoding='utf-8') as f:
            self.embed_data = json.load(f)

        await ctx.send("Embed data has been reloaded.")

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("Helper")


async def setup(bot):
    await bot.add_cog(Helper(bot))
