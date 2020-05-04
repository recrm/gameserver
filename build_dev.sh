#!/bin/bash

export ENV="dev"

trap "kill 0" EXIT

python3 -m backend &
npm start --prefix frontend

wait