echo "Cloning Repo...."
if [ -z $BRANCH ]
then
  echo "Cloning main branch...."
  git clone https://github.com/ZauteKm/UsePyrogramBot /UsePyrogramBot
else
  echo "Cloning $BRANCH branch...."
  git clone https://github.com/ZauteKm/UsePyrogramBot -b $BRANCH /UsePyrogramBot
fi
cd /UsePyrogramBot
pip3 install -U -r requirements.txt
echo "Starting Bot...."
python3 bot.py
