import discord
import datetime

#ロール Normal Career Zombie Ghost

usersStatus = {} #{userID, [p値,ロール文字列,name]}
careerList = [] #[userID]
roles = {} #{ロール名：　discord.Role}

def init_users(guild: discord.Guild):
    members = guild.members
    for member in members:
        if member.bot == False:
            usersStatus[member.id]=[0,"Normal",member.name]

    print("Init user status!")
    print(usersStatus)

def new_user(member: discord.Member):
    if member.bot == False:
        usersStatus[member.id] = [0,"Normal",member.name]
        print("New member! Welcome "+member.name+"!")

def out_user(member: discord.Member):
    if member.bot == False:
        del usersStatus[member.id]

def init_career(career: discord.Member):
    status = usersStatus[career.id]
    usersStatus[career.id] = [status[0],"Career",status[2]]
    careerList.append(career.id)
    print("New career!")
    print(usersStatus)
    #TODO :「感染者が出現しました！」アナウンス

def init_role(role: discord.Role):
    roles[role.name] = role

def init_announce(annouce):
    global announceChannel
    announceChannel = annouce


async def pollute(member: discord.Member, p:int):
    status = usersStatus[member.id]
    userP = status[0] + p
    userRole = status[1]
    usersStatus[member.id][0] = userP
    if (userP == 90 or userP == 91) and userRole == "Career":
        await member.send("# Warning! You will become Zombie soon! Your pollution degree is "+str(userP)+"!")
    if (userP == 190 or userP == 191) and (userRole == "Zombie" or userRole == "Zombie(static)"):
        await member.send("# Warning! You will become Ghost soon and then can't send message and speak in VC! Your pollution degree is "+str(userP)+"!")
    if userP >= 100 and userRole == "Career":
        usersStatus[member.id][1] = "Zombie"
        await member.add_roles(roles["Zombie"])
        await member.remove_roles(roles["Career"])
        await announceChannel.send("# Warning! "+status[2]+" became Zombie!")
    if userP >= 100 and userRole == "Normal":
        usersStatus[member.id][1] = "Zombie"
        await member.add_roles(roles["Zombie"])
        await announceChannel.send("# Warning! "+status[2]+" became Zombie!")
    if userP >= 200 and (userRole == "Zombie" or userRole == "Zombie(static)"):
        usersStatus[member.id][1] = "Ghost"
        await member.add_roles(roles["Ghost"])
        await member.remove_roles(roles["Zombie"])
        await member.edit(mute=True)
        await announceChannel.send("# Amen! "+status[2]+" passed away and became Ghost!\n# He can't speak tomorrow")
    if userP == 260 and (userRole == "Ghost" or userRole == "Ghost(static)"):
        await member.edit(deafen=True)
        await announceChannel.send("# Ghost "+status[2]+" run out of power and can't hear voice!")
        await member.send("You run out of power and can't hear voice today")

    #TODO :「汚染度が何%を超えました！」アナウンスとチェック
    

async def message_pollution(message: discord.Message):
    author = message.author
    authorStatus = usersStatus[author.id][1]
    if authorStatus == "Career" or authorStatus=="Zombie" or authorStatus=="Zombie(static)":
        await pollute(author,2)
    if message.reference != None:
        if type(message.reference.resolved)==discord.Message:
            replyedMember = message.reference.resolved.author
            if replyedMember.bot == False:
                replyedMemberStatus = usersStatus[replyedMember.id][1]
                if authorStatus == "Normal" and (replyedMemberStatus == "Zombie" or replyedMemberStatus == "Zombie(static)"):
                    await pollute(author,2)

async def reaction_pollution(reactedMember: discord.Member, reactMember: discord.Member):
    reactMemberStatus = usersStatus[reactMember.id][1]
    if reactedMember.bot == False:
        reactedMemberStatus = usersStatus[reactedMember.id][1]
        if reactMemberStatus == "Normal" and (reactedMemberStatus == "Zombie" or reactedMemberStatus == "Zombie(static)"):
            await pollute(reactMember,2)

async def purify(member: discord.Member):
    status = usersStatus[member.id]
    userRole = status[1]
    if userRole == "Career" or userRole == "Normal":
        usersStatus[member.id][0] = 0
    elif userRole == "Zombie(static)":
        usersStatus[member.id][0] = 0
        await member.remove_roles(roles["Zombie"])
        if member.id in careerList:
            usersStatus[member.id][1] = "Career"
            await member.add_roles(roles["Career"])
        else:
            usersStatus[member.id][1] = "Normal"
    elif userRole == "Zombie":
        usersStatus[member.id][1] = "Zombie(static)"
    elif userRole == "Ghost(static)":
        usersStatus[member.id][0] = 0
        await member.remove_roles(roles["Ghost"])
        await member.edit(mute=False)
        await member.edit(deafen=False)
        if member.id in careerList:
            usersStatus[member.id][1] = "Career"
            await member.add_roles(roles["Career"])
        else:
            usersStatus[member.id][1] = "Normal"
    elif userRole == "Ghost":
        usersStatus[member.id][1] = "Ghost(static)"
    await announceChannel.send("# Midnight Update\n"+printStatus(member))
    
async def midnight_check(guild: discord.Guild):
    for userID in usersStatus:
        user = guild.get_member(userID)
        await purify(user)


def printStatus(member: discord.Member):
    status = usersStatus[member.id]
    return "## "+status[2]+"'s status"+"\n**Role:** "+status[1]+"\n**Pollution degree:** "+str(status[0])