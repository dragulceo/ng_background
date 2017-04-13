import subprocess
import re
import urllib
import os
import time
import urllib2
import json

WIDTH = 1920
HEIGHT = 1200

FEED_LOCATION = "http://feeds.nationalgeographic.com/\
ng/photography/photo-of-the-day/"
IMAGE_FORMAT = r"(.*)_[0-9]+x[0-9]+(\.jpg)"
MINIMUM_SECONDS_BETWEEN_DOWNLOADS = 60 * 60 * 6

REDDIT_FEED_LOCATION = "https://www.reddit.com/r/GetMotivated.json"

SCRIPT = """/usr/bin/osascript<<END
tell application "Finder"
    set desktop picture to POSIX file "%s" as alias
end tell
do shell script "killall Dock"
END
"""


def get_large_image_url_from_feed_image_url(url, width, height):
    print url
    return re.sub(IMAGE_FORMAT, "\\1_" +
                  str(width) + "x" + str(height) + "\\2", url)


def set_desktop_background_via_apple_script(filename):
    subprocess.Popen(SCRIPT % filename, shell=True)


def save_url(url, target):
    urllib.urlretrieve(url, target)


def download_last_image_from_source(url, image_getter, target):
    #filename, headers = urllib.urlretrieve(url)
    #with file(filename) as f:
    #    contents = f.read()
    #print contents
    opener = urllib2.build_opener()
    user_agent = "Mozilla/5.0 Windows NT 6.1; WOW64; rv:12.0)\
 Gecko/20100101 Firefox/12.0"
    opener.addheaders = [("User-agent", user_agent)]
    response = opener.open(url)
    contents = response.read()
    #f = open('tmp', "r")
    #contents = f.read()
    #f.close()
    imageurl = image_getter(contents)
    if not imageurl is None:
        save_url(imageurl, target)


def get_first_image_from_text(text):
    images = re.search('(<|&lt;)enclosure\s+url="([^"]*\.jpg)"(\s|>)',
                       text, re.IGNORECASE)
    if images:
        image = images.group(2)
        return get_large_image_url_from_feed_image_url(image, WIDTH, HEIGHT)
    return None


def get_first_image_from_json(loadedJson):
    loaded = json.loads(loadedJson)
    for item in loaded.get('data', {}).get('children', []):
        print item.get('data').get('url')
        found = re.match(
            '(https?://i\.redd\.it/[a-z0-9]+\.jpg|\
https?://(i\.)?imgur\.com/[a-z0-9]+(\.jpg)?)',
            item.get('data', {}).get('url', ''), re.IGNORECASE)
        if found:
            return item.get('data').get('url')
    return None


def setng_background_image():
    target = "/tmp/bkg.jpg"
    seconds_past = MINIMUM_SECONDS_BETWEEN_DOWNLOADS + 1
    if os.path.isfile(target):
        seconds_past = time.time() - os.path.getctime(target)
    if True or seconds_past > MINIMUM_SECONDS_BETWEEN_DOWNLOADS:
        #download_last_image_from_source(FEED_LOCATION,
        #                                get_first_image_from_text, target)
        download_last_image_from_source(REDDIT_FEED_LOCATION,
                                        get_first_image_from_json, target)
        set_desktop_background_via_apple_script(target)


setng_background_image()
