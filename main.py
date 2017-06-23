import discord
import asyncio
import os
import glob
import random
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from rss import RSSFeed, GH_OBJECT, GH_COMMIT, GH_PR, GH_ISSUE, GH_QA, GH_FORUM
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
GENERAL_CHANNEL = "212250894228652034"

# URLs
COMMIT_URL = "https://github.com/godotengine/godot/commits/master.atom"
ISSUE_URL  = "https://api.github.com/repos/godotengine/godot/issues?sort=created"
DOC_COMMIT_URL = "https://github.com/godotengine/godot-docs/commits/master.atom"
DOC_ISSUE_URL = "https://api.github.com/repos/godotengine/godot-docs/issues?sort=created"
FORUM_URL  = "https://godotdevelopers.org/forum/discussions/feed.rss"
QA_URL     = "https://godotengine.org/qa/feed/questions.rss"

# Embed settings
MAX_DESC_LINES      =   4
EMBED_COMMIT_COLOR  =   0x1E54F8
EMBED_PR_COLOR      =   0x84D430
EMBED_ISSUE_COLOR   =   0xD44730
EMBED_QA_COLOR      =   0xF1E739
EMBED_FORUM_COLOR   =   0x3D81A6
EMBED_COMMIT_ICON   =   "https://cdnjs.cloudflare.com/ajax/libs/ionicons/2.0.1/png/512/clock.png"
EMBED_PR_ICON       =   "https://cdnjs.cloudflare.com/ajax/libs/ionicons/2.0.1/png/512/pull-request.png"
EMBED_ISSUE_ICON    =   "https://cdnjs.cloudflare.com/ajax/libs/ionicons/2.0.1/png/512/alert-circled.png"
EMBED_QA_ICON       =   "https://cdnjs.cloudflare.com/ajax/libs/ionicons/2.0.1/png/512/help-circled.png"
EMBED_FORUM_ICON    =   "https://cdnjs.cloudflare.com/ajax/libs/ionicons/2.0.1/png/512/chatbubbles.png"

# Message that bot returns on !help
HELP_STRING = """
:book: **Commands:**
!assign [role]: *assign yourself to one of the available roles.*\n
!unassign [role]: *unassign yourself from a role.*\n
!roles: *list available roles.*\n
!xp: *shows your current xp*\n
!rank: *show the 10 members with the most xp*"""

# Seconds to wait between checking feeds and stuff
COMMIT_TIMEOUT = 8
ISSUE_TIMEOUT = 66
DOC_COMMIT_TIMEOUT = 60
DOC_ISSUE_TIMEOUT = 660
FORUM_TIMEOUT = 10
QA_TIMEOUT = 10

# How long to wait to delete messages
FEEDBACK_DEL_TIMER = 5

# XP rank globals
RANK_MIN = 10
RANK_MAX = 25
RANK_SHRINK_DELAY = 30

# RMS is a beautiful man.
RMS_PATH = "rms"    # Folder where RMS memes are located.
RMS_MEMES = []

EMBED_ROSS_ICON = "http://i.imgur.com/OZLdaSn.png"
EMBED_ROSS_COLOR = 0x000F89
ROSS_QUOTES = [
    "There’s nothing wrong with having a tree as a friend.",
    "The secret to doing anything is believing that you can do it. Anything that you believe you can do strong enough, you can do. Anything. As long as you believe.",
    "We don’t make mistakes. We just have happy accidents.",
    "I think there’s an artist hidden at the bottom of every single one of us.",
    "You too can paint almighty pictures.",
    "No pressure. Just relax and watch it happen.",
    "Don’t forget to make all these little things individuals — all of them special in their own way.",
    "Find freedom on this canvas.",
    "It’s so important to do something every day that will make you happy.",
    "Talent is a pursued interest. Anything that you’re willing to practice, you can do.",
    "Make love to the canvas.",
    "[Painting] will bring a lot of good thoughts to your heart.",
    "We artists are a different breed of people. We’re a happy bunch.",
    "We want happy paintings. Happy paintings. If you want sad things, watch the news.",
    "That’s a crooked tree. We’ll send him to Washington.",
    "Every day is a good day when you paint.",
    "I think each of us, sometime in our life, has wanted to paint a picture.",
    "We tell people sometimes: We’re like drug dealers, come into town and get everybody absolutely addicted to painting. It doesn’t take much to get you addicted.",
    "They say everything looks better with odd numbers of things. But sometimes I put even numbers — just to upset the critics.",
    "Gotta give him a friend. Like I always say, ‘Everyone needs a friend.’",
    "See how it fades right into nothing. That’s just what you’re looking for.",
    "If I paint something, I don’t want to have to explain what it is.",
    "Water’s like me. It’s lazy. Boy, it always looks for the easiest way to do things.",
    "In painting, you have unlimited power. You have the ability to move mountains. You can bend rivers. But when I get home, the only thing I have power over is the garbage.",
    "Don’t forget to tell these special people in your life just how special they are to you.",
    "Didn’t you know you had that much power? You can move mountains. You can do anything.",
    "I like to beat the brush.",
    "Just let go — and fall like a little waterfall.",
    "Talk to the tree, make friends with it.",
    "I taught my son to paint mountains like these, and guess what? Now he paints the best darn mountains in the industry.",
    "I really believe that if you practice enough you could paint the ‘Mona Lisa’ with a two-inch brush.",
    "Be so very light. Be a gentle whisper.",
    "Use absolutely no pressure. Just like an angel’s wing.",
    "You need the dark in order to show the light.",
    "You can do anything you want to do. This is your world.",
    "You have to allow the paint to break to make it beautiful.",
    "However you think it should be, that’s exactly how it should be.",
    "In nature, dead trees are just as normal as live trees.",
    "You can have anything you want in the world — once you help everyone around you get what they want.",
    "If you do too much, it’s going to lose its effectiveness.",
    "This is happy place; little squirrels live here and play.",
    "That’s where the crows will sit. But we’ll have to put an elevator to put them up there because they can’t fly, but they don’t know that, so they still try.",
    "Remember how free clouds are. They just lay around in the sky all day long.",
    "We don’t really know where this goes — and I’m not sure we really care.",
    "If we’re going to have animals around we all have to be concerned about them and take care of them.",
    "You can do anything here — the only prerequisite is that it makes you happy.",
    "Go out on a limb — that’s where the fruit is.",
    "Isn’t it fantastic that you can change your mind and create all these happy things?",
    "Anytime you learn, you gain.",
    "It’s life. It’s interesting. It’s fun.",
    "Trees are like people. They all have a few flaws in them.",
    "When you get a little challenge in your life you tend to enjoy it.",
    "Even a little tree will grow up to be a big tree. All it needs is water, sunshine and love - the same as all of us.",
    "There’s tranquility and peace in my world, there’s never any violence.",
    "Art should make you feel good about yourself and about the world.",
    "It is my world and everything in my world is happy.",
    "If it ain’t broke, don’t fix it - but nothing is broken, so don’t worry about trying to fix anything.",
    "Let’s be brave - because we can do anything.",
    "We all have different ideas - and they’re all good - there is no good or bad.",
    "Think about a thunderstorm, they have a chaotic sound but when they are over everything is clean, fresh and beautiful again.",
    "The joy in life comes from doing your own thing.",
    "Go outside and make friends with a tree.",
    "Do a little, but don’t get greedy.",
    "All you have to do is decide and then let the rest happen.",
    "It will look like life is just exploding.",
    "At this point we’re not concerned - we’ll worry about that later.",
    "Just a tiny bit, we don’t need much today.",
    "If you look into the clouds long enough, you’ll find what you’re looking for.",
    "Too much will ruin the illusion.",
    "You just have to find what works for you.",
    "It’s a long way off, we don’t even know where it goes - but we don’t need to care.",
    "It gets to feel good and you want to just keep doing it, but the key is restraint.",
    "Once you get over the fear, you’ll be amazed at what you can do.",
    "Of course you can do that. You can do anything.",
    "Trees grow in every shape and size, just like people - and that’s what makes them fantastic.",
    "If you have to do something over again, it doesn’t mean you’re bad, it just means you’re normal.",
    "Let your imagination take you anywhere you want to go.",
    "If you don’t think you can do this - you’re not realizing how simple it is.",
    "Nothing in the world breeds success like success, even if you start with the smallest amount.",
    "There’s no good or bad. There’s just what makes you happy.",
    "It really doesn’t matter, we can always paint over it.",
    "Anything that you can visualize in your mind, you can do.",
    "Sometimes you can amaze yourself.",
    "All you have to do is realize there are no boundaries here.",
    "You can do anything in this life. As long as you believe you can.",
    "Sometimes life has a funny sense of humor.",
    "Once in awhile you need a little sorrow in your life.",
    "Don’t be afraid to go out on a limb. That’s where the fruit is.",
    "Spend some time talking with the trees.",
    "No one has ever been hurt by having too many friends.",
    "We don’t need to set the sky on fire, a little glow will do just fine.",
    "I love every little bird and critter.",
    "It can be scary to have this much power.",
    "Everybody has their own ideas, and that’s the way it should be.",
    "The only rule is that you should enjoy this.",
    "Remember, you can do anything in your world that you want to.",
    "All it takes is just a little change of perspective and you begin to see a whole new world.",
    "Everyone is going to see things differently - and that’s the way it should be.",
    "You can create beautiful things - but you have to see them in your mind first",
    "Don’t be afraid to make these big decisions. Once you start, they sort of just make themselves.",
    "With something so strong, a little bit can go a long way.",
    "Think about a cloud. Just float around and be there.",
    "In nature, dead trees are just as normal as live trees.",
    "You have to put some dark color in so your light color will show.",
    "In life you need colors.",
    "It’s a super day, so why not make a beautiful sky?",
    "It’s beautiful - and we haven’t even done anything to it yet",
    "Pretend you’re water. Just floating without any effort. Having a good day.",
    "They say everything looks better with odd numbers of things. But sometimes I put even numbers - just to upset the critics.",
    "When things happen - enjoy them. They’re little gifts.",
    "Take your time. Speed will come later.",
    "It’s amazing what you can do with a little love in your heart.",
    "God gave you this gift of imagination. Use it.",
    "You can do anything your heart can imagine.",
    "With practice comes confidence.",
    "If you don’t like it - change it. It’s your world.",
    "There is immense joy in just watching - watching all the little creatures in nature.",
    "That is when you can experience true joy, when you have no fear.",
    "We don’t really know where this goes - and I’m not sure we really care.",
    "Life is too short to be alone, too precious. Share it with a friend.",
    "If we’re going to have animals around we all have to be concerned about them and take care of them.",
    "Dead trees are also a part of nature.",
    "Sometimes you learn more from your mistakes than you do from your masterpieces.",
    "You want your tree to have some character. Make it special.",
    "The man who does the best job is the one who is happy at his job.",
    "Everything’s not great in life, but we can still find beauty in it.",
    "You’re the greatest thing that has ever been or ever will be. You’re special. You’re so very special.",
    "There are no accidents. There are no mistakes.",
    "There is no right or wrong - as long as it makes you happy and doesn’t hurt anyone.",
    "Everyone needs a friend. Friends are the most valuable things in the world.",
    "There are no mistakes. You can fix anything that happens.",
    "That’s why I paint - because I can create the kind of world I want - and I can make this world as happy as I want it.",
    "How do you make a round circle with a square knife? That’s your challenge for the day.",
    "Just think about these things in your mind - then bring them into your world."
]

GD_PATH = "gdmeme"
GD_MEMES = [
    ["feature.png",         "Akien via Github"],
    ["malware.png",         "Akien via Github"],
    ["vacation.png",        "nunodonato via Github"],
    ["abracadabra.jpg",     "Omicron666 via Discord"],
    ["WeAreGodotDev.png",   "Omicron666 via Discord"],
    ["adamot.png",          "Noshyaar via Discord"],
    ["floor.png",           "Noshyaar via Discord"],
    ["godots.png",          "Noshyaar via Discord"],
    ["mrworldwide.png",     "Noshyaar via Discord"],
    ["notclear.png",        "Noshyaar via Discord"],
    ["rare.png",            "Noshyaar via Discord"],
    ["scons.png",           "Noshyaar via Discord"],
    ["zodiac.png",          "Noshyaar via Discord"],
    ["wow.png",             "Noshyaar via Discord"],
    ["whowouldwin.png",     "Noshyaar via Discord"],
    ["unity_logo.png",      "Noshyaar via Discord"],
    ["steamsale.png",       "Noshyaar via Discord"],
    #["ＡＥＳＴＨＥＴＩＣ.png", "Noshyaar via Discord"],
    #["help_me.png",         "Noshyaar via Discord"],
    #["ooops.png",           "Noshyaar via Discord"],

    ["19149175.jpg",        "Igor Gritsenko via Facebook"],
    ["19250494.jpg",        "Adam Cooke via Facebook"],
    ["16819060.jpg",        "Oussama Boukhelf‎ via Facebook"],
    ["18010757.jpg",        "William Tumeo via Facebook"],
    ["18342521.jpg",        "Juan Bustelo via Facebook"],
    ["18814238.jpg",        "Nahomy Mejia via Facebook"],
    ["18920649.jpg",        "Nahomy Mejia via Facebook"],
    ["19113510.jpg",        "Nahomy Mejia via Facebook"],
    ["19396679.jpg",        "Feko Boke via Facebook"],

    ["lnnefu5mgary_0.png",  "zopyz via /r/Godot"],
    ["lnnefu5mgary_1.png",  "zopyz via /r/Godot"],
    ["lnnefu5mgary_2.png",  "zopyz via /r/Godot"],
    ["lnnefu5mgary_3.png",  "zopyz via /r/Godot"],
    ["lnnefu5mgary_4.png",  "zopyz via /r/Godot"],
    ["QlGMyhnuZ9.png",      "glatteis via /r/Godot"],
    ["gkzNOEx.png",         "jaydonteh via /r/Godot"],
    
    ["resolutions.png",     "anon (/agdg/), kkolyv (Discord)"]
]

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

    for i in range(len(GD_MEMES)):
        GD_MEMES[i][0] = os.path.join(GD_PATH, GD_MEMES[i][0])

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


async def check_duplicate_url(channel, url):
    if not url:
        print("URL is blank, won't check for duplicate.")
        return False
    async for log in client.logs_from(channel, limit=20):
        for e in log.embeds:
            if "url" in e:
                if url == e["url"]:
                    return True
        else:   # No duplicates
            continue    # Continue to next log item
        break   # If there was duplicates, it reaches this
    else:
        return False


def embed_gh(gh_object):
    tiny = False
    desc_text = gh_object["desc"]
    line_count = desc_text.count("\n") + 1
    if line_count > MAX_DESC_LINES:
        lbreaks = [n for n in range(len(desc_text)) if desc_text.find('\n', n) == n]
        desc_text = desc_text[0:lbreaks[MAX_DESC_LINES - 1]] + "\n....."
    issue_number = gh_object["issue_number"] + " " if gh_object["issue_number"] else ""
    post_type = icon_url = ""
    color = 0xFFFFFF
    if gh_object["type"] == GH_COMMIT:
        post_type = "Commit"
        color = EMBED_COMMIT_COLOR
        icon_url = EMBED_COMMIT_ICON
    elif gh_object["type"] == GH_PR:
        post_type = "Pull request"
        color = EMBED_PR_COLOR
        icon_url = EMBED_PR_ICON
    elif gh_object["type"] == GH_ISSUE:
        post_type = "Issue"
        color = EMBED_ISSUE_COLOR
        icon_url = EMBED_ISSUE_ICON
    elif gh_object["type"] == GH_QA:
        post_type = "Question"
        color = EMBED_QA_COLOR
        icon_url = EMBED_QA_ICON
        desc_text = discord.Embed.Empty
        tiny = True
    elif gh_object["type"] == GH_FORUM:
        post_type = "Forum thread by " + gh_object["author"]
        color = EMBED_FORUM_COLOR
        icon_url = EMBED_FORUM_ICON
        tiny = True

    footer_text = "{type} {issue_number}| {r}".format(
        type=post_type,
        issue_number=issue_number,
        r=gh_object["repository"]
    )

    e = discord.Embed(
        title=gh_object["title"],
        description=desc_text,
        url=gh_object["url"],
        color=color,
    )
    e.set_footer(
        text=footer_text,
        icon_url=icon_url
    )
    if not tiny:
        e.set_author(
            name=gh_object["author"],
            url=gh_object["author_url"],
            icon_url=gh_object["avatar_icon_url"]
        )
    return e


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
        gh_obj, stamp = feed.check_qa(QA_URL, qstamp.stamp if qstamp else "missing")

        if qstamp:
            if not qstamp.stamp == stamp:
                qstamp.stamp = stamp
        else:
            dbstamp = Stamp(descriptor="qa", stamp=stamp)
            session.add(dbstamp)
            print("Adding new stamp in database for Q&A")

        if gh_obj:
            if await check_duplicate_url(channel, gh_obj["url"]):
                print("Q&A thread already posted, abort!")
            else:
                print("Posting QA notification.")
                await client.send_message(channel, embed=embed_gh(gh_obj))

        session.commit()
        await asyncio.sleep(QA_TIMEOUT)


async def forum_checker():
    await client.wait_until_ready()
    channel = discord.Object(id=FORUM_CHANNEL)

    while not client.is_closed:
        session = Session()
        fstamp = session.query(Stamp).filter_by(descriptor="forum").first()
        gh_obj, stamp = feed.check_forum(
            FORUM_URL,
            fstamp.stamp if fstamp else "missing"
        )

        if fstamp:
            if not fstamp.stamp == stamp:
                fstamp.stamp = stamp
        else:
            # Creating new row for forum stamp
            dbstamp = Stamp(descriptor="forum", stamp=stamp)
            session.add(dbstamp)
            print("Adding new stamp in database for forum.")

        if gh_obj:
            if await check_duplicate_url(channel, gh_obj["url"]):
                print("Forum thread already posted, abort!")
            else:
                print("Posting Forum notification.")
                await client.send_message(channel, embed=embed_gh(gh_obj))

        session.commit()
        await asyncio.sleep(FORUM_TIMEOUT)


async def commit_checker():
    await client.wait_until_ready()
    channel = discord.Object(id=COMMIT_CHANNEL)

    while not client.is_closed:
        session = Session()
        cstamp = session.query(Stamp).filter_by(descriptor="commit").first()
        gh_obj, stamp = feed.check_commit(
            COMMIT_URL,
            cstamp.stamp if cstamp else "missing"
        )

        if cstamp:
            if not cstamp.stamp == stamp:
                # Updating stamp in db
                cstamp.stamp = stamp
        else:
            dbstamp = Stamp(descriptor="commit", stamp=stamp)
            session.add(dbstamp)
            print("Adding new stamp to database for commits")

        if gh_obj:
            if await check_duplicate_url(channel, gh_obj["url"]):
                print("Commit already posted, abort!")
            else:
                print("Posting Commit notification.")
                await client.send_message(channel, embed=embed_gh(gh_obj))

        session.commit()
        await asyncio.sleep(COMMIT_TIMEOUT)


async def issue_checker():
    await client.wait_until_ready()
    channel = discord.Object(id=ISSUE_CHANNEL)

    while not client.is_closed:
        session = Session()
        istamp = session.query(Stamp).filter_by(descriptor="issue").first()
        gh_objects, stamp = feed.check_issue(
            ISSUE_URL,
            istamp.stamp if istamp else "missing"
        )

        if istamp:
            if not istamp.stamp == stamp:
                # Updating stamp in db
                istamp.stamp = stamp
        else:
            dbstamp = Stamp(descriptor="issue", stamp=stamp)
            session.add(dbstamp)
            print("Adding new stamp to database for issues")

        if gh_objects:
            for gh_obj in gh_objects:
                if await check_duplicate_url(channel, gh_obj["url"]):
                    print("Issue already posted, removing!")
                else:
                    print("Posting Issue notification.")
                    await client.send_message(channel, embed=embed_gh(gh_obj))

        session.commit()
        await asyncio.sleep(ISSUE_TIMEOUT)


async def doc_commit_checker():
    await client.wait_until_ready()
    channel = discord.Object(id=COMMIT_CHANNEL)

    while not client.is_closed:
        session = Session()
        cstamp = session.query(Stamp).filter_by(descriptor="doc_commit").first()
        gh_obj, stamp = feed.check_commit(
            DOC_COMMIT_URL,
            cstamp.stamp if cstamp else "missing"
        )

        if cstamp:
            if not cstamp.stamp == stamp:
                # Updating stamp in db
                cstamp.stamp = stamp
        else:
            dbstamp = Stamp(descriptor="doc_commit", stamp=stamp)
            session.add(dbstamp)
            print("Adding new stamp to database for doc-commits")

        if gh_obj:
            if await check_duplicate_url(channel, gh_obj["url"]):
                print("Commit already posted, abort!")
            else:
                print("Posting Commit notification.")
                await client.send_message(channel, embed=embed_gh(gh_obj))

        session.commit()
        await asyncio.sleep(DOC_COMMIT_TIMEOUT)


async def doc_issue_checker():
    await client.wait_until_ready()
    channel = discord.Object(id=ISSUE_CHANNEL)

    while not client.is_closed:
        session = Session()
        istamp = session.query(Stamp).filter_by(descriptor="doc_issue").first()
        gh_objects, stamp = feed.check_issue(
            DOC_ISSUE_URL,
            istamp.stamp if istamp else "missing"
        )

        if istamp:
            if not istamp.stamp == stamp:
                # Updating stamp in db
                istamp.stamp = stamp
        else:
            dbstamp = Stamp(descriptor="doc_issue", stamp=stamp)
            session.add(dbstamp)
            print("Adding new stamp to database for doc-issues")

        if gh_objects:
            for gh_obj in gh_objects:
                if await check_duplicate_url(channel, gh_obj["url"]):
                    print("Issue already posted, removing!")
                else:
                    print("Posting Issue notification.")
                    await client.send_message(channel, embed=embed_gh(gh_obj))

        session.commit()
        await asyncio.sleep(DOC_ISSUE_TIMEOUT)


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

    # Posts quotes of Bob Ross
    if message.content.lower().startswith("!bobross") or message.content.lower().startswith("!ross") or message.content.lower().startswith("!br"):
        rand_c = random.randint(0, len(ROSS_QUOTES) - 1)
        quote = ROSS_QUOTES[rand_c]
        e = discord.Embed(
            color=EMBED_ROSS_COLOR,
            description=quote
        )
        e.set_author(
            name="Bob Ross",
            icon_url=EMBED_ROSS_ICON
        )
        await client.send_message(message.channel, embed=e)
        

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

    if message.content.lower().startswith("!meme"):
        fpath = None
        credit = "N/A"

        rand_c = random.randint(0, len(GD_MEMES) - 1)
        fpath = GD_MEMES[rand_c][0]
        credit = GD_MEMES[rand_c][1]

        if fpath:
            with open(fpath, "rb") as f:
                await client.send_file(message.channel, f, content="**By {0}**".format(credit))

    if message.channel.name != "botspam":
        return  # Ignore command if it's not written in botspam channel

    # Send help message.
    if (
        message.content.startswith("!help") or
        message.content.startswith("!commands")
    ):
        await client.send_message(message.channel, HELP_STRING)
        await client.delete_message(message)

    elif message.content.startswith("!xp"):
        # Get the xp for the user sending the message, or for any mentions
        # after the command.
        session = Session()
        msg = ""
        if not message.mentions:
            u = session.query(User).filter_by(userid=id).first()
            if u:
                msg = "{0}'s XP: **{1}**".format(
                    message.author.nick if message.author.nick else message.author.name, u.xp
                )
            else:
                msg = "**Not found.**"
        else:
            ranks = []
            for m in message.mentions:
                u = session.query(User).filter_by(userid=m.id).first()
                if u:
                    ranks.append(u)
            ranks = sorted(ranks, key=lambda x: x.xp, reverse=True)
            for u in ranks:
                mem = message.server.get_member(u.userid)
                msg += "{0}: **{1}**\n".format(
                    mem.nick if mem.nick else mem.name,
                    u.xp
                )
        if msg:
            tmp = await client.send_message(message.channel, msg)
            await delete_edit_timer(
                tmp, FEEDBACK_DEL_TIMER
            )
        try:
            await client.delete_message(message)
        except:
            pass

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
    tmp = await client.send_message(channel, msg)
    if (member.nick if member.nick else member.name) == "Goblok":
        for e in member.server.emojis:
            if e.name == "angryfaic":
                await client.add_reaction(tmp, e)
                break
    msg = ":new: `add_child(`{0}`)`\nWelcome to the server! :tada:".format(member.mention)
    channel = discord.Object(id=GENERAL_CHANNEL)
    tmp = await client.send_message(channel, msg)


# Prepare for takeoff.
populate_memes()
client.loop.create_task(commit_checker())
client.loop.create_task(issue_checker())
client.loop.create_task(doc_commit_checker())
client.loop.create_task(doc_issue_checker())
client.loop.create_task(forum_checker())
client.loop.create_task(qa_checker())
client.run(TOKEN)   # And we have liftoff.
