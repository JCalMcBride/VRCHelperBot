import json
import os

import discord
from discord.ext.commands import command, Cog, has_permissions
from more_itertools import chunked


class Moderation(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.relay_dict = {
            780228847659646996: 780427248741646346,
            780427248741646346: 780228847659646996,
            781837036084133929: 780378483657932861,
            780324338566037524: 780378483657932861,
        }
        self.replacement_dict = {
            "<@780427862742269977>": "<@&780232882228559882>",
            "<@780232882228559882>": "<@&780427862742269977>"
        }
        self.deletion_list = [781837036084133929, 780324338566037524]
        self.typing_list = [780228847659646996, 780427248741646346]
        self.relic_burner_dict = {
            780376195182493707: 780381645181681674,
            780199960980750376: 780202057885286440
        }
        self.introduction_dict = {780376195182493707: 1082479236872405073,
                                  780199960980750376: 1082486097034092604}
        self.notified_users = []

        self.role_data_file = "role_data.json"
        self.role_data = {}

        # Load role data from the JSON file
        if os.path.exists(self.role_data_file):
            try:
                with open(self.role_data_file, "r") as f:
                    self.role_data = json.load(f)
            except json.JSONDecodeError:
                print("Error: Invalid JSON file. Resetting role data.")
                self.role_data = {}

    @command(name="addrestricted")
    @has_permissions(manage_roles=True)
    async def add_restricted_role(self, ctx, user: str):
        role_id = 1175080632855056404
        burners_role_id = 780381645181681674
        role = ctx.guild.get_role(role_id)
        burners_role = ctx.guild.get_role(burners_role_id)

        if role is None:
            await ctx.send(f"Role with ID {role_id} not found.")
            return

        user_id = None
        if user.startswith("<@") and user.endswith(">"):
            user_id = int(user[2:-1].replace("!", ""))
        else:
            try:
                user_id = int(user)
            except ValueError:
                await ctx.send("Invalid user ID or mention.")
                return

        guild_member = ctx.guild.get_member(user_id)

        if guild_member is not None:
            if role in guild_member.roles:
                await ctx.send(f"<@{user_id}> already has the role.")
            else:
                await guild_member.add_roles(role)
                await ctx.send(f"Added the role to <@{user_id}>.")

            if burners_role in guild_member.roles:
                await guild_member.remove_roles(ctx.guild.get_role(burners_role))
        else:
            if str(user_id) in self.role_data:
                if role_id not in self.role_data[str(user_id)]:
                    self.role_data[str(user_id)].append(role_id)

                if burners_role_id in self.role_data[str(user_id)]:
                    self.role_data[str(user_id)].remove(burners_role_id)
            else:
                self.role_data[str(user_id)] = [role_id]
            try:
                with open(self.role_data_file, "w") as f:
                    json.dump(self.role_data, f)
            except Exception as e:
                print(f"Error saving role data: {e}")
            await ctx.send(f"User <@{user_id}> will be given the restricted role when they join.")

    async def save_user_roles(self, member):
        if member.guild.id == 780376195182493707:
            role_ids = [role.id for role in member.roles][1:]
            self.role_data[str(member.id)] = role_ids
            try:
                with open(self.role_data_file, "w") as f:
                    json.dump(self.role_data, f)
            except Exception as e:
                print(f"Error saving role data: {e}")

    async def readd_user_roles(self, member):
        if member.guild.id == 780376195182493707 and str(member.id) in self.role_data:
            role_ids = self.role_data[str(member.id)]
            burners_role_id = 780381645181681674
            restricted_role_id = 1175080632855056404

            if burners_role_id in role_ids and restricted_role_id in role_ids:
                role_ids.remove(burners_role_id)

            roles = [role for role in member.guild.roles if role.id in role_ids]

            for role in roles:
                try:
                    await member.add_roles(role)
                except Exception as e:
                    print(f"Error adding {role} roles to {member.name}: {e}")
            self.role_data.pop(str(member.id), None)  # Remove user's roles from the list
            with open(self.role_data_file, "w") as f:
                json.dump(self.role_data, f)

    @Cog.listener()
    async def on_member_remove(self, member):
        await self.save_user_roles(member)

    @Cog.listener()
    async def on_member_join(self, member):
        await self.readd_user_roles(member)

    async def relay_message(self, message, attachments, from_channel_id, to_channel_id):
        channel = self.bot.get_channel(to_channel_id)

        for word in self.replacement_dict:
            message.content = message.content.replace(word, self.replacement_dict[word])

        files = []
        for attachment in attachments:
            files.append(await attachment.to_file())

        message = f"**{message.author}** said in <#{from_channel_id}>: {message.content}"
        if len(message) > 1900:
            await channel.send(content=message[:1900], files=files)
            for message_part in chunked(message[1900:], 1900):
                await channel.send(content="".join(message_part))
        else:
            await channel.send(content=message, files=files)

    @Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if message.channel.id in self.relay_dict:
            if message.channel.id in self.deletion_list:
                await message.delete()

            if message.content[0] == "?":
                return

            await self.relay_message(message, message.attachments, message.channel.id,
                                     self.relay_dict[message.channel.id])

    @Cog.listener()
    async def on_typing(self, channel, user, when):
        if channel.id in self.typing_list \
                and user.id not in self.notified_users \
                and self.relic_burner_dict[channel.guild.id] not in [x.id for x in user.roles]:
            await channel.send(f"{user.mention} Hi! You do not currently have the relic burners role "
                               f"which you can receive after "
                               f"completing the tutorial in <#{self.introduction_dict[channel.guild.id]}>. "
                               f"Please complete the tutorial to receive the role "
                               f"and gain access to the rest of the server. "
                               f"Thank you! If that is not why you are asking for help, please continue.",
                               delete_after=20)
            self.notified_users.append(user.id)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("Moderation")


async def setup(bot):
    await bot.add_cog(Moderation(bot))
