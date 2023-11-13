#!/bin/usr/python3

# This is a sample Python script.
import os
import re
import requests
import shutil
import sys
import threading
import time
from datetime import datetime

from bs4 import BeautifulSoup

# Warning: Do not set this too high. You might crash your computer or DDoS dad.
# not responsible if banana bans you.
MAX_THREADS = 8


# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

def init(uid):
    r = requests.get('https://dad.gallery/users/' + str(uid) + '/submissions')
    if r.status_code == 404:
        print("This user appears to be deleted.")
        return
    elif r.status_code != 200:
        print("Something went Wrong. Status Code: " + str(r.status_code))
        return
    soup = BeautifulSoup(r.text, 'html.parser')
    username = soup.find(string=re.compile(r".*? - Submissions")).split(' ')[0]
    if not os.path.exists(username):
        os.mkdir(username)
    os.chdir(username)

    page_count = 1

    try:
        page_count = int(soup.find(class_="next_page")
                         .previous_sibling.previous_sibling.text)
    except AttributeError:
        # user only has 1 page of submissions
        pass

    return [username, page_count]


def download(uid, page):
    print("Downloading page: " + str(page))
    r = requests.get('https://dad.gallery/users/' + str(uid) +
                     '/submissions?page=' + str(page))

    if r.status_code != 200:
        print("Something went wrong. Status Code: " + str(r.status_code))
        return

    soup = BeautifulSoup(r.text, 'html.parser')
    submissions = soup.find_all('a', class_='submissionThumbnail')

    for submission in submissions:
        href = submission.attrs.get('href')
        r = requests.get('https://dad.gallery' + href)

        if r.status_code != 200:
            print("Something went wrong. Status Code: " + str(r.status_code))
            continue

        soup = BeautifulSoup(r.text, 'html.parser')
        img = soup.find(id="submissionImage").attrs.get('src')
        raw_date = soup.find(string=re.compile(r"Submitted at .*?")).split('Submitted at ')[-1]
        submitted_at = datetime.strptime(raw_date, "%H:%M, %b %d, %Y")
        date_string = submitted_at.strftime('%Y-%m-%dT%H:%M')
        original_filename = img.split('/')[-1]
        filename = date_string + '_' + original_filename

        if os.path.isfile(filename):
            continue

        r = requests.get(img, stream=True)
        if r.status_code == 200:
            with open(filename, 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)

    print("Finished page " + str(page))


def main(uid):
    [username, page_count] = init(uid)
    if username:
        for page in range(1, page_count + 1):
            worker = threading.Thread(target=download, args=(uid, page))
            worker.start()
            while threading.active_count() >= MAX_THREADS:
                time.sleep(1)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    try:
        main(int(sys.argv[1]))
    except ValueError as e:
        print("Couldn't get he user ID. Did you use the username by mistake?")
        raise e

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
