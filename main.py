import discord
import asyncio
import os
import iron_cache
from rss import RSSFeed

client = discord.Client()
feed = RSSFeed()    # Initialize RSS-scraper, see rss.py for config.

# CONFIG #
# If you have set your token as an environment variable
TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
# Uncomment this instead if you'd like to specify it here
# TOKEN = "YOUR_TOKEN"
# Roles that users can assign themselves to, must be lower case.
AVAILABLE_ROLES = [
    "programmer",
    "designer",
    "artist",
    "sound designer"
]
# Default role for new members of server, must be lower case.
DEFAULT_ROLE = "godotians"
# Channel ID where bot will post github notifications
COMMIT_CHANNEL = "225147946109370369"
ISSUE_CHANNEL = "225146729509552128"
FORUM_CHANNEL = "246571722965385216"
# COMMIT_CHANNEL = "225071177721184256"
# ISSUE_CHANNEL = COMMIT_CHANNEL
# Message that bot returns on !help
HELP_STRING = """
:book: **Commands:**
!assign [role]: *assign yourself to one of the available roles.*\n
!unassign [role]: *unassign yourself from a role.*\n
!roles: *list available roles.*"""
# \n
# !xp: *show your current xp (beta)*
# Seconds to wait between checking RSS feeds and API
COMMIT_TIMEOUT = 8
FORUM_TIMEOUT = 10
ISSUE_TIMEOUT = 61
# How long to wait to delete messages
FEEDBACK_DEL_TIMER = 5
# How much XP to give on each messages
BASE_XP = 1

cache = iron_cache.IronCache()


async def delete_edit_timer(msg, time, error=False, call_msg=None):
    ws = ":white_small_square:"
    bs = ":black_small_square:"
    for i in range(time + 1):
        await client.edit_message(
            msg, msg.content + "\n" + ws * (time - i) + bs * i
        )
        await asyncio.sleep(1)
    await client.delete_message(msg)
    if call_msg:
        try:
            await client.delete_message(call_msg)
        except:
            print("Call message does not exist.")


@client.event
async def on_ready():
    print("Logged in as: {0}--{1}".format(client.user.name, client.user.id))
    print("------")


async def forum_checker():
    await client.wait_until_ready()
    channel = discord.Object(id=FORUM_CHANNEL)
    while not client.is_closed:
        try:
            fstamp = cache.get(cache="godot_git_stamps", key="forum").value
        except:
            fstamp = "missing"
            print("No stamp found for forum.")
        f_msg, stamp = feed.check_forum(fstamp)
        if not fstamp == stamp:
            try:
                cache.put(cache="godot_git_stamps", key="forum", value=stamp)
            except:
                print("Error setting stamp on ironcache.")
                return False
        if f_msg:
            async for log in client.logs_from(channel, limit=20):
                if log.content == f_msg:
                    print("Forum thread already posted, abort!")
                    break
            else:
                await client.send_message(channel, f_msg)
        await asyncio.sleep(FORUM_TIMEOUT)


async def commit_checker():
    await client.wait_until_ready()
    channel = discord.Object(id=COMMIT_CHANNEL)
    while not client.is_closed:
        try:
            cstamp = cache.get(cache="godot_git_stamps", key="commit").value
        except:
            cstamp = "missing"
            print("No stamp found for commits.")
        c_msg, stamp = feed.check_commit(cstamp)
        # c_msg = False
        if not cstamp == stamp:
            try:
                cache.put(cache="godot_git_stamps", key="commit", value=stamp)
            except:
                print("Error setting stamp on ironcache.")
                return False
        if c_msg:
            async for log in client.logs_from(channel, limit=20):
                if log.content == c_msg:
                    print("Commit already posted, abort!")
                    break
            else:
                await client.send_message(channel, c_msg)
        await asyncio.sleep(COMMIT_TIMEOUT)

async def issue_checker():
    await client.wait_until_ready()
    channel = discord.Object(id=ISSUE_CHANNEL)
    while not client.is_closed:
        try:
            cstamp = cache.get(cache="godot_git_stamps", key="issue").value
        except:
            cstamp = "missing"
            print("No stamp found for issues.")
        i_msgs, stamp = feed.check_issue(cstamp)
        if not cstamp == stamp:
            try:
                cache.put(cache="godot_git_stamps", key="issue", value=stamp)
            except:
                print("Error settings stamp on ironcache.")
                return False
        if i_msgs:
            async for log in client.logs_from(channel, limit=20):
                for msg in i_msgs:
                    if log.content == msg:
                        print("Issue already posted, removing!")
                        i_msgs.remove(msg)
            for msg in i_msgs:
                await client.send_message(channel, msg)
        await asyncio.sleep(ISSUE_TIMEOUT)


@client.event
async def on_message(message):
    id = message.author.id
    # if message.author.id == client.user.id:
    #     print("Not granting XP to bot.")
    # else:
    #     try:
    #         cache.increment(cache="godot_userxp", key=id, amount=BASE_XP)
    #     except:
    #         print("No cache point for user {0} with id {1}".format(
    #             message.author.name, message.author.id
    #         ))
    #         cache.put(cache="godot_userxp", key=id, value=BASE_XP)

    if message.channel.name != "botspam":
        return

    if message.content.startswith("!help"):
        await client.send_message(message.channel, HELP_STRING)
        await client.delete_message(message)

    # elif message.content.startswith("!xp"):
    #     s = message.content.rstrip()[6:-1]
    #     tmp = None
    #     if not len(s):
    #         try:
    #             xp = cache.get(cache="godot_userxp", key=id).value
    #         except:
    #             xp = 0
    #         tmp = await client.send_message(
    #             message.channel, "**{0}**'s current xp: **[{1}]**".format(
    #                 message.author.name, xp
    #             )
    #         )
    #     elif not message.content[3] == " ":
    #         tmp = await client.send_message(
    #             message.channel,
    #             "Usage: !xp or !xp @username"
    #         )
    #     else:
    #         try:
    #             int(s)
    #         except TypeError:
    #             tmp = await client.send_message(
    #                 message.channel,
    #                 "Usage: !xp or !xp @username"
    #             )
    #         else:
    #             try:
    #                 u = message.server.get_member(s)
    #             except:
    #                 tmp = await client.send_message(
    #                     message.channel, "Member not found..."
    #                 )
    #                 print(client.user.id)
    #             else:
    #                 if not u:
    #                     # print(client.user.id, type(client.user.id))
    #                     print("No user from server.")
    #                     tmp = await client.send_message(
    #                         message.channel, "Member not found..."
    #                     )
    #                 else:
    #                     try:
    #                         xp = cache.get(cache="godot_userxp", key=s).value
    #                     except:
    #                         tmp = await client.send_message(
    #                             message.channel, "Member has no XP yet..."
    #                         )
    #                     else:
    #                         tmp = await client.send_message(
    #                             message.channel, "**{0}**'s current xp: **[{1}]**".format(
    #                                 u.name, xp
    #                             )
    #                         )
    #         print("#" * 30)
    #         print(s)
    #         print("#" * 30)
    #         # message.server.get_member_named(name)
    #
    #     if tmp:
    #         # 195659861600501761
    #         await delete_edit_timer(
    #             tmp, FEEDBACK_DEL_TIMER, error=True, call_msg=message
    #         )
    #     else:
    #         await client.delete_message(message)

    elif message.content.startswith("!assign"):
        s = message.content[8:]     # remove !assign
        if not len(s) or not message.content[7] == " ":
            tmp = await client.send_message(
                message.channel,
                "Usage: !assign [role]"
            )
            await delete_edit_timer(
                tmp, FEEDBACK_DEL_TIMER, error=True, call_msg=message
            )
        else:
            newrole = s
            roles = message.server.roles
            for r in roles:
                if r.name.lower() == newrole.lower():
                    if r.name.lower() in AVAILABLE_ROLES:
                        if r not in message.author.roles:
                            await client.add_roles(message.author, r)
                            tmp = await client.send_message(
                                message.channel,
                                ":white_check_mark: User {0} added to {1}.".format(
                                    message.author.name, r.name
                                )
                            )
                            await delete_edit_timer(
                                tmp, FEEDBACK_DEL_TIMER, call_msg=message
                            )
                        else:
                            tmp = await client.send_message(
                                message.channel,
                                "You already have that role."
                            )
                            await delete_edit_timer(
                                tmp, FEEDBACK_DEL_TIMER,
                                error=True, call_msg=message
                            )
                    else:
                        tmp = await client.send_message(
                            message.channel,
                            ":no_entry: *You're not allowed to assign yourself to that role.*"
                        )
                        await delete_edit_timer(
                            tmp, FEEDBACK_DEL_TIMER, error=True,
                            call_msg=message
                        )
                    break
            else:
                tmp = await client.send_message(
                    message.channel,
                    ":no_entry: **{0}** <- *Role not found.*".format(
                        newrole.upper()
                    )
                )
                await delete_edit_timer(
                    tmp, FEEDBACK_DEL_TIMER, error=True, call_msg=message
                )

    elif message.content.startswith("!unassign"):
        s = message.content[10:]     # remove !unassign
        if not len(s) or not message.content[9] == " ":
            tmp = await client.send_message(
                message.channel,
                "Usage: !unassign [role]"
            )
            await delete_edit_timer(tmp, FEEDBACK_DEL_TIMER, call_msg=message)
        else:
            oldrole = s
            roles = message.server.roles
            for r in message.author.roles:
                # print(r.name.lower())
                if r.name.lower() == oldrole.lower():
                    # print(r.name, "<-FOUND")
                    await client.remove_roles(message.author, r)
                    tmp = await client.send_message(
                        message.channel, ":white_check_mark: Role was removed."
                    )
                    await delete_edit_timer(
                        tmp, FEEDBACK_DEL_TIMER, call_msg=message
                    )
                    break
            else:
                tmp = await client.send_message(
                    message.channel,
                    ":no_entry: **{0}** <- You don't have that role.".format(
                        oldrole.upper()
                    )
                )
                await delete_edit_timer(
                    tmp, FEEDBACK_DEL_TIMER, error=True, call_msg=message
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
        await client.delete_message(message)


@client.event
async def on_member_join(member):
    for r in member.server.roles:
        if r.name.lower() == DEFAULT_ROLE.lower():
            print("Adding default role to user.")
            await client.add_roles(member, r)
            break
    else:
        print("DEFAULT ROLE NOT FOUND ON SERVER!")


client.loop.create_task(commit_checker())
client.loop.create_task(issue_checker())
client.loop.create_task(forum_checker())
client.run(TOKEN)
