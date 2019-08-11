# Appbot

This is a simple Telegram bot under 200 lines that notifies you when some app of a given app list is updated into the play store or app store.

To do so it uses [Apptrace](https://www.apptrace.com) website which is free to use and is updated daily.

## Instalation

The first step is to create a config.json file as the one included as config.json.template. This step is pretty straightforward as it only consists in searching for the right urls on Apptrace.

After creating a config.json file, with  an user able to invoke sudo it should be as simple as running the install.sh file:

```bash
sh install.sh
```

It should create a systemctl service called appbot which launches the service from the actual path

The only requirement is having Python3 with virtualenv installed.

If the service is running you should see something like this:

```bash
➜  ~ systemctl status appbot
● appbot.service - Dummy Service
   Loaded: loaded (/lib/systemd/system/appbot.service; enabled; vendor preset: disabled)
   Active: active (running) since Sun 2019-08-11 10:33:00 UTC; 4h 22min ago
 Main PID: 12721 (python3)
    Tasks: 9 (limit: 1150)
   Memory: 65.9M
   CGroup: /system.slice/appbot.service
           └─12721 /home/snooze/appbot/venv/bin/python3 /home/snooze/appbot/appbot.py 2> /home/snooze

Aug 11 10:33:00 ocean systemd[1]: Stopped appbot.
Aug 11 10:33:00 ocean systemd[1]: Started appbot.
```

## Telegram setup

First step is to talk to [Botfather](https://telegram.me/BotFather) and get a token.

With the URL that botfather gives, the second step is to start a conversation with the bot and get the chat_id of that conversation in order to add it to the whitelist.


## To do

* Simplify the process of obtaining a chatid
* Add functionality to add apps through a bot command
* Implement a proper log management to debug failures