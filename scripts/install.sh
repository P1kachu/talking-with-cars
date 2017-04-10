#!/bin/sh

cd /tmp/
git clone https://github.com/hardbyte/python-can.git
cd python-can
sudo python3 setup.py install
