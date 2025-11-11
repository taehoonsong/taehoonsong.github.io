#!/usr/bin/env bash

# Render all templates
uv run generate_website.py


if [ ! -f "./pages/resume.tex" ]; then 
    exit 0 
fi

# Convert resume.tex to pdf using pdflatex
pdflatex --output-directory=pages ./pages/resume.tex

# clean up
cd pages
latexmk -c
