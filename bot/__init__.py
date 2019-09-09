import json
import threading

import logging
from pprint import pformat, pprint

from telegram.ext import Updater, CommandHandler

from apptrace import fetch, isApp
from model import db, App, Version, Config


class Appbot():
    urls = []
    apps = []
    # Telegram
    updater = None
    whitelist = None
    admin = None
    config = None

    time = None

    ####################################################################################################################

    def __init__(self, path="./config.json", time=86400, handle=False):
        db.connect()
        db.create_tables([App, Version, Config])

        if self._first_run():
            logging.debug("[+] - First run")
            logging.debug("[+] - Loading config")
            self.config = self._read_config(path)
            logging.debug("[+] - Saving config")
            self._save_config()
        else:
            logging.debug("[+] - Restoring config from database")
            self.config = self._get_config().config

        self.urls = self.config["apps"]
        self.whitelist = self.config["whitelist"]
        self.admin = self.config["admin"]
        self.updater = Updater(self.config["token"])

        if time:
            self.time = time
            self._automatic_update()

        if handle:
            dp = self.updater.dispatcher
            dp.add_handler(CommandHandler('getid', self.get_chatid))
            dp.add_handler(CommandHandler('get_whitelist', self.get_whitelist))
            dp.add_handler(CommandHandler('add_whitelist', self.add_whitelist, pass_args=True))
            dp.add_handler(CommandHandler('del_whitelist', self.del_whitelist, pass_args=True))
            dp.add_handler(CommandHandler('get_apps', self.get_apps))
            dp.add_handler(CommandHandler('add_app', self.add_apps, pass_args=True))
            dp.add_handler(CommandHandler('del_app', self.del_apps, pass_args=True))
            dp.add_handler(CommandHandler('help', self.show_help))
            dp.add_handler(CommandHandler('update', self.manual_update))

            self.updater.start_polling()
            self.updater.idle()
        else:
            self.doit()

    def _first_run(self):
        return False if self._get_config() else True

    ####################################################################################################################

    def _read_config(self, path):
        with open(path) as f:
            return json.load(f)

    def _get_config(self):
        return Config.select().where(Config.id == 1).first()

    def _save_config(self):
        Config(id=1, config=self.config).save()

    def _update_config(self):
        self.config["apps"] = self.urls
        self.config["whitelist"] = self.whitelist
        self._save_config()

    ####################################################################################################################

    # Save new versions and apps to database
    def _save_app(self, apps):
        for app in apps:
            id = app["id"]
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
                            self._notify(Version.create(app=dapp, number=v["number"], date=v["date"]))
            else:
                dapp = App.create(
                    id=id,
                    name=app["name"],
                    os=app["type"],
                    rank=-1 if not app["info"]["rank"].replace('#', '').isdigit() else int(
                        app["info"]["rank"].replace('#', '')),
                    rating=-1 if not app["info"]["rating"].replace('.', '', 1).isdigit() else float(
                        app["info"]["rating"]),
                    ratings=-1 if not app["info"]["ratings"].replace(' ', '').isdigit() else int(
                        app["info"]["ratings"].replace(' ', '')),
                    availability=-1 if not app["info"]["availability"].split(' ')[0].isdigit() else int(
                        app["info"]["availability"].split(' ')[0]),
                    top25=-1 if not app["info"]["top25countries"].split(' ')[0].isdigit() else int(
                        app["info"]["top25countries"].split(' ')[0]),
                )

                if app["info"]["versions"] is not None:
                    for v in app["info"]["versions"]:
                        Version.create(
                            app=dapp,
                            number=v["number"],
                            date=v["date"]
                        )

    ####################################################################################################################

    # Send the notifications
    def _notify(self, version):
        url = None
        if version.app.os.lower() == "android":
            url = "https://play.google.com/store/apps/details?id=" + version.app.id + "&hl=en"
        else:
            url = "https://apps.apple.com/us/app/id" + version.app.id
        message = version.app.name + " (" + version.app.os + ") updated to " + version.number + " on " + version.date.strftime(
            "%d/%m/%Y") + ". " + url
        for chat in self.whitelist:
            self.updater.bot.send_message(chat_id=chat, text=message)

    ####################################################################################################################

    # Executes automatic updates every self._automatic_update seconds
    # TODO Instead of executing it every X seconds it would be better to actually schedule the task
    def _automatic_update(self):
        logging.debug("[+] - Executing automatic_update")
        self.send_message("Automatic update...")
        self.doit()
        # timer = threading.Timer(10, update_task)
        timer = threading.Timer(self.time, self._automatic_update)
        timer.start()

    ####################################################################################################################

    def doit(self):
        apps = []
        for url in self.urls:
            apps.append(fetch(url=url))
        self.apps = apps
        self._save_app(self.apps)

    ####################################################################################################################

    # Get the chat_id and return it through Telegram
    def get_chatid(self, bot, update):
        chat_id = str(update.message.chat_id)
        logging.debug("[+] - Executing get_chatid for " + chat_id)
        self.updater.bot.send_message(chat_id=chat_id, text=chat_id)

    def manual_update(self, bot, update):
        logging.debug("[+] - Executing manual_update")
        if self._check_whitelist(update):
            self.send_message("Updating...")
            self.doit()

    ####################################################################################################################

    # Get user whitelist
    def get_whitelist(self, bot, update):
        logging.debug("[+] - Executing get_whitelist")
        if self._check_whitelist(update):
            self.updater.bot.send_message(chat_id=update.message.chat_id, text=pformat(self.whitelist))

    # Add an user to the whitelist (only admins)
    def add_whitelist(self, bot, update, args):
        logging.debug("[+] - Executing add_whitelist")
        if self._check_admin(update) and args:
            for arg in args:
                if arg.isdigit():
                    self.whitelist.append(arg)
                    self.send_message("Adding [" + arg + "] to whitelist")
            self._update_config()

    # Remove an chatid from whitelist (only admins)
    def del_whitelist(self, bot, update, args):
        logging.debug("[+] - Executing del_whitelist")
        if self._check_admin(update) and args and len(args) == 1:
            arg = args[0]
            if arg.isdigit() and arg in self.whitelist:
                self.whitelist.remove(arg)
                self.send_message("Removing [" + arg + "] from whitelist")
            self._update_config()

    ####################################################################################################################

    # Get the watchlist of apps
    def get_apps(self, bot, update):
        logging.debug("[+] - Executing get_apps")
        if self._check_whitelist(update):
            self.updater.bot.send_message(chat_id=update.message.chat_id, text=pformat(self.urls))

    # Add an app to the watchlist (only admin)
    def add_apps(self, bot, update, args):
        logging.debug("[+] - Executing add_apps")
        if self._check_admin(update) and args:
            for arg in args:
                if isApp(arg):
                    self.urls.append(arg)
                    self.send_message("Adding [" + arg + "] to apps")
            self._update_config()
            self.doit()

    # Remove an app from the watchlist (only admin)
    def del_apps(self, bot, update, args):
        logging.debug("[+] - Executing del_apps")
        if self._check_admin(update) and args and len(args) == 1:
            arg = args[0]
            if isApp(arg) and arg in self.urls:
                self.urls.remove(arg)
                self.send_message("Removing ["+arg+"] from apps")
            self._update_config()
            self.doit()

    ####################################################################################################################

    # TODO
    def show_help(self, bot, update):
        logging.debug("[+] - Executing show_help")
        if self._check_whitelist(update):
            text = """
dp.add_handler(CommandHandler('getid', self.get_chatid))
dp.add_handler(CommandHandler('get_whitelist', self.get_whitelist))
dp.add_handler(CommandHandler('add_whitelist', self.add_whitelist, pass_args=True))
dp.add_handler(CommandHandler('del_whitelist', self.del_whitelist, pass_args=True))
dp.add_handler(CommandHandler('get_apps', self.get_apps))
dp.add_handler(CommandHandler('add_app', self.add_apps, pass_args=True))
dp.add_handler(CommandHandler('del_app', self.del_apps, pass_args=True))
dp.add_handler(CommandHandler('help', self.show_help))
dp.add_handler(CommandHandler('update', self.manual_update))
"""
            self.updater.bot.send_message(chat_id=update.message.chat_id, text=text)


    ####################################################################################################################

    # Check if chatid is in whitelist
    def _check_whitelist(self, update):
        return str(update.message.chat_id) in self.whitelist

    # Chack if chatid is an admin
    def _check_admin(self, update):
        return str(update.message.chat_id) in self.admin

    ####################################################################################################################

    def download_app(self, app):
        NotImplemented()

    ####################################################################################################################

    def send_message(self, message):
        for chatid in self.whitelist:
            self.updater.bot.send_message(chat_id=chatid, text=message)
