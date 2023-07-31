import userStatus

import schedule
import time
import asyncio
import discord


button = False

channels = {} #{channel_id: {member_id: [滞在時間, 状態]}} 状態：ミュートしてたらTrue してなかったら False 

def new_channel(voiceState: discord.VoiceState,member: discord.Member):
    channel = voiceState.channel
    mute = voiceState.mute or voiceState.self_mute
    memberDict = {member.id: [0, mute]}
    channels[channel.id] = memberDict

async def in_member(voiceState: discord.VoiceState,member: discord.Member):
    channel_id = voiceState.channel.id
    mute = voiceState.mute or voiceState.self_mute
    channels[channel_id][member.id] = [0, mute]
    status =userStatus.usersStatus[member.id][1]
    if status == "Zombie" or status == "Zombie(static)":
        for user in voiceState.channel.members:
            user_status = userStatus.usersStatus[user.id][1]
            if user_status == "Normal":
                await user.send("# Warning! Zombie "+member.name+" is comming! You will be polluted with Zombie!!")

def update_member(voiceState: discord.VoiceState,member: discord.Member):
    channel_id = voiceState.channel.id
    mute = voiceState.mute or voiceState.self_mute
    channels[channel_id][member.id][1] = mute

def out_member(voiceState: discord.VoiceState,member: discord.Member):
    if len(channels.keys()) == 0:
        return
    channel_id = voiceState.channel.id
    del channels[channel_id][member.id]

async def vc_pollution(guild: discord.Guild):
    for channel_id in channels.keys():
        members = channels[channel_id]
        for member_id in members.keys():
            status = userStatus.usersStatus[member_id][1]
            member_info = members[member_id]
            if member_info[0] > 0 and (status == "Career" or status == "Zombie" or status == "Zombie(static)" or status == "Ghost" or status == "Ghost(static)"):
                career = guild.get_member(member_id)
                if member_info[1]:
                    await userStatus.pollute(career,1)
                else:
                    await userStatus.pollute(career,2)
                for carried_id in members.keys():
                    status_carried = userStatus.usersStatus[carried_id][1]
                    carried_info = members[carried_id]
                    carried = guild.get_member(carried_id)
                    if carried_info[0] > 0 and status_carried=="Normal" and (status == "Zombie" or status == "Zombie(static)"):
                        if member_info[1]:
                            await userStatus.pollute(carried,1)
                        else:
                            await userStatus.pollute(carried,2)
            channels[channel_id][member_id][0] = channels[channel_id][member_id][0]+1
                    

def switch():
    global button
    button = True

async def vc_time_schedule(guild: discord.Guild):
    global button
    schedule.every(10).seconds.do(switch)
    #schedule.every(1).minutes.do(switch)
    while True:
        schedule.run_pending()
        if button == True:
            await vc_pollution(guild)
            print(channels)
            button = False
        await asyncio.get_event_loop().run_in_executor(
            None,
            time.sleep,
            1
        )