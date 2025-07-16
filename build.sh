#!/bin/bash

APP_DIR=$(pwd)

docker run --rm -it \
  -v "$APP_DIR":/home/user/app \
  -w /home/user/app \
  kivy/buildozer \
  buildozer android debug
