import discord
from discord.ext import commands
import pathlib
import aiofiles
import os
import sys

def resource_path(relative_path):
    ''' Get absolute path to resource, works for dev and for PyInstaller '''
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base_path, relative_path)

class Forbiddens(commands.Cog):
    def __init__(self, bot: discord.Client):
        self.bot = bot
        self.forbiddens = []
        self.text_path = pathlib.Path(resource_path('docs/금지어.txt'))
        
    async def load_forbidden_words(self):
        """금지어 파일을 비동기적으로 로드합니다."""
        try:
            # 디렉토리가 없으면 생성
            os.makedirs(os.path.dirname(self.text_path), exist_ok=True)
            
            async with aiofiles.open(self.text_path, mode='r', encoding='utf-8') as f:
                content = await f.read()
                self.forbiddens = [word.strip() for word in content.splitlines() if word.strip()]
        except FileNotFoundError:
            # 파일이 없을 경우 빈 파일 생성
            async with aiofiles.open(self.text_path, mode='w', encoding='utf-8') as f:
                await f.write('')
            self.forbiddens = []
        except Exception as e:
            print(f"금지어 파일 로딩 중 오류 발생: {str(e)}")
            self.forbiddens = []

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        # 메시지에 금지어가 포함되어 있으면 삭제합니다.
        for forbidden in self.forbiddens:
            if forbidden in message.content:
                try:
                    await message.delete()
                    await message.channel.send(f"{message.author.mention}, 금지어를 사용하셨습니다.")
                except discord.errors.Forbidden:
                    await message.channel.send("메시지를 삭제할 권한이 없습니다.")
                except Exception as e:
                    print(f"메시지 삭제 중 오류 발생: {str(e)}")
                break
    
    @commands.command()
    async def 금지어(self, ctx: commands.Context):
        """
        금지어 목록을 보여줍니다.
        사용법: !금지어
        """
        if not self.forbiddens:
            await ctx.send("등록된 금지어가 없습니다.")
            return
        
        # 긴 목록일 경우 여러 메시지로 나누어 전송
        forbidden_list = ", ".join(self.forbiddens)
        if len(forbidden_list) > 1900:  # Discord 메시지 제한 2000자 고려
            chunks = [self.forbiddens[i:i+20] for i in range(0, len(self.forbiddens), 20)]
            for chunk in chunks:
                await ctx.send("금지어 목록: " + ", ".join(chunk))
        else:
            await ctx.send("금지어 목록: " + forbidden_list)
    
    @commands.command()
    async def 금지어추가(self, ctx: commands.Context, forbidden: str):
        """
        금지어를 추가합니다.
        사용법: !금지어추가 [금지어]
        """
        if forbidden in self.forbiddens:
            await ctx.send(f"{forbidden}은(는) 이미 금지어 목록에 있습니다.")
            return
            
        try:
            self.forbiddens.append(forbidden)
            async with aiofiles.open(self.text_path, mode='a', encoding='utf-8') as f:
                await f.write(forbidden + "\n")
            await ctx.send(f"금지어 목록에 {forbidden}을(를) 추가했습니다.")
        except Exception as e:
            await ctx.send(f"금지어 추가 중 오류가 발생했습니다: {str(e)}")
            self.forbiddens.remove(forbidden)  # 롤백

    @commands.command()
    async def 금지어삭제(self, ctx: commands.Context, forbidden: str):
        """
        금지어를 삭제합니다.
        사용법: !금지어삭제 [금지어]
        """
        if forbidden not in self.forbiddens:
            await ctx.send(f"{forbidden}은(는) 금지어 목록에 없습니다.")
            return
            
        try:
            self.forbiddens.remove(forbidden)
            async with aiofiles.open(self.text_path, mode='w', encoding='utf-8') as f:
                await f.write("\n".join(self.forbiddens))
            await ctx.send(f"금지어 목록에서 {forbidden}을(를) 삭제했습니다.")
        except Exception as e:
            await ctx.send(f"금지어 삭제 중 오류가 발생했습니다: {str(e)}")
            self.forbiddens.append(forbidden)  # 롤백

async def setup(bot):
    cog = Forbiddens(bot)
    await cog.load_forbidden_words()  # Cog 초기화 시 금지어 로드
    await bot.add_cog(cog)