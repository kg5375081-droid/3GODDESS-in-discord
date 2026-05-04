import discord
from discord.ext import commands
import os
import json
from dotenv import load_dotenv

load_dotenv()

# Discord bot setup
# 보안을 위해 환경 변수에서 토큰을 가져오는 것을 권장합니다.
TOKEN = os.getenv("DISCORD_TOKEN")

# 봇의 권한(Intents) 설정
# 메시지 내용을 읽으려면 message_content가 반드시 True여야 합니다.
intents = discord.Intents.default()
intents.message_content = True 
intents.members = True  # 멤버 입장 이벤트를 감지하기 위해 필요합니다.

# 설정값
WELCOME_CHANNEL_ID = None  # 입장 메시지를 보낼 채널 ID를 여기에 입력하세요 (예: 123456789012345678)

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    if bot.user:
        print(f'✅ 로그인 완료: {bot.user.name} (ID: {bot.user.id})')
        print('------')

@bot.event
async def on_member_join(member):
    """새로운 멤버가 입장했을 때 실행되는 이벤트"""
    if WELCOME_CHANNEL_ID:
        channel = bot.get_channel(WELCOME_CHANNEL_ID)
        if isinstance(channel, discord.TextChannel):
            await channel.send(f"👋 안녕하세요, {member.mention}님! 우리 서버에 오신 것을 환영합니다!")
        else:
            print(f"⚠️ 설정된 채널 ID({WELCOME_CHANNEL_ID})가 텍스트 채널이 아니거나 찾을 수 없습니다.")
    else:
        print(f"ℹ️ {member.name}님이 입장했지만, WELCOME_CHANNEL_ID가 설정되지 않아 메시지를 보내지 못했습니다.")

@bot.command(name="상성")
async def compatibility(ctx):
    """상성 링크를 제공하는 명령어"""
    await ctx.send("https://gametora.com/ko/umamusume/compatibility")

@bot.command(name="카드비교")
async def card_compare(ctx):
    """카드 비교 링크를 제공하는 명령어"""
    await ctx.send("https://m.inven.co.kr/uma/compare/?col=6")
    await ctx.send("이곳에서 서포트카드를 비교하세요.😊") 
    
@bot.command(name="ping")
async def ping(ctx):
    """봇의 반응 속도를 확인하는 테스트 명령어"""
    await ctx.send(f"🏓 Pong! ({round(bot.latency * 1000)}ms)")

@bot.command(name="육성마")
async def yukseongma(ctx, *, query: str | None = None):
    """육성마 관련 정보를 검색하고 상세 적성을 보여주는 명령어"""
    print(f"DEBUG: Command !육성마 received with query: '{query}'")
    data_path = "yukseongma_data_with_aptitude.json"
    
    # Load data
    data = {}
    if os.path.exists(data_path):
        print(f"DEBUG: Found data file: {data_path}")
        with open(data_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                print(f"DEBUG: Loaded {len(data)} keys from JSON")
            except json.JSONDecodeError:
                print("DEBUG: JSON decode error!")
                data = {}
    else:
        print(f"DEBUG: Data file NOT found: {data_path}")
    
    if query:
        print(f"DEBUG: Searching for query: '{query}'")
        # Check for index at the end (e.g., "Name 1")
        parts = query.rsplit(' ', 1)
        search_query = query
        index_val = None
        
        if len(parts) == 2 and parts[1].isdigit() and parts[0].strip():
            search_query = parts[0].replace(" ", "")
            index_val = int(parts[1])
    
        found_key = None
        for key in data.keys():
            if search_query in key:
                found_key = key
                break
        
        if found_key:
            print(f"DEBUG: Found key: '{found_key}', index_val: {index_val}")
            variations = data[found_key]
            target_variation = None
            index_error = False
            
            if index_val is not None:
                print(f"DEBUG: Attempting to get variation index {index_val}")
                if 1 <= index_val <= len(variations):
                    target_variation = variations[index_val - 1]
                else:
                    await ctx.send(f"❌ {index_val}번 변형이 목록에 없습니다.")
                    index_error = True
            else:
                # Try to find the specific variation if user typed the title
                print(f"DEBUG: No index, searching title with query: '{query}'")
                for var in variations:
                    if query in var.get('title', ''):
                        target_variation = var
                        break
            
            if target_variation:
                # 1. 특정 제목이 매칭된 경우 (상세 정보 출력)
                embed = discord.Embed(
                    title=target_variation.get('title', '정보 없음'),
                    url=target_variation.get('url', ''),
                    color=discord.Color.blue()
                )
                embed.set_author(name=found_key)
                
                # Aptitude formatting
                track = target_variation.get('track_aptitude', {})
                dist = target_variation.get('distance_aptitude', {})
                strat = target_variation.get('strategy_aptitude', {})
    
                track_str = ", ".join([f"{k}{v}" for k, v in track.items()]) if track else "없음"
                dist_str = ", ".join([f"{k}{v}" for k, v in dist.items()]) if dist else "없음"
                strat_str = ", ".join([f"{k}{v}" for k, v in strat.items()]) if strat else "없음"
    
                embed.add_field(name="🏟️ 경기장 적성", value=track_str or "없음", inline=True)
                embed.add_field(name="📏 거리 적성", value=dist_str or "없음", inline=True)
                embed.add_field(name="🏃 각질 적성", value=strat_str or "없음", inline=True)
                
                await ctx.send(embed=embed)
            elif not index_error:
                # 2. 제목 매칭이 없는 경우 (변형 목록 출력)
                response = f"🔍 **{found_key}**에 대한 검색 결과입니다:\n"
                for i, var in enumerate(variations, 1):
                    response += f"{i}. {var.get('title', '제목 없음')}\n"
                await ctx.send(response)
        else:
            await ctx.send(f"❌ '{search_query}'에 대한 검색 결과가 없습니다.")
    else:
        await ctx.send("🔍 사용법: `!육성마 [이름]` 또는 `!육성마 [이름] [번호]`")

if __name__ == "__main__":
    if not TOKEN:
        print("❌ 오류: DISCORD_TOKEN이 설정되지 않았습니다. .env 파일을 확인하세요.")
    else:
        bot.run(TOKEN)