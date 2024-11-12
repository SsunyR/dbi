import discord
from discord.ext import commands

class Voice(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.temporary_channels = []
        self.temporary_categories = []
        self.bot.loop.create_task(self.setup_voice_channels())

    async def setup_voice_channels(self):
        # 봇이 준비될 때까지 대기
        await self.bot.wait_until_ready()
        
        for guild in self.bot.guilds:
            try:
                temporary_category = discord.utils.get(guild.categories, name="임시")

                # 임시 카테고리 생성
                if not temporary_category:
                    temporary_category = await self.create_temporary_category(guild)

                # 임시 음성 채널 생성
                if not discord.utils.get(temporary_category.voice_channels, name="임시"):
                    await self.create_temporary_channel(temporary_category)
            except Exception as e:
                print(f"Error setting up voice channels in guild {guild.name}: {e}")

    async def create_temporary_category(self, guild: discord.Guild):
        category = await guild.create_category(name="임시")
        return category

    async def create_temporary_channel(self, category: discord.CategoryChannel):
        channel = await category.create_voice_channel(name="임시")
        return channel

    def get_channel_name(self, member: discord.Member) -> str:
        # 닉네임이 없으면 사용자 이름 사용
        display_name = member.nick or member.name
        # 특수문자 제거 및 길이 제한
        safe_name = ''.join(c for c in display_name if c.isalnum() or c.isspace())
        return f"{safe_name[:20]}의 채널"

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        try:
            # 채널 입장 처리
            if after.channel and after.channel.name == "임시":
                channel_name = self.get_channel_name(member)
                temp_channel = await after.channel.clone(name=channel_name)
                await member.move_to(temp_channel)
                self.temporary_channels.append(temp_channel.id)

            # 채널 퇴장 처리
            if before.channel:
                if before.channel.id in self.temporary_channels:
                    if len(before.channel.members) == 0:
                        await before.channel.delete()
                        self.temporary_channels.remove(before.channel.id)
                
                if before.channel.id in self.temporary_categories:
                    if len(before.channel.members) == 0:
                        category = before.channel.category
                        if category:
                            for channel in category.channels:
                                await channel.delete()
                            await category.delete()
                            if before.channel.id in self.temporary_categories:
                                self.temporary_categories.remove(before.channel.id)

        except Exception as e:
            print(f"Error in voice state update: {e}")

async def setup(bot: commands.Bot):
    await bot.add_cog(Voice(bot))