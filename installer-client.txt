Commandes à suivre pour l installation du projet :
#(A AFIRE UNIQUEMENT QUAND LE DOSSIER EST EXTRAIT DANS LES TELECHARGEMENTS)
su
toto
apt update
apt install -y python3 python3-pip python3-venv libxcb-xinerama0 libqt5gui5 libqt5core5a libqt5widgets5
#SI VOUS AVEZ CE MESSAGE :
#Attente du verrou du cache: Impossible d obtenir le verrou /var/lib/dpkg/lock-frontend. Il est occupé par le processus 1673 (packagekitd)
#FAIRE systemctl restart packagekitd
cd /Downloads/SAE-3.02-main/
python3 -m venv .venv
source venv/bin/activate
pip install PyQt5
cd /SAE-3.02-main/src/
python3 main.py