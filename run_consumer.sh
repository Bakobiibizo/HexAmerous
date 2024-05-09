#!/bin/bash -x
if [ -f .env ]; then
    echo "Loading .env file"
    export $(cat .env | sed 's/#.*//g' | xargs)
fi

python src/consumer.py

echo "Sleeping for 100 seconds"
sleep 100