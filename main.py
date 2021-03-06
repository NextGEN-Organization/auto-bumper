import discord
import json
import asyncio
from threading import Thread

shouldRun = True

with open("config.json", "r") as settings:
    configFile = json.load(settings)
    debugVal = configFile['debug'] # Prompts debug messages if enabled.
    authorizedUserIDs = configFile['authorizedUserIDs']  # users who can use commands if authorized.
    superUserIDs = configFile['superUserIDs'] # Super users who can add other users.
    p = configFile['prefix']  # prefix if manual operation.
    mode = configFile['mode'] # set this to be automatic on startup or manual.
    channels = configFile['channels']  # optional if you're doing this manually.
    userToken = configFile['userToken'] # stores the token used to bump servers.


async def beginAutoBump():
    tasks = []
    for chanid in channels:
        tasks.append(sendMessages(chanid))
    await asyncio.gather(*tasks)


async def sendMessages(chanid):
    while True:
        global shouldRun
        if (shouldRun):
            try:
                channel = client.get_channel(chanid)
                await channel.send("!d bump")
                await debug("Sent a message in {0}".format(channel.id))
            except:
                print("Cannot send a message to channel {0}".format(chanid))
            await asyncio.sleep(7200)
        else:
            return


async def addSettings(message, content, target):
    try:
        value = int(content[1])
    except Exception:
        await message.channel.send("Invalid ID given.")
        return

    if (target == "channel"):
        with open("config.json", "r") as settings:
            config = json.load(settings)
            currentChannels = config['channels']
            if not(value in currentChannels):
                currentChannels.append(value)
                json.dump(config, open("config.json", "w"), indent=4)
        await message.channel.send("Successfully added channel.")

    elif (target == "user"):
        with open("config.json", "r") as settings:
            config = json.load(settings)
            authUsers = config['authorizedUserIDs']
            if not(value in authUsers):
                authUsers.append(value)
                json.dump(config, open("config.json", "w"), indent=4)
        await message.channel.send("Successfully added user.")
    return


async def removeSettings(message, content, target):
    try:
        value = int(content[1])
    except Exception:
        await message.channel.send("Invalid ID given.")
        return

    if (target == "channel"):
        with open("config.json", "r") as settings:
            config = json.load(settings)
            currentChannels = config['channels']
            if (value in currentChannels):
                currentChannels.remove(value)
            json.dump(config, open("config.json", "w"), indent=4)
        await message.channel.send("Successfully removed channel.")

    elif (target == "user"):
        with open("config.json", "r") as settings:
            config = json.load(settings)
            authUsers = config['authorizedUserIDs']
            if (value in authUsers):
                authUsers.remove(value)
            print(config)
            json.dump(config, open("config.json", "w"), indent=4)
        await message.channel.send("Successfully removed user.")
    return



async def stopAutoBump(message):
    global shouldRun
    shouldRun = False
    await message.channel.send("Auto-Bumping has stopped.")


async def help(message):
    await message.channel.send(f"""```
Your prefix: {p}
{p}help -> displays this message.
{p}begin -> starts the auto-bumper.
{p}stop -> stops the auto-bumper.
{p}add -> adds channels to the target list.
{p}del -> removes channels from the target list.
{p}adduser -> authorizes another user to use this script. REQUIRES SUPERUSER ACCESS.
{p}deluser -> Removes ID from authorized User list. REQUIRES SUPERUSER ACCESS.```""")



async def debug(value):
    if (debugVal):
        print("[DEBUG]: {0}".format(value))


class MyClient(discord.Client):
    async def on_message(self, message):
        content = message.content.split(' ')
        if (message.author.id) in (superUserIDs):
            if (content[0] == str(p) + "adduser"):
                await addSettings(message, content, "user")
            elif (content[0] == str(p) + "deluser"):
                await removeSettings(message, content, "user")
        if (message.author.id in authorizedUserIDs):
            if (content[0] == str(p) + "begin"):
                await beginAutoBump()
            elif (content[0] == str(p) + "add"):
                await addSettings(message, content, "channel")
            elif (content[0] == str(p) + "del"):
                await removeSettings(message, content, "channel")
            elif (content[0] == str(p) + "stop"):
                await stopAutoBump(message)
            elif (content[0] == str(p) + "help"):
                await help(message)


    async def on_connect(self):
        print("Welcome to the auto bumper. You can check your settings in the config file.\n")
        if (mode == "auto"):
            print("This script is in auto mode. The bots have started to send their messages automatically. There is no setup required.")
        elif (mode == "manual"):
            print("This script is in manual mode. The bots are awaiting your commands.\n Do {0}help for a command list.")
        else:
            print("The mode for this script is invalid. Assuming manual. Please change mode to \"auto\" under config.json")

        print("List of channels to bump: ")
        for channel in channels:
            try:
                channel = client.get_channel(channel)
                server = channel.guild
                print("   Channel ID: {0}\n   Channel name: {1}\n   Server name: {2}\n\n".format(channel.id, channel.name, server.name))
            except:
                print("   The account is not in the server with the channel {0}\n".format(channel))

        if (mode == "auto"):
            await beginAutoBump()

client = MyClient()
client.run(userToken, bot=False)
