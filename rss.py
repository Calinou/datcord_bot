import feedparser
import datetime

COMMIT_URL = "https://github.com/NiclasEriksen/godot_rpg/commits/master.atom"
ISSUE_URL = None    # Not implemented
PULL_URL = None     # Not implemented


class RSSFeed:

    def __init__(self):
        self.commit_url = COMMIT_URL
        self.last_commit_time = None

    def parse_commit(self):
        d = feedparser.parse(self.commit_url)
        if not d.feed.updated == self.last_commit_time:
            self.last_commit_time = d.feed.updated
            return d["items"][0]

    def format_commit_message(self, entry):
        msg = ":outbox_tray: **New commit by {1}**:\n```{0}```".format(
            entry["title"],
            entry["author"]
        )
        return msg

    def check_commit(self):
        e = self.parse_commit()
        if e:
            return self.format_commit_message(e)
        else:
            return False

    def check_issue(self):
        return False    # Not implemented

    def check_pull(self):
        return False    # Not implemented


if __name__ == "__main__":
    # For testing
    f = RSSFeed()
    while True:
        e = f.parse()
        if e:
            print(f.format_commit_message(e))
