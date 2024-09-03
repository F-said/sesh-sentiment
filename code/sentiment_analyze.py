from openai import OpenAI
import csv

import time

from config import KEY, system_prompt

LIMIT = 200

"""
Couldnt get ChatGPT to analyze this csv file simply through the web-interface,
so we'll instead query each row. (Ty to ChatGPT for providing this code)
"""


# Function to query the API for sentiment
def get_sentiment(text, title):
    prompt = f"""
    What is the sentiment of this comment from Reddit on sesh nicotine pouches?
    "{text}"

    Please respond using only one word.
    """

    stream = client.chat.completions.create(
        model="gpt-4o-2024-08-06",
        messages=[{
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        max_tokens=60
    )
    # strip to get only sentimnet
    sentiment = stream.choices[0].message.content.\
        lower().strip('\n').replace(' ', '')
    return sentiment


client = OpenAI(api_key=KEY)

sentiments = []

inpath = "data/csv/sesh_comments.csv"
outpath = "data/csv/sentiments.csv"

# Load the CSV file
with open(inpath, 'r', encoding="utf8") as csvfile:
    links = csv.reader(csvfile)
    # skip the headers
    next(links, None)

    index = 0
    for row in links:
        if index > LIMIT:
            break
        time.sleep(20)
        text = row[1]
        title = row[3]

        print(f"Analyzing {text}")
        sentiment = [get_sentiment(text, title)]
        print(f"Sentiment {sentiment}")
        sentiments.append(sentiment)
        index += 1

# Save the results to a new CSV file
with open(outpath, 'w', newline='') as f:
    # using csv.writer method from CSV package
    write = csv.writer(f)

    write.writerow(["sentiment"])
    write.writerows(sentiments)
