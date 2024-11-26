import discord
from discord.ext import commands
from discord import ui
import asyncio

class VoteModal(ui.Modal, title="투표 항목 입력"):
    def __init__(self, vote_title):
        super().__init__()
        self.vote_title = vote_title
        self.items = []

        self.add_item(ui.TextInput(
            label="투표 항목들 (줄바꿈으로 구분)",
            style=discord.TextStyle.paragraph,
            placeholder="항목1\n항목2\n항목3",
            required=True
        ))

    async def on_submit(self, interaction: discord.Interaction):
        self.items = self.children[0].value.split('\n')
        self.items = [item.strip() for item in self.items if item.strip()]
        
        if len(self.items) < 2:
            await interaction.response.send_message("최소 2개 이상의 투표 항목이 필요합니다.", ephemeral=True)
            return

        view = VoteView(self.vote_title, self.items, interaction.user)
        embed = self.create_vote_embed()
        await interaction.response.send_message(embed=embed, view=view)

    def create_vote_embed(self):
        embed = discord.Embed(title=f"📊 {self.vote_title}", color=discord.Color.blue())
        for i, item in enumerate(self.items, 1):
            embed.add_field(name=f"선택지 {i}", value=item, inline=False)
        embed.set_footer(text="아래 버튼을 눌러 투표를 시작하세요.")
        return embed

class VoteButton(ui.Button):
    def __init__(self, index, label):
        super().__init__(style=discord.ButtonStyle.gray, label=label)
        self.index = index

    async def callback(self, interaction: discord.Interaction):
        view: VoteView = self.view
        
        if not view.is_active:
            await interaction.response.send_message("투표가 종료되었습니다.", ephemeral=True)
            return

        user_id = interaction.user.id
        
        for voters in view.votes.values():
            if user_id in voters:
                voters.remove(user_id)
        
        view.votes[self.index].append(user_id)
        
        embed = view.create_vote_embed()
        await interaction.response.edit_message(embed=embed, view=view)

class VoteView(ui.View):
    def __init__(self, title, items, author):
        super().__init__(timeout=None)
        self.title = title
        self.items = items
        self.author = author
        self.votes = {i: [] for i in range(len(items))}
        self.is_active = False
        self.message = None

    @ui.button(label="투표 시작", style=discord.ButtonStyle.green)
    async def start_vote(self, interaction: discord.Interaction, button: ui.Button):
        if self.is_active:
            await interaction.response.send_message("이미 투표가 진행 중입니다.", ephemeral=True)
            return

        self.is_active = True
        button.disabled = True
        
        for i, item in enumerate(self.items):
            self.add_item(VoteButton(i, item))
        
        self.add_item(EndVoteButton(self))

        embed = self.create_vote_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    def create_vote_embed(self):
        embed = discord.Embed(title=f"📊 {self.title}", color=discord.Color.blue())
        
        if not self.is_active:
            for i, item in enumerate(self.items, 1):
                embed.add_field(name=f"선택지 {i}", value=item, inline=False)
            return embed

        total_votes = sum(len(voters) for voters in self.votes.values())
        
        for i, item in enumerate(self.items):
            voters = self.votes[i]
            vote_count = len(voters)
            percentage = (vote_count / total_votes * 100) if total_votes > 0 else 0
            bar_length = int(percentage / 10) if percentage > 0 else 0
            bar = "█" * bar_length + "░" * (10 - bar_length)
            
            value = f"{bar} {vote_count}표 ({percentage:.1f}%)"
            embed.add_field(name=f"{item}", value=value, inline=False)

        if not self.is_active:
            embed.set_footer(text="투표가 종료되었습니다.")
        
        return embed

    def create_result_embed(self):
        total_votes = sum(len(voters) for voters in self.votes.values())
        
        # 결과를 득표순으로 정렬
        sorted_results = sorted(
            [(i, len(voters)) for i, voters in self.votes.items()],
            key=lambda x: x[1],
            reverse=True
        )

        embed = discord.Embed(
            title=f"📊{self.title}",
            color=discord.Color.gold()
        )

        embed.add_field(
            name="총 투표수",
            value=f"**{total_votes}**표",
            inline=False
        )

        # 1등 항목 강조
        if sorted_results:
            winner_idx, winner_votes = sorted_results[0]
            winner_percentage = (winner_votes / total_votes * 100) if total_votes > 0 else 0
            embed.add_field(
                name="🏆 최다 득표",
                value=f"**{self.items[winner_idx]}**\n{winner_votes}표 ({winner_percentage:.1f}%)",
                inline=False
            )

        embed.add_field(
            name="상세 결과",
            value="ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ",
            inline=False
        )

        # 각 항목별 결과 표시
        for i, (item_idx, vote_count) in enumerate(sorted_results, 1):
            percentage = (vote_count / total_votes * 100) if total_votes > 0 else 0
            bar_length = int(percentage / 10) if percentage > 0 else 0
            bar = "█" * bar_length + "░" * (10 - bar_length)
            

            rank_emoji = ["🥇", "🥈", "🥉"]
            rank = rank_emoji[i-1] if i <= 3 else f"{i}."
            
            embed.add_field(
                name=f"{rank} {self.items[item_idx]}",
                value=f"{bar} {vote_count}표 ({percentage:.1f}%)",
                inline=False
            )

        embed.set_footer(text=f"투표 생성자: {self.author.display_name}")
        return embed

class EndVoteButton(ui.Button):
    def __init__(self, vote_view: VoteView):
        super().__init__(style=discord.ButtonStyle.red, label="투표 종료")
        self.vote_view = vote_view

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.vote_view.author.id:
            await interaction.response.send_message("투표를 생성한 사람만 종료할 수 있습니다.", ephemeral=True)
            return

        if not self.vote_view.is_active:
            await interaction.response.send_message("이미 종료된 투표입니다.", ephemeral=True)
            return

        self.vote_view.is_active = False
        
        for item in self.vote_view.children:
            item.disabled = True

        # 투표 종료 메시지 및 결과 전송
        result_embed = self.vote_view.create_result_embed()
        await interaction.response.edit_message(embed=self.vote_view.create_vote_embed(), view=self.vote_view)
        await interaction.followup.send(embed=result_embed)

class VoteCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def 투표(self, ctx: commands.Context, *, title: str = "투표"):
        """
        - 투표를 생성합니다. (!투표 [제목])
        """
        # 슬래시 커맨드가 아닌 일반 커맨드에서는 모달을 직접 보낼 수 없음
        # 대신 View를 사용하여 투표 생성
        view = VoteView(title, [], ctx.author)
        embed = discord.Embed(
            title=f"📊 {title}",
            description="투표 항목을 입력해주세요 (줄바꿈[shift+enter]으로 구분)",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)
        
        try:
            # 사용자의 다음 메시지를 기다림
            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel
            
            msg = await self.bot.wait_for('message', timeout=60.0, check=check)
            
            # 입력받은 항목들을 처리
            items = [item.strip() for item in msg.content.split('\n') if item.strip()]
            
            if len(items) < 2:
                await ctx.send("최소 2개 이상의 투표 항목이 필요합니다.")
                return
            
            # 투표 View 생성 및 전송
            view = VoteView(title, items, ctx.author)
            embed = discord.Embed(title=f"📊 {title}", color=discord.Color.blue())
            for i, item in enumerate(items, 1):
                embed.add_field(name=f"{i}. {item}", value="", inline=False)
            embed.set_footer(text="아래 버튼을 눌러 투표를 시작하세요.")
            
            await ctx.send(embed=embed, view=view)
            
        except asyncio.TimeoutError:
            await ctx.send("시간이 초과되었습니다. 다시 시도해주세요.")

async def setup(bot):
    await bot.add_cog(VoteCog(bot))