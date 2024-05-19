import json

import discord
from discord import ButtonStyle, NotFound
from discord.ext.commands import command, Cog, has_permissions


class PageButtons(discord.ui.View):
    def __init__(self, embeds):
        self.embeds = embeds
        self.max_page = len(embeds) - 1
        self.current_page = 0
        super().__init__()
        self.thumbs_up_button.disabled = True
        self.tools_button.disabled = True
        self.previous_page_button.disabled = True

    def button_handler(self, guild_id: int):
        if self.current_page == self.max_page:
            self.next_page_button.disabled = True
            self.thumbs_up_button.disabled = False
            if guild_id == 780376195182493707:
                self.tools_button.disabled = False
        elif self.current_page == 0:
            self.previous_page_button.disabled = True
        else:
            self.next_page_button.disabled = False
            self.previous_page_button.disabled = False
            self.thumbs_up_button.disabled = True
            self.tools_button.disabled = True

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

        self.button_handler(interaction.guild_id)

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

        self.button_handler(interaction.guild_id)

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

        try:
            if interaction.guild_id == 780376195182493707:
                role_id = 780381645181681674
            elif interaction.guild_id == 780199960980750376:
                role_id = 780202057885286440

            await interaction.user.add_roles(discord.Object(id=role_id),
                                             reason="User has completed the introduction.")
        except Exception as e:
            await interaction.response.edit_message(content="An error occurred while trying to add the role to you,"
                                                            " please contact a staff member.", embed=None, view=None)

        try:
            await interaction.response.edit_message(content="Welcome to the server!\n\n"
                                                            "If you change your mind and would like to disable access "
                                                            "to the communtiy channels, just go through "
                                                            "this again and select the other option.",
                                                    embed=None, view=self)
        except NotFound:
            self.stop()

    @discord.ui.button(
        emoji="🛠️",
        style=ButtonStyle.green,
        custom_id=f"tools_button"
    )
    async def tools_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        for item in self.children:
            item.disabled = True

        try:
            if interaction.guild_id == 780376195182493707:
                role_id = 1229377208926077008

            await interaction.user.add_roles(discord.Object(id=role_id),
                                             reason="User has completed the introduction.")
        except Exception as e:
            await interaction.response.edit_message(content="An error occurred while trying to add the role to you,"
                                                            " please contact a staff member.", embed=None, view=None)

        try:
            await interaction.response.edit_message(content="Welcome to the server!\n\n"
                                                            "If you ever want to have access to the community channels, "
                                                            "just go through this again and select the other option.",
                                                    embed=None, view=self)
        except NotFound:
            self.stop()


class EmbedSpawner(discord.ui.View):
    def __init__(self):
        self.embed_data = None
        with open('data/embed_data.json', 'r', encoding='utf-8') as f:
            self.embed_data = json.load(f)
        super().__init__(timeout=None)

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

    @has_permissions(manage_messages=True)
    @command(name='setup', aliases=['s'])
    async def setup_embed(self, ctx):
        """Sets up the embed spawner."""
        view = EmbedSpawner()
        server_name = ctx.guild.name
        await ctx.send(f"Welcome to the {server_name} server, please follow the steps shown in this tutorial. "
                       "Start by clicking begin tutorial.", view=view)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            view_vrc = EmbedSpawner()
            self.bot.add_view(view_vrc, message_id=1082479515319664752)

            view_vrr = EmbedSpawner()
            self.bot.add_view(view_vrr, message_id=1082486372100747264)

            self.bot.cogs_ready.ready_up("Helper")


async def setup(bot):
    await bot.add_cog(Helper(bot))
