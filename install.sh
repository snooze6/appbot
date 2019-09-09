echo "[+] - We are in "$PWD

echo "[+] - Creating virtualenv"
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate

echo "[+] - Creating service"
sed "s:\x7bPATH\x7d:$PWD:g" appbot.service.template > appbot.service # ':' is due to $PWD containing '/'
cat appbot.service
read -r -p "[+] - Are you sure? [y/N] " response
case "$response" in
    [yY][eE][sS]|[yY])
        sudo cp appbot.service /lib/systemd/system/appbot.service
        sudo systemctl daemon-reload
        sudo systemctl start appbot.service
        sudo systemctl enable appbot.service
        ;;
    *)
        echo "[+] - Not creating service"
        ;;
esac

echo "[+] - Finished"
