#!/usr/bin/env bash

./build.sh all

cd pages

uv run python -m http.server &
http_server_pid=$!

# Trap sigint and kill all background processes
trap 'kill "$http_server_pid"; exit' SIGINT

xdg-open "http://localhost:8000"

# Watch for file changes
cd -
watchman-make -p "content/*" "static/**/*" "templates/*" "filters/*" "generate_website.py" -r "./build.sh all"
