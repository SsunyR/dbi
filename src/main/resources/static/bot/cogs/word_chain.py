import discord
from discord.ext import commands
import random
import asyncio
from typing import Dict, List, Set

class WordChainView(discord.ui.View):
    def __init__(self, timeout=180):
        super().__init__(timeout=timeout)
        self.participants: List[discord.Member] = []

    @discord.ui.button(label="참가", style=discord.ButtonStyle.green)
    async def join_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user in self.participants:
            return
        
        self.participants.append(interaction.user)
        await interaction.message.edit(
            embed=discord.Embed(
                title="끝말잇기 참가자 현황",
                description="\n".join(f"{idx + 1}. {player.display_name}" for idx, player in enumerate(self.participants))
            )
        )

    @discord.ui.button(label="나가기", style=discord.ButtonStyle.red)
    async def leave_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user not in self.participants:
            return
        
        self.participants.remove(interaction.user)
        await interaction.message.edit(
            embed=discord.Embed(
                title="끝말잇기 참가자 현황",
                description="\n".join(f"{idx + 1}. {player.display_name}" for idx, player in enumerate(self.participants))
            )
        )

    @discord.ui.button(label="게임시작", style=discord.ButtonStyle.blurple)
    async def start_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if len(self.participants) < 2:
            await interaction.response.send_message("게임을 시작하려면 최소 2명의 참가자가 필요합니다!", ephemeral=True)
            return
        
        self.stop()
        await interaction.response.defer()

class GameControlView(discord.ui.View):
    def __init__(self, game_manager, timeout=180):
        super().__init__(timeout=timeout)
        self.game_manager = game_manager

    @discord.ui.button(label="새 게임", style=discord.ButtonStyle.green)
    async def new_game_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.game_manager.start_new_game(interaction)

    @discord.ui.button(label="게임 끝", style=discord.ButtonStyle.red)
    async def end_game_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.game_manager.end_game(interaction)

class WordChainGame:
    def __init__(self, participants: List[discord.Member], channel: discord.TextChannel):
        self.participants = participants
        self.channel = channel
        self.player_order: List[discord.Member] = []
        self.current_player_idx = 0
        self.used_words: Set[str] = set()
        self.last_word = ""
        self.word_history: List[str] = []
        
    def get_current_player(self) -> discord.Member:
        return self.player_order[self.current_player_idx]

    def next_player(self):
        self.current_player_idx = (self.current_player_idx + 1) % len(self.player_order)

    def is_valid_word(self, word: str) -> bool:
        if not self.last_word:  # 첫 단어인 경우
            return True
        return word[0] == self.last_word[-1] and word not in self.used_words

class WordChain(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.games: Dict[int, WordChainGame] = {}  # guild_id: game
        
    async def create_game_channel(self, guild: discord.Guild, participants: List[discord.Member]) -> discord.TextChannel:
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True)
        }
        
        for participant in participants:
            overwrites[participant] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
            
        channel = await guild.create_text_channel(
            '끝말잇기-게임',
            overwrites=overwrites
        )
        return channel

    async def start_new_game(self, interaction: discord.Interaction):
        game = self.games.get(interaction.guild_id)
        if not game:
            await interaction.response.send_message("진행 중인 게임이 없습니다!", ephemeral=True)
            return

        # 새로운 순서 생성
        random.shuffle(game.participants)
        game.player_order = game.participants.copy()
        game.current_player_idx = 0
        game.used_words.clear()
        game.word_history.clear()
        game.last_word = ""

        order_msg = "🎲 새로운 게임을 시작합니다!\n\n플레이어 순서:\n"
        order_msg += "\n".join(f"{idx + 1}. {player.display_name}" for idx, player in enumerate(game.player_order))
        
        await game.channel.send(order_msg)
        await interaction.response.send_message("새 게임이 시작되었습니다!", ephemeral=True)

    async def end_game(self, interaction: discord.Interaction):
        game = self.games.get(interaction.guild_id)
        if not game:
            await interaction.response.send_message("진행 중인 게임이 없습니다!", ephemeral=True)
            return

        channel_to_delete = game.channel
        del self.games[interaction.guild_id]
        await channel_to_delete.delete()
        await interaction.response.send_message("게임이 종료되었습니다.", ephemeral=True)

    @commands.command(name="끝말잇기")
    async def word_chain(self, ctx):
        """
        - 끝말잇기 게임을 시작합니다.(2인 이상)
        """
        if ctx.guild.id in self.games:
            await ctx.send("이미 진행 중인 게임이 있습니다!")
            return

        view = WordChainView()
        embed = discord.Embed(
            title="끝말잇기 참가자 현황",
            description="아직 참가자가 없습니다."
        )
        await ctx.send(embed=embed, view=view)
        
        await view.wait()
        if len(view.participants) < 2:
            await ctx.send("참가자가 부족하여 게임을 시작할 수 없습니다.")
            return

        # 게임 채널 생성
        game_channel = await self.create_game_channel(ctx.guild, view.participants)
        
        # 게임 인스턴스 생성
        game = WordChainGame(view.participants, game_channel)
        self.games[ctx.guild.id] = game
        
        # 순서 정하기
        random.shuffle(game.participants)
        game.player_order = game.participants.copy()
        
        # 순서 안내
        order_msg = "🎮 게임이 시작됩니다!\n\n플레이어 순서:\n"
        order_msg += "\n".join(f"{idx + 1}. {player.display_name}" for idx, player in enumerate(game.player_order))
        order_msg += f"\n\n{game.get_current_player().mention}님부터 시작해 주세요!"
        
        await game_channel.send(order_msg)
        
        # 게임 진행
        while True:
            current_player = game.get_current_player()
            
            def check(message):
                return (message.channel == game_channel and 
                       message.author == current_player)
            
            try:
                message = await self.bot.wait_for('message', timeout=30.0, check=check)
                word = message.content.strip()
                
                if not game.is_valid_word(word):
                    await game_channel.send(f"❌ {current_player.mention}님이 패배하셨습니다!")
                    
                    # 게임 종료 후 컨트롤 뷰 표시
                    view = GameControlView(self)
                    await game_channel.send("게임이 종료되었습니다. 다음 중 선택해주세요:", view=view)
                    break
                
                game.used_words.add(word)
                game.last_word = word
                game.word_history.append(word)
                
                # 단어 기록 표시
                history_msg = " - ".join(game.word_history)
                await game_channel.send(f"✅ {current_player.mention}님: {history_msg}")
                
                game.next_player()
                await game_channel.send(f"다음 차례: {game.get_current_player().mention}")
                
            except asyncio.TimeoutError:
                await game_channel.send(f"⏰ {current_player.mention}님이 시간 초과로 패배하셨습니다!")
                
                view = GameControlView(self)
                await game_channel.send("게임이 종료되었습니다. 다음 중 선택해주세요:", view=view)
                break

async def setup(bot):
    await bot.add_cog(WordChain(bot))