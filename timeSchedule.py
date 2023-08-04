import userStatus

import schedule
import time
import asyncio
import discord


button = False

def switch():
    global button
    button = True

async def time_schedule(guild: discord.Guild):
    global button
    #schedule.every(60).seconds.do(switch) #utc < jst 9時間
    schedule.every().days.at("00:00").do(switch)
    while True:
        schedule.run_pending()
        if button == True:
            print("hoge")
            await userStatus.midnight_check(guild)
            button = False
        await asyncio.get_event_loop().run_in_executor(
            None,
            time.sleep,
            1
        )