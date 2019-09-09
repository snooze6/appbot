# Coded by: HamidrezaMoradi
# www.github.com/hamidrezamoradi

import requests
from bs4 import BeautifulSoup

print('''\033[1;32m
     ___    ____  __ __ ____                      __                __         
    /   |  / __ \/ //_// __ \____ _      ______  / /___  ____ _____/ /__  _____
   / /| | / /_/ / ,<  / / / / __ \ | /| / / __ \/ / __ \/ __ `/ __  / _ \/ ___/
  / ___ |/ ____/ /| |/ /_/ / /_/ / |/ |/ / / / / / /_/ / /_/ / /_/ /  __/ /    
 /_/  |_/_/   /_/ |_/_____/\____/|__/|__/_/ /_/_/\____/\__,_/\__,_/\___/_/     

 \033[1;77m\033[41m      Google Play  Downloader  v1.5,  Author:  @HamidrezaMoradi  (Github)     \033[m\n
''')
GooglePlayLink = input('\033[1;32m Insert a Google Play link or Package name: \033[m')


def PackageName(GooglePlayLink):  # For find Package Name from GooglePlay link - like "com.spotify.music"
    j = 0
    if GooglePlayLink[0:46] == "https://play.google.com/store/apps/details?id=":  # If "GooglePlayLink" is a Link
        for i in GooglePlayLink:
            j += 1
            if i == '=':
                if GooglePlayLink[-3] == '=':
                    return GooglePlayLink[j:-6]
                elif GooglePlayLink[-9] == '&':
                    return GooglePlayLink[j:-9]
                else:
                    return GooglePlayLink[j:]
    elif '.' in GooglePlayLink:  # If "GooglePlayLink" is a Package name
        return GooglePlayLink
    else:
        print('\n\033[31m [!] Your input not true.\033[m')


PackageName = PackageName(GooglePlayLink)


def command_function(downloadUrl):
    if downloadUrl['title'][-1] == 'b':
        Type = 'Data'
    elif downloadUrl['title'][-1] == 'k':
        Type = 'APK'
    command = input('\n\n\n [*] Download %s File Now?([\033[32mY\033[m]es or [\033[31mN\033[m]o)\033[m: ' % Type)
    if command.lower() == 'y':
        print('\033[1;33m\n [*] Wait...\033[m')
        r = requests.get(downloadUrl['href'], allow_redirects=True)
        open('File/%s' % downloadUrl['title'], 'wb').write(r.content)
        print('\n\033[32m [*] Downloaded and save in File folder. Enjoy :)\033[m')
    elif command.lower() == 'n':
        pass
    else:
        print('\n\033[31m [!] Wrong command.\033[n')
        return command_function()


if PackageName is not None:  # If "PackageName" function do not be return "None" value
    apkdl = 'https://apkdl.in/app/details?id=%s' % PackageName
    try:
        r = requests.get(apkdl)
        App_Page = BeautifulSoup(r.text, 'html.parser')
        downloadUrl = App_Page.find("a", itemprop='downloadUrl')
        # For find App/Game info
        print('\n \033[1;33minfo:\033[m\n  \033[34mName: \033[m' + App_Page.find('b').string)
        print('  \033[34mVersion: \033[m' + App_Page.find('span', itemprop='softwareVersion').string)
        print('  \033[34mUpdated on: \033[m' + App_Page.find('span', itemprop='dateModified').string)
        print('  \033[34mDownload size: \033[m' + App_Page.find('span', itemprop='fileSize').string)
        # For find App/Game Download Link
        downloadUrl = ('https://apkdl.in' + downloadUrl['href'])
        r = requests.get(downloadUrl)
        DownloadPage = BeautifulSoup(r.text, 'html.parser')
        downloadUrl = DownloadPage.find_all("a", rel='nofollow')
        if len(downloadUrl) is 2:
            command_function(downloadUrl[1])

        command_function(downloadUrl[0])


    except requests.exceptions.ConnectionError:
        print('\n\033[31m [!] No internet.\n [!] Check your network connection.\033[m')
    except TypeError:
        print('\n\033[31m [!] App/Game not found.\033[m')
    except AttributeError:
        print('\n\033[31m [!] Your input not true.\033[m')
