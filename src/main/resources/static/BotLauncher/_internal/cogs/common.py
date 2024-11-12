import discord
from discord.ext import commands

class Common(commands.Cog):
    
    def __init__(self, bot: discord.Client):
        self.bot = bot

    @commands.command()
    async def 멤버(self, ctx: commands.Context):
        """
        - 서버의 멤버 상태를 확인합니다. 사용법: !멤버
        """
        online = 0
        offline = 0
        dnd = 0
        idle = 0
        members = ctx.guild.members
        for member in members:
            if member.bot:
                continue
            if member.status == discord.Status.online:
                online += 1
            if member.status == discord.Status.offline:
                offline += 1
            if member.status == discord.Status.dnd:
                dnd += 1
            if member.status == discord.Status.idle:
                idle += 1

        await ctx.send(f"온라인 : {online}\n오프라인 : {offline}\n방해금지 : {dnd}\n자리비움 : {idle}")

    
    # 내가 입력한 마지막 메시지 삭제
    @commands.command()
    async def 삭제(self, ctx: commands.Context, count: int = 1):
        """
        - 명령어를 사용한 사용자의 최근 메시지를 삭제합니다.
        - 사용법: !삭제 [개수] (기본값: 1)
        """
        # 최근 메시지를 10개까지 확인해 명령어를 제외한 메시지를 개수만큼 삭제
        deleted = 0
        async for message in ctx.channel.history(limit=10):
            if message != ctx.message and message.author == ctx.author and count > 0:
                await message.delete()
                count -= 1
                deleted += 1
        
        if deleted > 0:
            # 삭제 완료 메시지
            await ctx.send(f"{deleted}개의 메시지를 삭제했습니다.", delete_after=5)
        else:
            # 삭제할 메시지가 없을 때
            await ctx.send("삭제할 메시지가 없습니다.", delete_after=5)
        
        # 명령어 메시지 삭제
        await ctx.message.delete()

async def setup(bot):
    await bot.add_cog(Common(bot))