# Godot Engine Discord server bot

This repository contains the source code for the
[Godot Engine Discord](https://godotengine.org/community) bot.

## Commands

|            Command | Description                                               |
|-------------------:|:----------------------------------------------------------|
|   `!assign [role]` | Assigns yourself to one of the available roles.           |
|   `!meme [author]` | Returns a meme (only usable in the **#bot_cmd** channel). |
|           `!roles` | Lists available roles.                                    |
|            `!ross` | Returns a Bob Ross quote.                                 |
| `!unassign [role]` | Unassigns yourself from a role.                           |
| `!unassign [role]` | Unassigns yourself from a role.                           |

There are also some commands which print a URL or fixed message
for convenience's sake:

|          Command | What it prints                                               |
|-----------------:|:-------------------------------------------------------------|
|           `!api` | The URL to the Godot class reference.                        |
| `!class [class]` | The URL to the specified class in the Godot class reference. |
|        `!csharp` | The URL to GodotSharp, a C# community resource.              |
|       `!gdquest` | The URL to GDquest's YouTube channel.                        |
|           `!kcc` | The URL to KidsCanCode's YouTube channel.                    |
|       `!nightly` | The URL to Calinou's nightly builds.                         |
|     `!pronounce` | A sentence about how "Godot" should be pronounced.           |
|          `!step` | The URL to the official step-by-step tutorial.               |
|           `!tut` | The URL to the list of tutorials in the documentation.       |

## Installation

### Prerequisites

- Python 3.6 (Python 3.7 or later aren't supported yet).
- [Poetry](https://github.com/sdispater/poetry) for installing dependencies.

### Running

- Clone this repository or
  [download a ZIP archive](https://github.com/Calinou/datcord_bot/archive/master.zip).
- Run `poetry install` while in the repository's directory to install
  dependencies.
- Set the `DISCORD_BOT_TOKEN` environment variable to the bot's Discord token.
- Run the script with `python3 main.py`.

## License

Copyright © 2016-2020 Godot Engine contributors

- Unless otherwise specified, files in this repository are licensed under
  the MIT license; see [LICENSE.md](LICENSE.md) for more information.
- [icon.svg](icon.svg) is based on
  [godotengine/godot/icon.svg](https://github.com/godotengine/godot/blob/master/icon.svg)
  and is licensed under CC BY 3.0 Unported; see
  [LOGO_LICENSE.md](https://github.com/godotengine/godot/blob/master/LOGO_LICENSE.md)
  for more information.
- Files in the `gdmeme/` directory are not licensed under the MIT license.
