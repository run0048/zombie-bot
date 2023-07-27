from discord.ext import commands
import discord
import userStatus

from dotenv import load_dotenv
load_dotenv()
import os

TOKEN = os.getenv("TOKEN")
GUILD_ID = os.getenv("GUILD_ID")

intents = discord.Intents.default()
intents.members = True # メンバー管理の権限
intents.message_content = True # メッセージの内容を取得する権限
intents.guilds = True #サーバー管理の権限

# Botをインスタンス化
bot = commands.Bot(
    command_prefix="$", # $コマンド名　でコマンドを実行できるようになる
    case_insensitive=True, # コマンドの大文字小文字を区別しない ($hello も $Hello も同じ!)
    intents=intents # 権限を設定
)

client = discord.Client(intents=intents)
guild = client.get_guild(GUILD_ID)

@bot.event
async def on_ready():
    print("Bot is ready!")

@bot.event
async def on_guild_available(guild):
    print("Create role!")
    await guild.create_role(name="Career")
    userStatus.init_users(guild)


@bot.event
async def on_message(message: discord.Message):
    """メッセージをおうむ返しにする処理"""

    if message.author.bot: # ボットのメッセージは無視
        return

    #新しいcareerコマンド
    if "!career" in message.content:
        userStatus.init_career(message.mentions)

    #career汚染度
    userStatus.message_pollution(message)

    await message.reply(message.content)


bot.run(TOKEN)