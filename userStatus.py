import discord

#ロール normal career zombie ghost

userStatus = {} #{userID, [p値,ロール文字列]}

def init_users(guild: discord.Guild):
    members = guild.members
    for member in members:
        if member.bot == False:
            userStatus[member.id]=[0,"normal",member.name]
    print("Init user status!")
    print(userStatus)

def init_career(careers):
    for career in careers:
        userStatus[career.id] = [userStatus[career.id][0],"career"]
    print("New career!")
    print(userStatus)
    #TODO :「感染者が出現しました！」アナウンス

def pollute(member: discord.Member, p:int):
    userStatus[member.id][0] += p
    #TODO :「汚染度が何%を超えました！」アナウンスとチェック
    

def message_pollution(message: discord.Message):
    author = message.author
    authorStatus = userStatus[author.id][1]
    if authorStatus == "career" or authorStatus=="zombie":
        pollute(author,1)