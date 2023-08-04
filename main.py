from discord.ext import commands
import discord
import userStatus
import timeSchedule
import vcStatus

from dotenv import load_dotenv
load_dotenv()
import os


TOKEN = os.getenv("TOKEN")


intents = discord.Intents.default()
intents.members = True # メンバー管理の権限
intents.message_content = True # メッセージの内容を取得する権限
intents.guilds = True #サーバー管理の権限
intents.voice_states = True #VC関連の権限
intents.moderation = True #time out の権限

# Botをインスタンス化
bot = commands.Bot(
    command_prefix="$", # $コマンド名　でコマンドを実行できるようになる
    case_insensitive=True, # コマンドの大文字小文字を区別しない ($hello も $Hello も同じ!)
    intents=intents # 権限を設定
)

client = discord.Client(intents=intents)



@bot.event
async def on_ready():
    print("Bot is ready!")

@bot.event
async def on_guild_available(guild):
    global myGuild
    myGuild = guild
    print("Create role!")
    global careerRole
    global zombieRole
    global ghostRole
    careerRole = await guild.create_role(name="Career",colour=discord.Colour.brand_green())
    zombieRole = await guild.create_role(name="Zombie",colour=discord.Colour.dark_purple())
    ghostRole = await guild.create_role(name="Ghost",colour=discord.Colour.dark_blue())
    userStatus.init_role(careerRole)
    userStatus.init_role(zombieRole)
    userStatus.init_role(ghostRole)
    userStatus.init_users(guild)
    await timeSchedule.time_schedule(guild)

@bot.event
async def on_member_join(member):
    userStatus.new_user(member)

@bot.event
async def on_member_remove(member):
    userStatus.out_user(member)

@bot.event
async def on_message(message: discord.Message):
    """メッセージをおうむ返しにする処理"""

    if message.author.bot: # ボットのメッセージは無視
        return

    #career汚染度
    await userStatus.message_pollution(message)

    status = userStatus.usersStatus[message.author.id][1]
    if status == "Ghost" or status == "Ghost(static)":
        print("delete")
        await message.delete() 

    #新しいcareerコマンド
    if "!career" in message.content:
        for mention in message.mentions:
            if mention == message.author or message.author.guild_permissions.administrator:
                userStatus.init_career(mention)
                await mention.add_roles(careerRole)
        announceChannel= message.channel
        userStatus.init_announce(announceChannel)

    if "!p" in message.content:
        await message.channel.send(userStatus.printStatus(message.author))

    if "!status" in message.content:
        for id in userStatus.usersStatus.keys():
            member = myGuild.get_member(id)
            await message.channel.send(userStatus.printStatus(member))

    #100だけ汚染させる 管理者コマンド
    if "!pollute" in message.content:
        if not message.author.guild_permissions.administrator:
            return
        await userStatus.pollute(message.author,100)

    #ゾンビやゴーストを感染者を健常者に復活させる 管理者コマンド
    if "!refresh" in message.content:
        if not message.author.guild_permissions.administrator:
            return
        for mention in message.mentions:
            userStatus.careerList.remove(mention.id)
            for i in range(2):
                await userStatus.purify(mention)

    #作成したロールを消去させる 管理者コマンド
    if "!fin" in message.content:
        if not message.author.guild_permissions.administrator:
            return
        await careerRole.delete()
        await zombieRole.delete()
        await ghostRole.delete()


@bot.event
async def on_reaction_add(reaction: discord.Reaction, user: discord.Member):
    status = userStatus.usersStatus[user.id][1]
    if status == "Ghost" or status == "Ghost(static)":
        print("delete")
        await reaction.clear() 
    await userStatus.reaction_pollution(reaction.message.author, user)

once = True
@bot.event
async def on_voice_state_update(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
    if after.channel != None:
        if after.channel.id not in vcStatus.channels.keys():
            vcStatus.new_channel(after,member)
        elif before.channel == None:
            await vcStatus.in_member(after,member)
        else:
            vcStatus.update_member(after,member)
    else:
        vcStatus.out_member(before,member)
    
    global once
    if once:
        once = False
        await vcStatus.vc_time_schedule(myGuild)


bot.run(TOKEN)


