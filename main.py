import discord
import asyncio
import os
import glob
import random
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from rss import RSSFeed
from models import Base, User, Stamp

client = discord.Client()   # Initialize discord client
feed = RSSFeed()            # Initialize RSS-scraper, see rss.py for config.

# When running script, initialize db engine and create sqlite database
# with tables if not existing.
engine = create_engine("sqlite:///app.db")
# Session maker object, to instantiate sessions from
Session = sessionmaker(bind=engine)
# Ensure all tables are created.
print("Ensuring database scheme is up to date.")
Base.metadata.create_all(engine)

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

# Channel ID's
COMMIT_CHANNEL = "225147946109370369"
ISSUE_CHANNEL = "225147946109370369"
FORUM_CHANNEL = "246571722965385216"
QA_CHANNEL = "246571722965385216"
NEWCOMER_CHANNEL = "253576562136449024"

# Message that bot returns on !help
HELP_STRING = """
:book: **Commands:**
!assign [role]: *assign yourself to one of the available roles.*\n
!unassign [role]: *unassign yourself from a role.*\n
!roles: *list available roles.*\n
!rank: *show the 10 members with the most xp*"""

# Seconds to wait between checking feeds and stuff
COMMIT_TIMEOUT = 8
FORUM_TIMEOUT = 10
QA_TIMEOUT = 10
ISSUE_TIMEOUT = 61

# How long to wait to delete messages
FEEDBACK_DEL_TIMER = 5

# XP rank globals
RANK_MIN = 10
RANK_MAX = 25
RANK_SHRINK_DELAY = 30

# RMS is a beautiful man.
RMS_PATH = "rms"    # Folder where RMS memes are located.
RMS_MEMES = []


def populate_memes():
    """
    Retrieves all pictures in the RMS_PATH folder and sorts them by name
    """
    global RMS_MEMES
    memes = [
        glob.glob(
            os.path.join(RMS_PATH, e)
        ) for e in [
            '*.jpg', '*.JPG', '*.jpeg', '*.JPEG',
            '*.gif', '*.GIF', '*.png', '*.PNG'
        ]
    ]
    # "sorted" defaults to alphabetical on strings.
    RMS_MEMES = sorted([j for i in memes for j in i])


async def shrink_rank_list(msg):
    """
    Takes the message that was posted with ranks and shortens it after a while.
    """
    await asyncio.sleep(RANK_SHRINK_DELAY)
    sp = msg.content.split("\n")
    if len(sp) > RANK_MIN + 1:  #
        sp = [l + "\n" for l in sp[:RANK_MIN + 1]]
        edited_msg = ""
        for s in sp:
            edited_msg += s
    else:
        # Won't do anything if there's not enough ranks.
        edited_msg = msg.content
    await client.edit_message(msg, edited_msg)


async def delete_edit_timer(msg, time, error=False, call_msg=None):
    """
    Counts down by editing the response message, then deletes both that one and
    the original message.
    """
    ws = ":white_small_square:"
    bs = ":black_small_square:"

    for i in range(time + 1):
        await client.edit_message(
            msg, msg.content + "\n" + ws * (time - i) + bs * i
        )
        await asyncio.sleep(1)

    await client.delete_message(msg)

    if call_msg:
        # Prevent crash if the call message has been deleted before the bot
        # gets to it.
        try:
            await client.delete_message(call_msg)
        except:
            print("Call message does not exist.")


@client.event
async def on_ready():
    print("Logged in as: {0}--{1}".format(client.user.name, client.user.id))
    print("------")


# To check feeds, they all work basically the same here.
# They check the database for timestamps, if they don't exist they create new.
# They pass those stamps to feedchecker in rss.py, which returns a string or
# a list of strings, and a new stamp. The new stamp is then written back to the
# database, and if there's any strings returned it will post them as messages
# in their appropriate channels. Before posting the messages, they check if
# that exact message has been posted before, by iterating through the 20 last
# messages and comparing them.

async def qa_checker():
    await client.wait_until_ready()
    channel = discord.Object(id=QA_CHANNEL)

    while not client.is_closed:
        session = Session()
        qstamp = session.query(Stamp).filter_by(descriptor="qa").first()
        q_msg, stamp = feed.check_qa(qstamp.stamp if qstamp else "missing")

        if qstamp:
            if not qstamp.stamp == stamp:
                qstamp.stamp = stamp
        else:
            dbstamp = Stamp(descriptor="qa", stamp=stamp)
            session.add(dbstamp)
            print("Adding new stamp in database for Q&A")

        if q_msg:
            async for log in client.logs_from(channel, limit=20):
                if log.content == q_msg:
                    print("Q&A thread already posted, abort!")
                    break
            else:
                await client.send_message(channel, q_msg)

        session.commit()
        await asyncio.sleep(QA_TIMEOUT)

async def forum_checker():
    await client.wait_until_ready()
    channel = discord.Object(id=FORUM_CHANNEL)

    while not client.is_closed:
        session = Session()
        fstamp = session.query(Stamp).filter_by(descriptor="forum").first()
        f_msg, stamp = feed.check_forum(fstamp.stamp if fstamp else "missing")

        if fstamp:
            if not fstamp.stamp == stamp:
                fstamp.stamp = stamp
        else:
            # Creating new row for forum stamp
            dbstamp = Stamp(descriptor="forum", stamp=stamp)
            session.add(dbstamp)
            print("Adding new stamp in database for forum.")

        if f_msg:
            async for log in client.logs_from(channel, limit=20):
                if log.content == f_msg:
                    print("Forum thread already posted, abort!")
                    break
            else:
                await client.send_message(channel, f_msg)

        session.commit()
        await asyncio.sleep(FORUM_TIMEOUT)


async def commit_checker():
    await client.wait_until_ready()
    channel = discord.Object(id=COMMIT_CHANNEL)

    while not client.is_closed:
        session = Session()
        cstamp = session.query(Stamp).filter_by(descriptor="commit").first()
        c_msg, stamp = feed.check_commit(cstamp.stamp if cstamp else "missing")

        if cstamp:
            if not cstamp.stamp == stamp:
                # Updating stamp in db
                cstamp.stamp = stamp
        else:
            dbstamp = Stamp(descriptor="commit", stamp=stamp)
            session.add(dbstamp)
            print("Adding new stamp to database for commits")

        if c_msg:
            async for log in client.logs_from(channel, limit=20):
                if log.content == c_msg:
                    print("Commit already posted, abort!")
                    break
            else:
                await client.send_message(channel, c_msg)

        session.commit()
        await asyncio.sleep(COMMIT_TIMEOUT)

async def issue_checker():
    await client.wait_until_ready()
    channel = discord.Object(id=ISSUE_CHANNEL)

    while not client.is_closed:
        session = Session()
        istamp = session.query(Stamp).filter_by(descriptor="issue").first()
        i_msg, stamp = feed.check_issue(istamp.stamp if istamp else "missing")

        if istamp:
            if not istamp.stamp == stamp:
                # Updating stamp in db
                istamp.stamp = stamp
        else:
            dbstamp = Stamp(descriptor="issue", stamp=stamp)
            session.add(dbstamp)
            print("Adding new stamp to database for issues")

        if i_msg:
            async for log in client.logs_from(channel, limit=20):
                for msg in i_msg:
                    if log.content == msg:
                        print("Issue already posted, removing!")
                        i_msg.remove(msg)
            for msg in i_msg:
                await client.send_message(channel, msg)

        session.commit()
        await asyncio.sleep(ISSUE_TIMEOUT)


@client.event
async def on_message(message):
    id = message.author.id

    # This was an easter egg by karroffel:
    #if message.author.id == "195659861600501761":
    #    await client.add_reaction(message, "🐖")

    if message.author.id == client.user.id:
        print("Not granting XP to bot.")
    elif message.content.startswith("!"):
        # Don't give XP for bot commands.
        print("Ignoring message as a command, no xp.")
    else: 
        xp = 1 + len(message.content) // 80
        session = Session()
        # Check if the user exists in the database and update the xp column.
        # If user doesn't exist, create row.
        if session.query(User).filter_by(userid=id).first():
            session.query(User).filter_by(userid=id).update(
                {"xp": User.xp + xp}
            )
            print("Awarded {0} xp to {1}".format(xp, message.author.name))
        else:
            print("Creating new user row for {0}".format(id))
            u = User(userid=id, xp=xp)
            session.add(u)

        session.commit()

    # Posts a picture of RMS.
    if message.content.lower().startswith("!rms"):
        choice_error = False
        fpath = None
        c = message.content[5:]

        if not len(c.strip()) or not message.content[4] == " ":
            choice_error = True

        try:
            c = int(c.strip())
            if c > 0 and c <= len(RMS_MEMES):
                fpath = RMS_MEMES[c - 1]
            else:
                choice_error = True
        except ValueError:
            choice_error = True

        if choice_error:
            # choice_error occurs when a valid integer hasn't been supplied
            # or it's out of bounds. This will pick a random image instead.
            rand_c = random.randint(0, len(RMS_MEMES) - 1)
            c = rand_c + 1  # c is the number which we will post alongside img.
            fpath = RMS_MEMES[rand_c]

        if fpath:
            with open(fpath, "rb") as f:
                await client.send_file(message.channel, f, content="**#{0}:**".format(c))

    if message.channel.name != "botspam":
        return  # Ignore command if it's not written in botspam channel

    # Send help message.
    if (
        message.content.startswith("!help") or
        message.content.startswith("!commands")
    ):
        await client.send_message(message.channel, HELP_STRING)
        await client.delete_message(message)

    elif message.content.startswith("!rank"):
        # Get's the top ranking users by their xp and posts a list of them.
        session = Session()
        ranks = session.query(User).order_by(User.xp.desc()).all()
        ranks = ranks[:RANK_MAX]    # Slice. Perhaps use SQLAlchemy for this.
        msg = "**XP leaderboard:**"

        for u in ranks:
            m = message.server.get_member(u.userid)
            if m:
                name = m.nick if m.nick else m.name
                msg += "\n{0}: **{1}**".format(name, u.xp)

        session.commit()

        tmp = await client.send_message(message.channel, msg)
        await client.delete_message(message)
        await shrink_rank_list(tmp)

    # Show a list of assignable roles.
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

    # Attempt to assign the user to a role.
    elif (
        message.content.startswith("!assign") or
        message.content.startswith("!set") or
        message.content.startswith("!role")
    ):
        # TODO Unassign all roles.
        error = False

        # Have to slice the message depending on the command alias given.
        if message.content.startswith("!assign"):
            s = message.content[8:]     # remove !assign
            if not len(s) or not message.content[7] == " ":
                error = True
        elif message.content.startswith("!set"):
            s = message.content[5:]
            if not len(s) or not message.content[4] == " ":
                error = True
        elif message.content.startswith("!role"):
            s = message.content[6:]
            if not len(s) or not message.content[5] == " ":
                error = True

        if error:
            # If a valid role hasn't been supplied.
            tmp = await client.send_message(
                message.channel,
                "Usage: !assign [role]"
            )
            await delete_edit_timer(
                tmp, FEEDBACK_DEL_TIMER, error=True, call_msg=message
            )
        else:
            # This looks messy, but it works. There must be a more effective
            # method of getting the role object rather than iterating over
            # all available roles and checking their name.
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

    elif (
        message.content.startswith("!unassign") or
        message.content.startswith("!remove")
    ):
        error = False

        # It's the same here that it was with !assign
        if message.content.startswith("!unassign"):
            s = message.content[10:]     # remove !unassign
            if not len(s) or not message.content[9] == " ":
                error = True
        elif message.content.startswith("!remove"):
            s = message.content[8:]     # remove !remove
            if not len(s) or not message.content[7] == " ":
                error = True

        if error:
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


@client.event
async def on_member_join(member):
    # Actions to take when a new member joins the server.
    channel = discord.Object(id=NEWCOMER_CHANNEL)
    msg = ":new: {0} joined the server. Current member count: **{1}**".format(
        member.mention, member.server.member_count
    )
    await client.send_message(channel, msg)


# Prepare for takeoff.
populate_memes()
client.loop.create_task(commit_checker())
client.loop.create_task(issue_checker())
client.loop.create_task(forum_checker())
client.loop.create_task(qa_checker())
client.run(TOKEN)   # And we have liftoff.
