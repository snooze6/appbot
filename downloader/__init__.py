import subprocess
from pprint import pprint


def download(app):
    appname = app
    print("[+] - Downloading " + app)
    return subprocess.call(
        "java -cp ./deps/raccoon-desktop-4.x.y-dev-1.jar de.onyxbits.raccoon.Main -gpa-download " + app,
                           shell=True)


if __name__ == "__main__":
    pprint(download("com.facebook.orca"))
