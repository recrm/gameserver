#!/bin/bash

export REACT_APP_ENV="dev"

trap "kill 0" EXIT

python3 -m backend &
npm start --prefix frontend

wait