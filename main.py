import discord
import asyncio
import os
from rss import RSSFeed

client = discord.Client()
feed = RSSFeed()    # Initialize RSS-scraper, see rss.py for config.

### CONFIG ###
# If you have set your token as an environment variable
TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
# Uncomment this instead if you'd like to specify it here
# TOKEN = "YOUR_TOKEN"
# Roles that users can assign themselves to, must be lower case.
AVAILABLE_ROLES = [
    "programmer",
    "designer",
    "artist"
]
# Default role for new members of server, must be lower case.
DEFAULT_ROLE = "blue"
# Channel ID where bot will post github notifications
COMMIT_CHANNEL = "225147946109370369"
ISSUE_CHANNEL = "225146729509552128"
# Message that bot returns on !help
HELP_STRING = """
:book: **Commands:**
!assign [role]: *assign yourself to one of the available roles.*\n
!unassign [role]: *unassign yourself from a role.*\n
!roles: *list available roles.*
"""
# Seconds to wait between checking RSS feeds and API
COMMIT_TIMEOUT = 5
ISSUE_TIMEOUT = 30

@client.event
async def on_ready():
    print("Logged in as: {0}--{1}".format(client.user.name, client.user.id))
    print("------")

async def commit_checker():
    await client.wait_until_ready()
    channel = discord.Object(id=COMMIT_CHANNEL)
    while not client.is_closed:
        c_msg = feed.check_commit()
        if c_msg:
            await client.send_message(channel, c_msg)
        await asyncio.sleep(COMMIT_TIMEOUT)

async def issue_checker():
    await client.wait_until_ready()
    channel = discord.Object(id=ISSUE_CHANNEL)
    while not client.is_closed:
        i_msgs = feed.check_issue()
        for msg in i_msgs:
            await client.send_message(channel, msg)
        await asyncio.sleep(ISSUE_TIMEOUT)

@client.event
async def on_message(message):
    if message.content.startswith("!help"):
        await client.send_message(message.channel, HELP_STRING)

    elif message.content.startswith("!assign"):
        s = message.content.split()[1:] # remove !assign
        if not len(s) == 1:
            await client.send_message(
                message.channel,
                "Usage: !assign [role]"
            )
        else:
            newrole = s[0]
            roles = message.server.roles
            for r in roles:
                if r.name.lower() == newrole.lower():
                    if r.name.lower() in AVAILABLE_ROLES:
                        if not r in message.author.roles:
                            await client.add_roles(message.author, r)
                            await client.send_message(
                                message.channel, ":white_check_mark: User {0} added to {1}.".format(
                                    message.author.name, r.name
                                )
                            )
                        else:
                            await client.send_message(
                                message.channel,
                                "You already have that role."
                            )
                    else:
                        await client.send_message(
                            message.channel,
                            ":no_entry: *You're not allowed to assign yourself to that role.*"
                        )
                    break
            else:
                await client.send_message(
                    message.channel,
                    ":no_entry: **{0}** <- *Role not found.*".format(
                        newrole.upper()
                    )
                )

    elif message.content.startswith("!unassign"):
        s = message.content.split()[1:] # remove !assign
        if not len(s) == 1:
            await client.send_message(
                message.channel,
                "Usage: !unassign [role]"
            )
        else:
            oldrole = s[0]
            roles = message.server.roles
            for r in message.author.roles:
                # print(r.name.lower())
                if r.name.lower() == oldrole.lower():
                    # print(r.name, "<-FOUND")
                    await client.remove_roles(message.author, r)
                    await client.send_message(message.channel, ":white_check_mark: Role was removed.")
                    break
            else:
                await client.send_message(
                    message.channel,
                    ":no_entry: **{0}** <- You don't have that role.".format(
                        oldrole.upper()
                    )
                )
    elif message.content.startswith("!roles"):
        s = ":scroll: **Available roles:**\n"
        s += "```\n"
        for i, r in enumerate(AVAILABLE_ROLES):
            s += "{0}".format(r.upper())
            if not i == len(AVAILABLE_ROLES) - 1:
                s += ", "
        s += "```"
        await client.send_message(
            message.channel,
            s
        )


@client.event
async def on_member_join(m):
    for r in m.server.roles:
        if r.name.lower() == DEFAULT_ROLE.lower():
            await client.add_roles(m, r)


client.loop.create_task(commit_checker())
client.loop.create_task(issue_checker())
client.run(TOKEN)
