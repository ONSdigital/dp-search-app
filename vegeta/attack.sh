#! /bin/bash

if [ ! -f ./vegeta ]; then
    wget https://github.com/tsenart/vegeta/releases/download/v6.3.0/vegeta-v6.3.0-darwin-386.tar.gz
    tar -xvf vegeta-v6.3.0-darwin-386.tar.gz
fi

echo "GET http://localhost:5000/recommend/user?count=10" | ./vegeta attack -duration=5s -connections 10 -rate 1000 | tee results.bin | ./vegeta report
