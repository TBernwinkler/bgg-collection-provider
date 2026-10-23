#!/usr/bin/env sh

cd /usr/src/app/bgg-collection-provider
pip install --no-cache-dir -r ./requirements.txt

python ./main.py
