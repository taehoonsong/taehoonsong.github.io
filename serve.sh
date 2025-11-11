#!/usr/bin/env bash

cd pages

uvx python -m http.server &

http_server_pid="$!"
trap 'kill "$http_server_pid"' exit

cd -

xdg-open "http://localhost:8000"
watchman-make -p "content/*" "static/*" "templates/*" "generate_website.py" -r "./build.sh"
