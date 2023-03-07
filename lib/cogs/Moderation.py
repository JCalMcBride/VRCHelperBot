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

            await self.relay_message(message, message.attachments, message.channel.id, self.relay_dict[message.channel.id])

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
                               delete_after=10)
            self.notified_users.append(user.id)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("Moderation")


async def setup(bot):
    await bot.add_cog(Moderation(bot))
