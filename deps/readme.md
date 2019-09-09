# Racoon 4

Raccoon is an APK downloader for fetching apps from Google Play.

* Cross platform (Linux, Windows, Mac OS)
* Avoids the privacy issues that arise from connecting your Android device with a Google account
* Easily install apps on multiple devices without downloading them several times.

You can check it out on its [repository](https://github.com/onyxbits/raccoon4)

## Why is Racoon4 here?

It is required for downloading the APKs directly from the app store if the option is enabled. The first time an account need to be configured up in the GUI by directly running the jar:

```bash
java -jar raccoon-desktop-4.x.y-dev-1.jar 
```

After that you could use the CLI by specifying the main class

```bash
java -cp raccoon-desktop-4.x.y-dev-1.jar de.onyxbits.raccoon.Main -gpa-download <com.whatever.package>
```

Though the CLI is not really documented you can check it on

[https://github.com/onyxbits/raccoon4/blob/master/src/main/java/de/onyxbits/raccoon/cli/Router.java](https://github.com/onyxbits/raccoon4/blob/master/src/main/java/de/onyxbits/raccoon/cli/Router.java)

