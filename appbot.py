import datetime
import json
import requests
from bs4 import BeautifulSoup
from peewee import *
from telegram.ext import Updater, CommandHandler
import threading

# Apps
apps = []
# Telegram
updater = None
whitelist = None

# Database stuff
db = SqliteDatabase('data.db')


class BaseModel(Model):
    class Meta:
        database = db


class App(BaseModel):
    id = CharField(primary_key=True, unique=True)
    name = CharField()
    os = CharField()
    rank = IntegerField()
    rating = FloatField()
    ratings = IntegerField()
    availability = IntegerField()
    top25 = IntegerField()


class Version(BaseModel):
    app = ForeignKeyField(App, backref='versions')
    number = CharField()
    date = DateTimeField()


def read_config(path="./config.json"):
    with open(path) as f:
        return json.load(f)


def get_info(app):
    def get_arr(row):
        ret = []
        for field in row.find_all("div", {"class": "infobox"}):
            ret.append(field.find_all("p", {"class": "data"})[0].contents[0])
        return ret

    r = requests.get(app["url"])
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

        app["info"] = info
    else:
        raise Exception("AppTrace.com is not responding 200")


def save(apps):
    db.connect()
    db.create_tables([App, Version])
    for app in apps:
        id = app["url"].split('/')[-1]
        dapp = App.select().where(App.id == id).first()
        if dapp:
            if app["info"]["versions"] is not None:
                datetimes = [v["date"] for v in app["info"]["versions"]]
                versions = Version.select().where(Version.app == dapp)
                if versions is not None:
                    for v in versions:
                        if v.date in datetimes: datetimes.remove(v.date)
                    rawv = [v for v in app["info"]["versions"] if v["date"] in datetimes]
                    for v in rawv:
                        # notify(Version(app=dapp, number=v["number"], date=v["date"]))
                        notify(Version.create(app=dapp, number=v["number"], date=v["date"]))
        else:
            dapp = App.create(
                id=id,
                name=app["name"],
                os=app["type"],
                rank=-1 if not app["info"]["rank"].replace('#', '').isdigit() else int(app["info"]["rank"].replace('#', '')),
                rating=-1 if not app["info"]["rating"].replace('.','',1).isdigit() else float(app["info"]["rating"]),
                ratings=-1 if not app["info"]["ratings"].replace(' ', '').isdigit() else int(app["info"]["ratings"].replace(' ', '')),
                availability=-1 if not app["info"]["availability"].split(' ')[0].isdigit() else int(app["info"]["availability"].split(' ')[0]),
                top25=-1 if not app["info"]["top25countries"].split(' ')[0].isdigit() else int(app["info"]["top25countries"].split(' ')[0]),
            )

            if app["info"]["versions"] is not None:
                for v in app["info"]["versions"]:
                    Version.create(
                        app=dapp,
                        number=v["number"],
                        date=v["date"]
                    )


def notify(version):
    url = None
    if version.app.os.lower() == "android":
        url = "https://play.google.com/store/apps/details?id=" + version.app.id + "&hl=en"
    else:
        url = "https://apps.apple.com/us/app/id" + version.app.id
    message = version.app.name + " (" + version.app.os + ") updated to " + version.number + " on " + version.date.strftime("%d/%m/%Y") + ". " + url
    for chat in whitelist:
        updater.bot.send_message(chat_id=chat, text=message)


def doit():
    for app in apps:
        get_info(app)
    save(apps)


def update(bot, update):
    print("[+] - Execute manual update")
    for chat in whitelist:
        updater.bot.send_message(chat_id=chat, text="Updating...")
    doit()


def update_task():
    print("[+] - Executing scheduled update")
    doit()
    # timer = threading.Timer(10, update_task)
    timer = threading.Timer(86400, update_task)
    timer.start()


if __name__ == "__main__":
    print("[+] - Starting")
    print("[+] - Reading config")
    config = read_config()
    apps = config["apps"]
    whitelist = config["whitelist"]
    for app in apps: print("[+] - " + app["name"] + " - " + app["type"])

    updater = Updater(config["token"])

    # doit()

    print("[+] - Starting background task")
    update_task()

    print("[+] - Starting manual update handler")
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('update', update))
    updater.start_polling()
    updater.idle()
