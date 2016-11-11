#!/bin/sh
virtualenv -p python3.5 env
. ./env/bin/activate
pip3 install -r requirements.txt
