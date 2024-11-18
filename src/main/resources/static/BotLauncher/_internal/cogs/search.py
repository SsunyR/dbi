import discord
from discord.ext import commands
import aiohttp
from bs4 import BeautifulSoup
import urllib.parse
import re
from typing import List, Tuple

class Search(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    async def cog_load(self):
        """코그가 로드될 때 aiohttp 세션을 생성합니다."""
        self.session = aiohttp.ClientSession()
    
    async def cog_unload(self):
        """코그가 언로드될 때 세션을 정리합니다."""
        if self.session:
            await self.session.close()

    def clean_html(self, text: str) -> str:
        """HTML 태그와 특수문자를 제거합니다."""
        text = re.sub(r'<.*?>', '', text)
        text = text.replace('&nbsp;', ' ').replace('&quot;', '"')
        text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
        return text.strip()

    async def get_search_results(self, query: str, num_results: int = 5) -> List[Tuple[str, str, str]]:
        """구글 검색 결과를 비동기적으로 가져옵니다."""
        encoded_query = urllib.parse.quote(query)
        url = f'https://www.google.com/search?q={encoded_query}&num={num_results}'
        
        try:
            async with self.session.get(url, headers=self.headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status != 200:
                    return []
                
                html_content = await response.text()
                soup = BeautifulSoup(html_content, 'html.parser')
                
                results = []
                for div in soup.find_all('div', class_='g')[:num_results]:
                    try:
                        # 제목과 링크 추출
                        title_elem = div.find('h3')
                        if not title_elem:
                            continue
                        title = self.clean_html(title_elem.text)
                        
                        # 링크 추출
                        link_elem = div.find('a')
                        if not link_elem:
                            continue
                        link = link_elem['href']
                        if not link.startswith('http'):
                            continue
                        
                        # 설명 추출
                        desc_elem = div.find('div', class_='VwiC3b')
                        description = self.clean_html(desc_elem.text) if desc_elem else "설명 없음"
                        
                        results.append((title, link, description))
                    except Exception as e:
                        print(f"Result parsing error: {e}")
                        continue
                        
                return results
                
        except Exception as e:
            print(f"Search error: {e}")
            return []

    async def create_search_embed(self, query: str, results: List[Tuple[str, str, str]]) -> discord.Embed:
        """검색 결과를 임베드로 변환합니다."""
        embed = discord.Embed(
            title=f"'{query}' 검색 결과",
            color=discord.Color.blue()
        )
        
        for i, (title, link, description) in enumerate(results, 1):
            # 설명이 너무 길면 자르기
            if len(description) > 200:
                description = description[:197] + "..."
            
            embed.add_field(
                name=f"{i}. {title}",
                value=f"{description}\n{link}",
                inline=False
            )
        
        embed.set_footer(text="Powered by Google Search")
        return embed

    @commands.command(name='검색')
    async def 검색(self, ctx, *, query: str):
        """
        구글 검색 결과를 보여줍니다.
        사용법: !검색 [검색어]
        """
        async with ctx.typing():
            try:
                # 임시 메시지 전송
                temp_msg = await ctx.send("검색 중입니다...")
                
                # 검색 결과 가져오기
                results = await self.get_search_results(query)
                
                if not results:
                    await temp_msg.edit(content="검색 결과를 찾을 수 없습니다.")
                    return

                # 임베드 생성 및 전송
                embed = await self.create_search_embed(query, results)
                await temp_msg.edit(content=None, embed=embed)
                
            except Exception as e:
                await ctx.send(f"검색 중 오류가 발생했습니다: {str(e)}")

    @검색.error
    async def search_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("검색어를 입력해주세요. 사용법: !검색 [검색어]")
        else:
            await ctx.send(f"오류가 발생했습니다: {str(error)}")

async def setup(bot):
    await bot.add_cog(Search(bot))