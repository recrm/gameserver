#!/bin/bash

trap "kill 0" EXIT

python3 -m backend &
npm start --prefix frontend

wait