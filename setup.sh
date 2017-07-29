#!/bin/bash

# Install docker, pip, htop and tmux
apt-get update
apt-get -y install python-pip apt-transport-https ca-certificates curl gnupg2 software-properties-common tmux htop
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo apt-key add -
sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/debian \
   $(lsb_release -cs) \
   stable"
apt-get update
apt-get install -y docker-ce

# Install docker-compose
pip install docker-compose

# Build & pull the containers
docker-compose build
docker-compose pull
