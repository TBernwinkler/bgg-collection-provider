#!/usr/bin/env sh

cd /usr/src/app/bgg-collection-provider
pip install --no-cache-dir -r ./requirements.txt

python ./collectionProviderApi.py > /usr/src/app/logs/backend-api.log
