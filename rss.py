import feedparser
import datetime
import requests

COMMIT_URL = "https://github.com/godotengine/godot/commits/master.atom"
ISSUE_URL = "https://api.github.com/repos/godotengine/godot/issues?sort=created"
C_TIMESTAMP_FILE = "commit_stamp"
I_TIMESTAMP_FILE = "issue_stamp"


class RSSFeed:

    def __init__(self):
        self.commit_url = COMMIT_URL
        self.issue_url = ISSUE_URL
        self.last_commit_time = None
        self.last_issue_time = None

    def save_stamp(self, t, stamp):
        fn = None
        if t == "commit":
            fn = C_TIMESTAMP_FILE
        elif t == "issue":
            fn = I_TIMESTAMP_FILE
        if fn:
            f = open(fn, "w")
            f.write(stamp)
            f.close()
        else:
            print("No a valid type, not writing stamp to disk.")

    def get_stamp(self, t):
        fn = None
        if t == "commit":
            fn = C_TIMESTAMP_FILE
        elif t == "issue":
            fn = I_TIMESTAMP_FILE
        if fn:
            try:
                f = open(fn, "r")
            except IOError:
                return None
            else:
                s = f.read()
                f.close()
                return s

    def parse_commit(self):
        d = feedparser.parse(self.commit_url)
        if not d.feed.updated == self.get_stamp("commit"):
            self.save_stamp("commit", d.feed.updated)
            return d["items"][0]

    def format_commit_message(self, entry):
        msg = ":outbox_tray: **New commit by {1}:**\n```{0}```\n<{2}>".format(
            entry["title"],
            entry["author"],
            entry["link"]
        )
        return msg

    def check_commit(self):
        e = self.parse_commit()
        if e:
            return self.format_commit_message(e)
        else:
            return False

    def check_issue(self):
        stamp = self.get_stamp("issue")
        if stamp:
            url = "{0}{1}{2}".format(
                self.issue_url, "&since=", stamp
            )
        else:
            url = self.issue_url
        try:
            r = requests.get(url=url)
        except:
            return []
        parsed = r.json()

        try:
            r.json()[0]
        except KeyError:
            print("Nothing recieved from API, call limit?")
            return []    # Probably went over call limit

        # 2016-09-12T20:26:12Z
        messages = []
        if stamp:
            old_stamp = datetime.datetime.strptime(
                stamp,
                "%Y-%m-%dT%H:%M:%SZ"
            )
        latest_stamp = None
        candidate_stamp = old_stamp
        if stamp:
            for issue in parsed:
                new_stamp = datetime.datetime.strptime(
                    issue["created_at"],
                    "%Y-%m-%dT%H:%M:%SZ"
                )
                # print(issue["created_at"], stamp, " | ", old_stamp, new_stamp)
                if new_stamp > old_stamp:
                    if new_stamp > candidate_stamp:
                        candidate_stamp = new_stamp
                        latest_stamp = issue["created_at"]
                    messages.append(self.format_issue_message(issue))
        else:
            print("No stamp, getting it from the latest issue.")
            # messages.append(self.format_issue_message(parsed[0]))
            latest_stamp = parsed[0]["created_at"]

        if latest_stamp:
            self.save_stamp("issue", latest_stamp)

        messages.reverse()
        return messages

    def format_issue_message(self, e):
        try:
            e["pull_request"]
        except KeyError:
            prefix = ":exclamation: **New issue:**"
        else:
            prefix = ":question: **New pull request:**"
        msg = "{pf} *#{n} by {u}*\n```{t}```\n<{url}>".format(
            pf=prefix,
            n=e["number"],
            u=e["user"]["login"],
            t=e["title"],
            url=e["html_url"]
        )
        return msg


if __name__ == "__main__":
    # For testing
    from time import sleep
    f = RSSFeed()
    while True:
        print(f.check_issue())
        # print(f.check_commit())
        sleep(5)
