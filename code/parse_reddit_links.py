# Save each unique link as a separate JSON file
import requests
import time

import csv
import json


with open('data/csv/links.csv', newline='') as link_file:
    links = csv.reader(link_file)
    # skip the headers
    next(links, None)

    # read each url and save as json file
    for row in links:
        url = row[0]
        title = row[1]

        # navigate to page
        time.sleep(3)
        try:
            # prepare to read html as json
            json_link = url + ".json"
            response = requests.get(json_link)

            # remove special chars from title
            file = title.translate(str.maketrans(
                {' ': '', '.': '',  "/": '', '?': '', ':': '', ',': '',
                 '\"': '', '!': '', '\'': '', '-': ''}))

            filename = f'data/{file}.json'
            print(f"Creating {filename}")

            # read in file as json
            with open(filename, 'w') as json_file:
                json.dump(response.json(), json_file, indent=4)

        except requests.exceptions.RequestException as e:
            print(f"Error fetching JSON for {url}: {e}")
