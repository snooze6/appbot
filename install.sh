echo "We are in "$PWD
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
sed "s:\x7bPATH\x7d:$PWD:g" appbot.service.template > appbot.service # ':' is due to $PWD containing '/'
sudo cp appbot.service /lib/systemd/system/appbot.service
sudo systemctl daemon-reload
systemctl start appbot.service
systemctl enable appbot.service