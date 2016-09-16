import discord
import asyncio
import os
client = discord.Client()

### CONFIG ###
# If you have set your token as an environment variable
TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
# Uncomment this instead if you'd like to specify it here
# TOKEN = "YOUR_TOKEN"

@client.event
async def on_ready():
    print("Logged in as: {0}--{1}".format(client.user.name, client.user.id))
    print("------")

@client.event
async def on_message(message):

    if message.content.startswith("!create_stamps"):
        if message.author.id == "175364770113781761":
            cr = client.create_role(message.server, name="cstamp")
            ir = client.create_role(message.server, name="istamp")
            msg = "Commit role ID: {0}\nIssue role ID: {1}".format(
                cr.id, ir.id
            )
            await client.send_message(message.channel, msg)
        await client.delete_message(message)


client.run(TOKEN)
