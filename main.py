#!/usr/bin/env python3

import asyncio
import os
import random
import re
from typing import Any

from typing_extensions import Final

import discord

client: Final = discord.Client()

# Configuration
#
# Set the token as an environment variable before running the script.
TOKEN: Final = os.environ.get("DISCORD_BOT_TOKEN")
# Roles that users can assign themselves to, must be lower case.
AVAILABLE_ROLES: Final = [
    "programmer",
    "designer",
    "artist",
    "sound designer",
    "helper",
    "she/her",
    "he/him",
    "they/them",
]

# Channel names
# Some commands can only be used in the bot commands channel to avoid spam
BOT_COMMANDS_CHANNEL: Final = "bot-cmd"

# URLs
STEP_BY_STEP_URL: Final = "https://docs.godotengine.org/en/latest/getting_started/step_by_step/index.html"
C_SHARP_URL: Final = "http://godotsharp.net/"
CLASS_API_URL: Final = "https://docs.godotengine.org/en/latest/classes/index.html"
TUTORIALS_URL: Final = "https://docs.godotengine.org/en/latest/community/tutorials.html"
NIGHTLY_URL: Final = "https://hugo.pro/projects/godot-builds/"
KIDS_CAN_CODE_YT: Final = "https://www.youtube.com/channel/UCNaPQ5uLX5iIEHUCLmfAgKg"
GDQUEST_YT: Final = "https://www.youtube.com/channel/UCxboW7x0jZqFdvMdCFKTMsQ"
GAME_PROGRAMMING_PATTERNS_URL: Final = "http://gameprogrammingpatterns.com/contents.html"
DOWNLOAD_MIRROR_URL: Final = "https://archive.hugo.pro/godot-tuxfamily/"

# Valid class name regular expression. This avoids possible exploits, such as
# highlighting blocked users on Discord or redirecting to unwanted pages.
# TODO: Remove `_` once Godot 4.0 is released, as `IP_Unix` and `TCP_Server` have been
# renamed to `IPUnix` and `TCPServer` respectively.
CLASS_REGEX: Final = re.compile("^[a-zA-Z0-9@_]+$")

# Message that the bot returns on `!help`
HELP_STRING: Final = """:book: **Commands:**
!assign [role]: *Assign yourself to one of the available roles.*
!unassign [role]: *Unassign yourself from a role.*
!roles: *List available roles.*
:book: **Factoids:**
!api: *Online Godot class reference.*
!class [class]: *Online Godot class reference for the specified class.*
!csharp: *Godot C# documentation.*
!gdquest: *GDquest YouTube channel.*
!kcc: *KidsCanCode YouTube channel.*
!nightly: *Calinou's nightly Godot builds.*
!pronounce: *Godot pronounciation.*
!step: *Godot step by step documentation.*
!tut: *List of tutorials in the Godot documentation.*"""

# How long to wait for before deleting messages
FEEDBACK_DEL_TIMER: Final = 5

# A lot of people ask how to prounce Godot
HOW_TO_PRONOUNCE_GODOT: Final = "There is no right way. It varies based on your region."

WORK_ON_GAME: Final = "https://imgur.com/a/egsXCBs"
EMBED_ROSS_ICON: Final = "http://i.imgur.com/OZLdaSn.png"
EMBED_ROSS_COLOR: Final = 0x000F89
ROSS_QUOTES: Final = [
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
    "Just think about these things in your mind - then bring them into your world.",
]

GD_PATH: Final = "gdmeme"
GD_MEMES: Final = [
    ["wolf3d_godot.png", "Calinou"],
    ["questions.png", "Anonymous"],
    ["steamsale.png", "Anonymous"],
    ["precious.png", "Anonymous"],
    ["cereal.png", "Anonymous"],
    ["asset-store.png", "Anonymous"],
    ["languages.png", "Anonymous"],
    ["plot-twist.png", "Anonymous"],
    ["just-godot.png", "Anonymous"],
    ["alpaca.png", "Anonymous"],
    ["friendzoned.png", "Anonymous"],
    ["init.png", "Anonymous"],
    ["adamot.png", "Anonymous"],
    ["floor.png", "Anonymous"],
    ["godots.png", "Anonymous"],
    ["mrworldwide.png", "Anonymous"],
    ["notclear.png", "Anonymous"],
    ["rare.png", "Anonymous"],
    ["scons.png", "Anonymous"],
    ["wow.png", "Anonymous"],
    ["unity-spinner.png", "Anonymous"],
    ["pending-prs.jpg", "Anonymous"],
    ["torrent.png", "Anonymous"],
    ["godoot.png", "Anonymous"],
    ["feature.png", "Akien via GitHub"],
    ["malwareinstall.png", "Akien via GitHub"],
    ["ubuntu.png", "Akien via GitHub"],
    ["whole-new-world.png", "Akien via GitHub"],
    ["nodeintobool.jpg", "groud via GitHub"],
    ["vacation.png", "nunodonato via GitHub"],
    ["fuckyoux11.png", "reduz via GitHub"],
    ["boeing.png", "reduz via GitHub"],
    ["about-gnu-linux.png", "Anonymous via GitHub"],
    ["utterbullshit.png", "Akien via IRC"],
    ["ads-dock.png", "Akien via IRC"],
    ["godoit.png", "bojidar_bg via IRC"],
    ["godoit2.png", "groud via IRC"],
    ["docs-howto.png", "Fryy via IRC"],
    ["karroffel-tim.png", "karroffel via Matrix"],
    ["shy-godot.png", "kkolyv via Matrix"],
    ["morpheus.png", "kkolyv via Matrix"],
    ["do_it_for_her.png", "01lifeleft via Discord"],
    ["live_dangerously.png", "01lifeleft via Discord"],
    ["godot-episode3.png", "Calinou via Discord"],
    ["i_didnt_listen.png", "Calinou via Discord"],
    ["nine_inch_nodes.png", "Calinou via Discord"],
    ["cute-in-execute.png", "Dramatico via Discord"],
    ["chad-godot.png", "Gors via Discord"],
    ["godot-chan03.png", "kkolyv via Discord"],
    ["internet-activity.png", "Mistery Man via Discord"],
    ["godot-3-2-1.png", "Mistery Man via Discord"],
    ["perfect_godette.png", "Mistery Man via Discord"],
    ["noodlescript.png", "NoeDev via Discord"],
    ["gdscript-see-sharp.png", "NoohAlavi via Discord"],
    ["abracadabra.jpg", "Omicron666 via Discord"],
    ["godonymous.png", "Omicron666 via Discord"],
    ["godot_airlines.jpg", "onur via Discord"],
    ["collisionshape.png", "sheepandshepherd via Discord"],
    ["gd3_pbr_edition.png", "YeOldeDM via Discord"],
    ["kenny-tester.png", "Zylann via Discord"],
    ["godoterminator.jpg", "Zylann via Discord"],
    ["cat-godot.jpg", "Juan Linietsky via Facebook"],
    ["sad-godot.jpg", "Juan Linietsky via Facebook"],
    ["tuxedot.jpg", "Juan Linietsky via Facebook"],
    ["comingofage.jpg", "Juan Linietsky via Facebook"],
    ["galgodot2.jpg", "Adam Cooke via Facebook"],
    ["untitled01.jpg", "Oussama Boukhelf via Facebook"],
    ["dragonball.jpg", "William Tumeo via Facebook"],
    ["balloon.jpg", "William Tumeo via Facebook"],
    ["galgodot1.jpg", "Juan Bustelo via Facebook"],
    ["gamedev_time.jpg", "Mariano Suligoy via Facebook"],
    ["whereisgodot.jpg", "Nahomy Mejia via Facebook"],
    ["dontwantnolife.jpg", "Nahomy Mejia via Facebook"],
    ["sisterross.jpg", "Nahomy Mejia via Facebook"],
    ["spongebob.jpg", "Nahomy Mejia via Facebook"],
    ["first-word.jpg", "Nahomy Mejia via Facebook"],
    ["ugly-mid-school.jpg", "Rafał Michałuszek via Facebook"],
    ["jam-theme.jpg", "José A Barrera Díaz via Facebook"],
    ["votetime.jpg", "José A Barrera Díaz via Facebook"],
    ["meme-engine.jpg", "Henrique Alves via Facebook"],
    ["mrgodot.jpg", "Henrique Campos via Facebook"],
    ["terminator.jpg", "Bruno Correia da Silva via Facebook"],
    ["dotgot-engine.jpg", "Christian Melgarejo Bresanovich via Facebook"],
    ["trust-godot.jpg", "anon via Facebook"],
    ["new3.0build.png", "zopyz via /r/godot"],
    ["unity-malware.png", "zopyz via /r/godot"],
    ["unity-graveyard.png", "zopyz via /r/godot"],
    ["replacegdscript.png", "zopyz via /r/godot"],
    ["rickroll.jpg", "zopyz via /r/godot"],
    ["godot-products.png", "jaydonteh via /r/godot"],
    ["guy-looks-gal.jpg", "Sam Vila on Twitter"],
    ["godot-chan01.png", "anon via 4chan"],
    ["godot-chan02.png", "anon via 4chan"],
    ["resolutions.png", "anon (/agdg/), kkolyv (Discord)"],
    ["revert.png", "vnen (IRC), Akien, reduz (GitHub)"],
]

last_meme = ""


def populate_memes() -> None:
    """
    Retrieves all pictures ``GD_MEMES`` folder and sorts them by name.
    """

    for i in range(len(GD_MEMES)):
        GD_MEMES[i][0] = os.path.join(GD_PATH, GD_MEMES[i][0])


async def delete_edit_timer(
    msg: Any, time: int, error: bool = False, call_msg: Any = None
) -> None:
    """
    Counts down by editing the response message, then deletes both that one and
    the original message.
    """
    ws: Final = ":white_small_square:"
    bs: Final = ":black_small_square:"

    # Cache the message content. We can't use msg.content in the for
    # loop as the msg object is mutable (so that we would append a new
    # line for every loop iteration).
    msg_text: str = msg.content

    for i in range(time + 1):
        await msg.edit(content=msg_text + "\n" + ws * (time - i) + bs * i)
        await asyncio.sleep(1)

    await msg.delete()

    if call_msg:
        # Prevent crash if the call message has been deleted before the bot
        # gets to it.
        try:
            await call_msg.delete()
        except:
            print("Call message does not exist.")


@client.event
async def on_ready() -> None:
    print(f"Logged in as: {client.user.name}--{client.user.id}")
    print("------")


@client.event
async def on_message(message: Any) -> None:
    # Posts quotes of Bob Ross
    if (
        message.channel.name == BOT_COMMANDS_CHANNEL
        and message.content.lower().startswith("!bobross")
        or message.content.lower().startswith("!ross")
        or message.content.lower().startswith("!br")
    ):
        rand_c = random.randint(0, len(ROSS_QUOTES) - 1)
        quote = ROSS_QUOTES[rand_c]
        e = discord.Embed(color=EMBED_ROSS_COLOR, description=quote)
        e.set_author(name="Bob Ross", icon_url=EMBED_ROSS_ICON)
        await message.channel.send(embed=e)

    elif message.channel.name == BOT_COMMANDS_CHANNEL and message.content.lower().startswith(
        "!meme"
    ):
        choice_error = False
        fpath = None
        credit = "N/A"
        c = message.content[6:]
        global last_meme
        if not len(c.strip()) or not message.content[5] == " ":
            choice_error = True

        submeme = []
        if not choice_error:
            for i in GD_MEMES:
                if i[1].lower().find(c.lower()) != -1:
                    submeme.append(i)

        if choice_error or len(submeme) == 0:
            submeme = GD_MEMES

        rand_c = 0
        fpath = ""

        tries = 0
        while tries < 4:
            rand_c = random.randint(0, len(submeme) - 1)
            fpath = submeme[rand_c][0]
            if fpath != last_meme:
                break
            tries += 1

        last_meme = fpath

        credit = submeme[rand_c][1]

        if fpath:
            with open(fpath, "rb") as f:
                await message.channel.send(f"**By {credit}**", file=discord.File(f))

    # Send help message.
    elif (
        message.channel.name == BOT_COMMANDS_CHANNEL
        and message.content.startswith("!help")
        or message.content.startswith("!commands")
    ):
        await message.channel.send(HELP_STRING)

    # Show a list of assignable roles.
    elif message.channel.name == BOT_COMMANDS_CHANNEL and message.content.startswith(
        "!roles"
    ):
        s = ":scroll: **Available roles:**\n"
        s += "```\n"

        for index, role in enumerate(AVAILABLE_ROLES):
            s += f"{role.upper()}"
            if not index == len(AVAILABLE_ROLES) - 1:
                s += ", "
        s += "```"

        await message.channel.send(s)

    # Attempt to assign the user to a role.
    elif (
        message.channel.name == BOT_COMMANDS_CHANNEL
        and message.content.startswith("!assign")
        or message.content.startswith("!set")
        or message.content.startswith("!role")
    ):
        # TODO Unassign all roles.
        error = False

        # Have to slice the message depending on the command alias given.
        if message.content.startswith("!assign"):
            s = message.content[8:]  # remove !assign
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
            tmp = await message.channel.send("Usage: !assign [role]")
            await delete_edit_timer(
                tmp, FEEDBACK_DEL_TIMER, error=True, call_msg=message
            )
        else:
            # This looks messy, but it works. There must be a more effective
            # method of getting the role object rather than iterating over
            # all available roles and checking their name.
            new_role = s
            roles = message.guild.roles

            for role in roles:
                if role.name.lower() == new_role.lower():
                    if role.name.lower() in AVAILABLE_ROLES:
                        if role not in message.author.roles:
                            await message.author.add_roles(role)
                            tmp = await message.channel.send(
                                f":white_check_mark: User {message.author.name} added to {role.name}."
                            )
                            await delete_edit_timer(
                                tmp, FEEDBACK_DEL_TIMER, call_msg=message
                            )
                        else:
                            tmp = await message.channel.send(
                                "You already have that role."
                            )
                            await delete_edit_timer(
                                tmp, FEEDBACK_DEL_TIMER, error=True, call_msg=message
                            )
                    else:
                        tmp = await message.channel.send(
                            ":no_entry: *You're not allowed to assign yourself to that role.*"
                        )
                        await delete_edit_timer(
                            tmp, FEEDBACK_DEL_TIMER, error=True, call_msg=message
                        )
                    break
            else:
                tmp = await message.channel.send(
                    f":no_entry: **{new_role.upper()}** <- *Role not found.*"
                )
                await delete_edit_timer(
                    tmp, FEEDBACK_DEL_TIMER, error=True, call_msg=message
                )

    elif (
        message.channel.name == BOT_COMMANDS_CHANNEL
        and message.content.startswith("!unassign")
        or message.content.startswith("!remove")
    ):
        error = False

        # It's the same here that it was with !assign
        if message.content.startswith("!unassign"):
            s = message.content[10:]  # remove !unassign
            if not len(s) or not message.content[9] == " ":
                error = True
        elif message.content.startswith("!remove"):
            s = message.content[8:]  # remove !remove
            if not len(s) or not message.content[7] == " ":
                error = True

        if error:
            tmp = await message.channel.send("Usage: !unassign [role]")
            await delete_edit_timer(tmp, FEEDBACK_DEL_TIMER, call_msg=message)
        else:
            old_role = s
            roles = message.guild.roles
            for role in message.author.roles:
                if role.name.lower() == old_role.lower():
                    await message.author.remove_roles(role)
                    tmp = await message.channel.send(
                        ":white_check_mark: Role was removed."
                    )
                    await delete_edit_timer(tmp, FEEDBACK_DEL_TIMER, call_msg=message)
                    break
            else:
                tmp = await message.channel.send(
                    f":no_entry: **{old_role.upper()}** <- You don't have that role."
                )
                await delete_edit_timer(
                    tmp, FEEDBACK_DEL_TIMER, error=True, call_msg=message
                )

    elif message.content.lower().startswith("!api"):
        await message.channel.send(CLASS_API_URL)

    elif message.content.lower().startswith("!class"):
        class_name: Final = message.content[7:].lower()  # Remove `!class`.
        if class_name != "" and CLASS_REGEX.match(class_name):
            # Percent-encode the `@` symbol to prevent highlighting users on Discord.
            class_name_escaped: Final = class_name.replace("@", "%40")
            await message.channel.send(
                f"https://docs.godotengine.org/en/stable/classes/class_{class_name_escaped}.html"
            )
        elif class_name != "":
            await message.channel.send(
                "Invalid class name (must not contain spaces or special characters other than `@` and `_`)."
            )
        else:
            await message.channel.send("Usage: !class [class]")

    elif message.content.lower().startswith("!csharp"):
        await message.channel.send(C_SHARP_URL)

    elif message.content.lower().startswith("!game"):
        await message.channel.send(WORK_ON_GAME)

    elif message.content.lower().startswith("!gdquest"):
        await message.channel.send(GDQUEST_YT)

    elif message.content.lower().startswith("!kcc"):
        await message.channel.send(KIDS_CAN_CODE_YT)

    elif message.content.lower().startswith("!mirror"):
        await message.channel.send(DOWNLOAD_MIRROR_URL)

    elif message.content.lower().startswith("!nightly"):
        await message.channel.send(NIGHTLY_URL)

    elif message.content.lower().startswith("!patterns"):
        await message.channel.send(GAME_PROGRAMMING_PATTERNS_URL)

    elif message.content.lower().startswith("!pronounce"):
        await message.channel.send(HOW_TO_PRONOUNCE_GODOT)

    elif message.content.lower().startswith("!step"):
        await message.channel.send(STEP_BY_STEP_URL)

    elif message.content.lower().startswith("!tut"):
        await message.channel.send(TUTORIALS_URL)


# Prepare for takeoff.
populate_memes()
client.run(TOKEN)  # And we have liftoff.
