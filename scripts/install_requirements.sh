sudo apt-get update
sudo apt install python3.12-venv
sudo apt-get remove docker docker-engine docker.io -y
sudo apt install docker.io -y
sudo systemctl start docker
sudo systemctl enable docker
sudo apt install docker-compose-plugin -y

python3 -m venv env
source env/bin/activate

pip install -r ./app/requirements.txt
deactivate


