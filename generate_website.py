import datetime as dt
import json
import shutil
from pathlib import Path
from typing import TypedDict

import jinja2 as jj
from markdown import markdownFromFile

SRC_PATH = Path("content")
OUTPUT_PATH = Path("pages")
POSTS_PATH = OUTPUT_PATH / "posts"
TEMPLATE_PATH = Path("templates")
STATIC_DIR = Path("static")


class SocialMediaLink(TypedDict):
    label: str
    url: str
    svg_path: str
    svg_data: str


def prep_jinja() -> jj.Environment:
    loader = jj.FileSystemLoader(TEMPLATE_PATH)
    env = jj.Environment(loader=loader, autoescape=True)

    return env


# ! TODO: convert markdown files in SRC_PATH to html.
# Implement syntax highlighting in code blocks.
# Should support Python, SQL at minimum. Look into LaTeX rendering later.
def markdown_to_html(md_file: Path) -> None:
    output_path_str = f"{POSTS_PATH}/{md_file.stem}.html"
    markdownFromFile(input=str(md_file), output=output_path_str, encoding="utf-8")


def get_data() -> dict:
    path = SRC_PATH / "resume.json"
    with path.open(encoding="utf-8", errors="ignore") as f:
        data = json.load(f)

    # For copyright notice in footer
    data["current_year"] = dt.datetime.now(tz=dt.UTC).year

    # Make fullname
    data["name"] = f"{data['first_name']} {data['last_name']}"

    if "social_media_links" not in data:
        return data

    # Add svg data for each social link
    social_media_links: list[SocialMediaLink] = data["social_media_links"]

    for link in social_media_links:
        svg_path = link.get("svg_path")
        if svg_path is None:
            continue

        with Path(svg_path).open(encoding="utf-8", errors="ignore") as f:
            link["svg_data"] = f.read()

    return data


def render_templates(env: jj.Environment, data: dict) -> list[tuple[str, str]]:
    results = []
    for t in TEMPLATE_PATH.iterdir():
        if not t.suffix.lower().endswith(".html"):
            continue

        jinja_temp = env.get_template(t.name)
        results.append((t.name, jinja_temp.render(**data)))

    return results


def clean_output_path() -> None:
    if not OUTPUT_PATH.exists():
        return

    shutil.rmtree(OUTPUT_PATH)


def copy_static_to_output() -> None:
    for item in STATIC_DIR.iterdir():
        if item.is_dir():
            shutil.copytree(item, f"{OUTPUT_PATH}/{item.name}")
        else:
            shutil.copy(item, f"{OUTPUT_PATH}/{item.name}")


def export_outputs(render_results: list[tuple[str, str]]) -> None:
    OUTPUT_PATH.mkdir(exist_ok=True)
    copy_static_to_output()

    for result in render_results:
        file_name, html = result
        export_path = OUTPUT_PATH / file_name
        with Path(export_path).open("w", encoding="utf-8") as f:
            f.write(html)


def export_posts() -> None:
    POSTS_PATH.mkdir(exist_ok=True)
    blog_posts = [f for f in SRC_PATH.iterdir() if f.suffix.lower() == ".md"]
    for post in blog_posts:
        markdown_to_html(post)


def main() -> None:
    data = get_data()
    env = prep_jinja()
    clean_output_path()

    render_results = render_templates(env, data)
    export_outputs(render_results)
    export_posts()


if __name__ == "__main__":
    main()
