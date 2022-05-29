#!/bin/bash

# exit if any command fails
set -e
set -x

wait-for-it -t 60 db:5432
wait-for-it -t 60 127.0.0.1:8000

export $(cat .env | grep -v ^# | xargs)
env

make coverage
