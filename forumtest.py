import feedparser
import datetime
from time import mktime, sleep
import requests
FORUM_URL = "https://godotdevelopers.org/forum/discussions/feed.rss"


class FeedReader:
    def __init__(self):
        self.forum_url = FORUM_URL

    def parse_forum(self, stamp):
        msg = None
        d = feedparser.parse(self.forum_url)
        latest = d["items"][:5]
        old_stamp = datetime.datetime.fromtimestamp(float(stamp))
        for thread in reversed(latest):
            th_stamp = datetime.datetime.fromtimestamp(
                mktime(thread["published_parsed"])
            )
            if th_stamp > old_stamp:
                msg = self.format_forum_message(thread)
                print(mktime(thread["published_parsed"]))
                return msg, float(mktime(thread["published_parsed"]))
        else:
            return False, stamp

    def format_forum_message(self, thread):
        t = thread["title"]
        c = thread["category"]
        a = thread["author"]
        l = thread["link"]
        msg = "New forum thread by **{a}** in {c}\n```{t}```\n<{l}>".format(
            a=a,
            c=c,
            t=t,
            l=l,
        )
        return msg


if __name__ == "__main__":
    fr = FeedReader()
    print(datetime.datetime.now())
    stamp = 0
    while True:
        msg, stamp = fr.parse_forum(stamp)
        if msg:
            print(msg, stamp)
            print("------------")
        sleep(3)
