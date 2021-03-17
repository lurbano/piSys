import time
import asyncio

async def basicTimer(server, mins, secs):
    timeLeft = int(mins*60 + secs)
    totTime = int(mins*60 + secs)
    print("Starting Timer: ", totTime)
    while timeLeft > 0:
        timeLeft -= 1
        m = timeLeft // 60
        s = timeLeft % 60
        server.write_message({"info": "timer", "m":m, "s":s})
        await asyncio.sleep(1)
    print("Timer Done.")
