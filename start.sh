# chmod +x start.sh
cd ~/reposter/
pkill -f reposter.py

git reset --hard 
git pull

rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
python --version ///// Has to be Python 3.7.16+
pip install -r requirements.txt
python ~/reposter/reposter.py