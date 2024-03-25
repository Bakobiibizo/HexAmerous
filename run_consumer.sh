#!/bin/bash -x
if [ -f .env ]; then
    echo "Loading .env file"
    export $(cat .env | sed 's/#.*//g' | xargs)
fi

python consumer.py

echo "Sleeping for 10 seconds"
sleep 10