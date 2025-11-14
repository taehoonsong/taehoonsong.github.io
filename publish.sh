#!/usr/bin/env bash


./build.sh all

git add ./pages
git commit -m "publish new pages on $(date +%Y-%m-%d)"
git push origin main
