import json
import csv

import glob
import os

from datetime import datetime


def recurse_comments(reply):
    # get data
    comment = reply["body"]
    comment = comment.replace("\n", "")

    score = reply["score"]
    date = reply["created"]

    # convert timestamp to UTC
    dt_object = datetime.fromtimestamp(float(date))
    formatted_time = dt_object.strftime('%m/%d/%Y %H:%M')

    # append to global row
    row = {
        "date": formatted_time,
        "text": comment,
        "score": score,
        "title": title
    }

    rows.append(row)

    # get next layer of replies if exists
    try:
        replies = reply["replies"]["data"]["children"]
    except (KeyError, TypeError) as e:
        print("No more comments, recursion complete.", e)
        return

    # recurse through comments and append to rows
    for next_reply in replies:
        # skip non-comments
        if next_reply["kind"] != "t1":
            continue
        recurse_comments(next_reply["data"])


data_path = 'data/json/'
json_obs = []

# load each json object into a list
for fname in glob.glob(os.path.join(data_path, '*.json')):
    with open(fname, mode='r') as f:
        json_obs.append(json.load(f))

# iterate through each json object and parse date_created, textual content,
# score of post, score of comment, and title of post (for association)
# TODO: Consider parent of post, for more complex analysis

header = ["date", "text", "score", "title"]
rows = []

for obj in json_obs:
    # attempt to get self text
    try:
        first_obj = obj[0]["data"]["children"][0]["data"]
    except (KeyError, TypeError) as e:
        print("Malformed JSON, skipping self text", e)

    is_self = first_obj["is_self"]

    # retrieve selftext if exists
    self_text = first_obj["selftext"] if is_self else "Media"
    self_text = self_text.replace("\n", "")

    # get post date, upvotes, downvotes, title
    score = first_obj["score"]
    title = first_obj["title"]
    date = first_obj["created"]

    # convert timestamp to UTC
    dt_object = datetime.fromtimestamp(float(date))
    formatted_time = dt_object.strftime('%m/%d/%Y %H:%M')

    self_row = {
        "date": formatted_time,
        "text": self_text,
        "score": score,
        "title": title
    }

    rows.append(self_row)

    # attempt to get all comments
    try:
        second_obj = obj[1]["data"]["children"]
    except (KeyError, TypeError) as e:
        print("No comments", e)

    # iterate through all comments under post, until no more comments possible
    # threads are arbitrarily long, so keep searching until
    # replies can no longer be found
    for thread in second_obj:
        # TODO: Repetetive of above function, abstract away
        # skip non-comments
        if thread["kind"] != "t1":
            continue
        comments = thread["data"]

        # get first comment
        comment = comments["body"]
        comment = comment.replace("\n", "")

        # get post date, upvotes, downvotes, title
        score = comments["score"]
        date = comments["created"]

        # convert timestamp to UTC
        dt_object = datetime.fromtimestamp(float(date))
        formatted_time = dt_object.strftime('%m/%d/%Y %H:%M')

        # next row
        row = {
            "date": formatted_time,
            "text": comment,
            "score": score,
            "title": title
        }

        rows.append(row)

        # iterate through all replies if they exist
        try:
            replies = comments["replies"]["data"]["children"]
        except (KeyError, TypeError) as e:
            print("No more replies, next thread", e)
            continue

        # replies can have subsequent replies, handle recursivley
        for reply in replies:
            # skip non-comments
            if reply["kind"] != "t1":
                continue
            recurse_comments(reply["data"])


# write out to csv file
filepath = "data/csv/comments.csv"
with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=header)
    writer.writeheader()
    writer.writerows(rows)
