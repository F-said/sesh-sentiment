import urllib.parse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import csv
import time

# set up filepath where links will be saved in
filepath = "data/csv/links.csv"

# Set up the search URL
root = "https://www.google.com/"
url = "https://google.com/search?q="
query = 'site:reddit.com ""sesh"" nicotine pouch'
query = urllib.parse.quote_plus(query)
link = url + query

print(f'Main link to search for: {link}')

# Configure Selenium WebDriver
options = Options()
# options.add_argument('--headless')
options.add_argument("--window-size=1920,1200")
driver = webdriver.Chrome(options=options)
driver.get(link)

# set config for how many links to get
reddit_links = []
page = 0
PAGE_LIM = 10

try:
    while page < PAGE_LIM:
        # Wait until search results are loaded
        wait = WebDriverWait(driver, 15)
        search_div = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#search')))

        # Find elements containing links
        results = search_div.find_elements(
            By.CSS_SELECTOR,
            "div[jscontroller][lang][jsaction][data-hveid][data-ved]"
        )

        # Extract url and title of post
        for result in results:
            try:
                # get title by h3 tag
                title_h3 = result.find_element(By.CSS_SELECTOR, "h3")
                title = title_h3.get_attribute("innerText")

                # get url by a/href tag after h3
                url_a = result.find_element(By.CSS_SELECTOR, "a:has(> h3)")
                url = url_a.get_attribute("href")

                # if this is a reddit link, save to list of links
                if 'reddit.com' in url:
                    reddit_links.append({
                        "url": url,
                        "title": title
                    })
            except Exception as e:
                print(f'Error extracting link: {e}')

        # Find and click the "Next" button to go to the next page of results
        try:
            # get next links
            next_button = driver.find_elements(By.LINK_TEXT, "Next")
            if len(next_button):
                # wait a sec
                time.sleep(2)
                # click on button
                next_button[-1].click()
            page += 1
        except Exception as e:
            print("No more pages or error navigating to the next page:", e)
            break
finally:
    driver.quit()

# load into csv file
header = ["url", "title"]
with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=header)
    writer.writeheader()
    writer.writerows(reddit_links)
