# Personal website
Use jinja templates to generate a personal website. Inspired from [portfolio_generator](https://github.com/CoreyMSchafer/portfolio_generator).

## How it works
[`generate_website.py`](./generate_website.py) uses `jinja2` to generate static HTML websites into [`pages`](./pages). The output folder can be changed in the generation script.

## For development
This assumes that [uv](https://github.com/astral-sh/uv) is available and that the repo has been initialized by `uv sync`.
1. Start watchdog: [`./watch.sh`](./watch.sh)
1. In another shell, start the local website: [`./serve.sh`](./serve.sh)
