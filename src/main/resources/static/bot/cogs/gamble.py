import discord
from discord.ext import commands
import random
import asyncio

class Gamble(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="제비뽑기")
    async def draw_lots(self, ctx, *, options=None):
        """
        - 쉼표로 구분된 옵션들 중에서 하나를 무작위로 선택합니다. (!제비뽑기 옵션1, 옵션2, ...)
        """
        if not options:
            await ctx.send("사용법: !제비뽑기 옵션1, 옵션2, 옵션3, ...")
            return
        
        choices = [choice.strip() for choice in options.split(",")]
        if len(choices) < 2:
            await ctx.send("최소 2개 이상의 옵션이 필요합니다!")
            return
        
        selected = random.choice(choices)
        await ctx.send(f"🎯 제비뽑기 결과: **{selected}**")

    @commands.command(name="추첨")
    async def draw_numbers(self, ctx, start: int = 1, end: int = 10):
        """
        - 범위 내에서 무작위로 숫자를 추첨합니다. (!추첨 [시작 숫자] [끝 숫자])
        """
        try:
            # 입력값 검증
            if start >= end:
                await ctx.send("시작 숫자는 끝 숫자보다 작아야 합니다!")
                return
            
            # 숫자 추첨
            number = random.sample(range(start, end + 1), 1)
            
            # 결과 임베드 생성
            embed = discord.Embed(
                title="🎯 번호 추첨 결과",
                color=discord.Color.green()
            )
            
            embed.description = f"**{number}**"
            
            # 추첨 정보 표시
            info = f"범위: {start}~{end}"
            embed.set_footer(text=info)
            
            # 추첨 애니메이션 (선택적)
            msg = await ctx.send("🎲 추첨 중...")
            await asyncio.sleep(1.5)
            await msg.edit(content=None, embed=embed)
            
        except ValueError:
            await ctx.send("올바른 숫자를 입력해주세요!")
        except:
            await ctx.send("추첨 중 오류가 발생했습니다.")
    
    @commands.command(name="로또")
    async def lotto(self, ctx):
        """
        - 로또 번호를 생성합니다 (1~45 중 6개)
        """
        try:
            
            embed = discord.Embed(
                title="🎱 로또 번호 생성기",
                color=discord.Color.gold()
            )
            
            numbers = random.sample(range(1, 46), 6)
            numbers.sort()
            numbers_str = " - ".join(map(str, numbers))
            
            embed.add_field(
                name=f"🎲 추첨 결과",
                value=f"**{numbers_str}**",
                inline=False
            )
            
            msg = await ctx.send("🎲 번호 생성 중...")
            await asyncio.sleep(1)
            await msg.edit(content=None, embed=embed)
            
        except:
            await ctx.send("번호 생성 중 오류가 발생했습니다.")

async def setup(bot):
    await bot.add_cog(Gamble(bot))