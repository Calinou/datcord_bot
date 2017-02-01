import feedparser
import datetime
from time import mktime
import requests
import socket
from html2text import html2text

# How long to attempt to connect to the urls above. A long timeout will cause
# the bot to wait way too long.
TIMEOUT = 10
socket.setdefaulttimeout(TIMEOUT)

GH_COMMIT           =   0
GH_PR               =   1
GH_ISSUE            =   2
GH_QA               =   3
GH_FORUM            =   4
GH_OBJECT           =   dict(
    type=0,
    title="No title",
    desc="No description",
    url="https://github.com/godotengine/godot/",
    author="No author",
    author_url="https://github.com",
    avatar_icon_url="",
    issue_number=None,
    repository=""
)


class RSSFeed:
    """
    This is a worms nest.
    """
    def __init__(self):
        pass

    def parse_commit(self, url, stamp):
        try:
            r = requests.get(url, timeout=TIMEOUT)
        except:
            print("Error on requesting commit url.")
            return None, stamp

        d = feedparser.parse(r.content)
        try:
            if not d.feed.updated == stamp:
                # self.save_stamp("commit", d.feed.updated)
                return d["items"][0], d.feed.updated
            else:
                return None, stamp
        except AttributeError:
            print("Attribute error on feed.")
            return None, stamp

    def check_qa(self, url, stamp):
        msg = None

        try:
            r = requests.get(url, timeout=TIMEOUT)
        except:
            print("Error on requesting Q&A url.")
            return None, stamp

        d = feedparser.parse(r.content)
        latest = d["items"][:5]

        try:
            old_stamp = datetime.datetime.fromtimestamp(float(stamp))
        except ValueError:
            print("Stamp invalid, making new from current time.")
            old_stamp = datetime.datetime.now()
            stamp = float(mktime(old_stamp.utctimetuple()))

        for thread in reversed(latest):
            th_stamp = datetime.datetime.fromtimestamp(
                mktime(thread["published_parsed"])
            )
            if th_stamp > old_stamp:
                msg = self.format_qa_message(thread)
                print("New Q&A thread found, posting.")
                return msg, mktime(thread["published_parsed"])
        else:
            return False, float(mktime(old_stamp.utctimetuple()))

    def check_forum(self, url, stamp):
        msg = None

        try:
            r = requests.get(url, timeout=TIMEOUT)
        except:
            print("Error on requesting forum url.")
            return None, stamp

        d = feedparser.parse(r.content)
        latest = d["items"][:5]
        try:
            old_stamp = datetime.datetime.fromtimestamp(float(stamp))
        except ValueError:
            print("Stamp invalid, making new from current time.")
            old_stamp = datetime.datetime.now()
            stamp = float(mktime(old_stamp.utctimetuple()))

        for thread in reversed(latest):
            th_stamp = datetime.datetime.fromtimestamp(
                mktime(thread["published_parsed"])
            )
            if th_stamp > old_stamp:
                msg = self.format_forum_message(thread)
                print("New forum thread found, posting.")
                return msg, mktime(thread["published_parsed"])
        else:
            return False, float(mktime(old_stamp.utctimetuple()))

    def check_commit(self, url, stamp):
        e, newstamp = self.parse_commit(url, stamp)
        if e:
            return self.format_commit_message(e), newstamp
        else:
            return False, newstamp

    def check_issue(self, url, stamp):
        try:
            old_stamp = datetime.datetime.strptime(
                stamp,
                "%Y-%m-%dT%H:%M:%SZ"
            )
        except ValueError:
            old_stamp = datetime.datetime.utcnow()
            stamp = datetime.datetime.strftime(
                old_stamp,
                "%Y-%m-%dT%H:%M:%SZ"
            )
        url = "{0}{1}{2}".format(
            url, "&since=", stamp
        )
        try:
            r = requests.get(url=url)
        except: # There's way too many errors to bother checking for specifics.
            return [], stamp
        parsed = r.json()

        try:
            r.json()[0]
        except KeyError:
            print("Nothing recieved from API, call limit?")
            return [], stamp    # Probably went over call limit
        except IndexError:
            # No new issues.
            return [], stamp

        # 2016-09-12T20:26:12Z
        messages = []
        latest_stamp = None
        candidate_stamp = old_stamp
        for issue in parsed:
            new_stamp = datetime.datetime.strptime(
                issue["created_at"],
                "%Y-%m-%dT%H:%M:%SZ"
            )
            if new_stamp > old_stamp:
                if new_stamp > candidate_stamp:
                    candidate_stamp = new_stamp
                    latest_stamp = issue["created_at"]
                messages.append(self.format_issue_message(issue))

        if latest_stamp:
            stamp = datetime.datetime.strftime(
                datetime.datetime.utcnow(),
                "%Y-%m-%dT%H:%M:%SZ"
            )

        messages.reverse()
        return messages, stamp

    def format_issue_message(self, entry):
        gho = GH_OBJECT.copy()
        try:
            entry["pull_request"]
        except KeyError:
            gho["type"] = GH_ISSUE
        else:
            gho["type"] = GH_PR
        gho["issue_number"] = "#" + str(entry["number"])
        gho["author"] = entry["user"]["login"]
        gho["author_url"] = entry["user"]["html_url"]
        gho["avatar_icon_url"] = entry["user"]["avatar_url"] + "&s=32"
        gho["url"] = entry["html_url"]
        gho["title"] = entry["title"]
        desc = entry["body"].lstrip().replace("\r", "").rstrip().replace("    ", "")
        gho["desc"] = desc
        gho["repository"] = entry["repository_url"].split("/")[-1]

        return gho

    def format_commit_message(self, entry):
        gho = GH_OBJECT.copy()
        gho["type"] = GH_COMMIT
        gho["title"] = entry["title"]
        desc = html2text(entry["summary"]).lstrip()
        desc = desc[desc.find("\n"):len(desc)].rstrip()
        gho["desc"] = desc.lstrip().replace("    ", "")
        gho["url"] = entry["link"]
        gho["author"] = entry["author"]
        if "href" in entry["author_detail"]:
            gho["author_url"] = entry["author_detail"]["href"]
        gho["avatar_icon_url"] = entry["media_thumbnail"][0]["url"]
        gho["repository"] = entry["link"].split("/")[-3]

        return gho

    def format_qa_message(self, thread):
        gho = GH_OBJECT.copy()
        gho["type"] = GH_QA
        gho["title"] = thread["title"]
        gho["url"] = thread["link"]
        gho["repository"] = thread["category"]

        return gho

    def format_forum_message(self, thread):
        gho = GH_OBJECT.copy()
        gho["type"] = GH_FORUM
        gho["title"] = thread["title"]
        gho["desc"] = html2text(thread["description"])
        gho["url"] = thread["link"]
        gho["author"] = thread["author"]
        gho["repository"] = thread["category"]

        return gho

if __name__ == "__main__":
    # For testing
    the_feed = RSSFeed()
