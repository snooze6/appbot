import datetime
import re
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


def fetch(url):
    def get_arr(row):
        ret = []
        for field in row.find_all("div", {"class": "infobox"}):
            ret.append(field.find_all("p", {"class": "data"})[0].contents[0])
        return ret

    r = requests.get(url)
    if r.status_code == 200:
        content = BeautifulSoup(r.content, 'html.parser')

        info = {
            "age": None,
            "availability": None,
            "activity": None,
            "ratings": None,
            "rank": None,
            "top25countries": None,
            "rating": None,
            "versions": None
        }

        # Parsing Round up
        table = content.body.find(id='content').div.find_all("div", {"class": "inforow"})
        row = table[0]
        arr = get_arr(row)
        info["age"] = arr[0]
        info["availability"] = arr[1]
        info["activity"] = arr[2]
        row = table[1]
        arr = get_arr(row)
        info["ratings"] = arr[0]
        info["rank"] = arr[1]
        info["top25countries"] = arr[2]

        aside = content.body.find(id='aside')

        # Parsing ratings
        rating = aside.find_all("div")[0].find_all("div")[4]
        info["rating"] = rating.strong.contents[0]
        # print(rating.span.contents[0])

        # Parsing versions
        versions = aside.find_all("div")[9]
        for row in versions.find_all("div")[2].find_all("div", {"class": "row"}):
            d = row.find_all("div", {"class": "cell"})
            if info["versions"] is None:
                info["versions"] = []
            info["versions"].append({
                "number": d[0].contents[0],
                "date": datetime.datetime.strptime(d[1].contents[0], '%B %d %Y')
            })

        app = {}
        app["url"] = app
        app["info"] = info
        app["id"] = url.split('/')[-1]
        app["type"] = "Android" if app["id"].isdigit() else "iOS"
        app["name"] = content.body.find(id="headline_properties_artwork").h1.contents[0]
        return app
    else:
        raise Exception("AppTrace.com is not responding 200")


def isApp(app):
    def is_url(url):
        try:
            result = urlparse(url)
            return True
        except ValueError:
            return False

    try:
        if is_url(app):
            parsed = urlparse(app)
            regex = re.compile('([a-z]+\.)+[a-z]+')
            if 'apptrace.com' == parsed.netloc \
                    and parsed.scheme == 'https' \
                    and '/app/' in parsed.path \
                    and (parsed.path.replace('/app/', '').isdigit() or regex.match(parsed.path.replace('/app/', ''))) \
                    and parsed.params == '' \
                    and parsed.query == '' \
                    and parsed.fragment == '':
                return True
    except Exception:
        return False
    return False


if __name__ == "__main__":
    print(isApp("https://apptrace.com/app/544007664"))
    print(isApp("https://apptrace.com/app/com.duolingo"))
    print(isApp("https://apptrace.com/app/com\"<script>"))
