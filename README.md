# Personal website
Use jinja templates to generate a personal website. Inspired by [portfolio_generator](https://github.com/CoreyMSchafer/portfolio_generator) and [easy-pandoc-templates](https://github.com/ryangrose/easy-pandoc-templates).

## How it works
[`generate_website.py`](./generate_website.py) uses `jinja2` to generate static HTML websites into [`pages`](./pages).

## Prerequisites
1. [uv](https://github.com/astral-sh/uv) is available and the repo has been initialized by `uv sync`.
2. [pandoc](https://pandoc.org)
3. [pywatchman](https://github.com/facebook/watchman)
4. pdflatex, latexmk (usually bundled with TeX distributions)

## Usage
Run [`serve.sh`](./serve.sh)
