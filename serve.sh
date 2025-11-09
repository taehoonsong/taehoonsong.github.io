#!/usr/bin/env bash

OUTPUT_DIR=pages

cd "$OUTPUT_DIR" && uvx python -m http.server
