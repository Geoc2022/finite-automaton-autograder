#!/usr/bin/env bash

apt install -y software-properties-common curl
add-apt-repository -y ppa:deadsnakes/ppa

apt-get update
yes | apt-get install -y python3.13 python3.13-dev python3.13-venv
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.13

python3.13 -V
python3.13 -m pip install -U pip wheel setuptools
python3.13 -m pip install -r /autograder/source/requirements.txt