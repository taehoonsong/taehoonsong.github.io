#!/usr/bin/env bash

./build.sh all

cd pages

uv run python -m http.server 8000 &
http_server_pid=$!

# Trap sigint and kill all background processes
trap 'kill "$http_server_pid"; exit' SIGINT

user_os=$(uname)
if [ "$user_os" == "Linux" ]; then
  xdg-open "http://localhost:8000"
elif [ "$user_os" == "Darwin" ]; then
  open "http://localhost:8000"
fi


# Watch for file changes
cd -
watchman-make -p "content/*" "static/**/*" "templates/*" "filters/*" "generate_website.py" -r "./build.sh all"
