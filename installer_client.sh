sudo apt update
sudo systemctl stop packagekit
sudo sed -i 's|http://deb.debian.org/debian|http://ftp.fr.debian.org/debian|g' /etc/apt/sources.list /etc/apt/sources.list.d/* 2>/dev/null
sudo apt install -y python3 python3-pip python3-venv libxcb-xinerama0 libqt5gui5 libqt5core5a libqt5widgets5
python3 -m venv venv
source venv/bin/activate
pip install PyQt5
cd src/
python3 main.py