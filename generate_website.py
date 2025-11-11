import datetime as dt
import json
import shutil
from pathlib import Path
from typing import TypedDict

import pypandoc
from jinja2 import Environment, FileSystemLoader
from slugify import slugify

SRC_PATH = Path("content")
OUTPUT_PATH = Path("pages")
TEMPLATE_PATH = Path("templates")
STATIC_DIR = Path("static")


class SocialMediaLink(TypedDict):
    label: str
    url: str
    svg_path: str
    svg_data: str


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

        with Path(STATIC_DIR, svg_path).open(encoding="utf-8", errors="ignore") as f:
            link["svg_data"] = f.read()

    return data


def render_template(template_name: str, env: Environment, data: dict) -> None:
    jinja_temp = env.get_template(template_name)

    export_path = OUTPUT_PATH / template_name
    content = jinja_temp.render(**data)

    with export_path.open("w", encoding="utf-8") as f:
        f.write(content)


def render_resume(loader: FileSystemLoader, data: dict) -> None:
    env = Environment(
        loader=loader,
        block_start_string="<BLOCK>",
        block_end_string="</BLOCK>",
        variable_start_string="<VAR>",
        variable_end_string="</VAR>",
        autoescape=True,
    )

    file_name = "resume.tex"
    jinja_temp = env.get_template(file_name)

    export_path = OUTPUT_PATH / file_name
    tex = jinja_temp.render(**data)
    with export_path.open("w", encoding="utf-8") as f:
        f.write(tex)


def render_index(loader: FileSystemLoader, data: dict) -> None:
    env = Environment(loader=loader, autoescape=True)

    file_name = "index.html"
    jinja_temp = env.get_template(file_name)

    export_path = OUTPUT_PATH / file_name
    html = jinja_temp.render(**data)

    with Path(export_path).open("w", encoding="utf-8") as f:
        f.write(html)


def render_posts() -> None:
    t = TEMPLATE_PATH / "post.html"
    out_path = OUTPUT_PATH / "posts"
    out_path.mkdir(exist_ok=True)

    [
        pypandoc.convert_file(
            source_file=file,
            to="html5",
            format="gfm",
            extra_args=(f"--template={t!s}", "--toc"),
            outputfile=out_path / f"{slugify(file.stem)}.html",
        )
        for file in SRC_PATH.iterdir()
        if file.suffix.lower() == ".md"
    ]


def main() -> None:
    clean_output_path()

    OUTPUT_PATH.mkdir(exist_ok=True)
    copy_static_to_output()

    loader = FileSystemLoader(TEMPLATE_PATH)

    # Read resume data from JSON file
    data = get_data()

    # Render landing page
    index_env = Environment(loader=loader, autoescape=True)
    render_template("index.html", index_env, data)

    # Render tex that will be converted to PDF later by pdflatex
    resume_env = Environment(
        loader=loader,
        block_start_string="<BLOCK>",
        block_end_string="</BLOCK>",
        variable_start_string="<VAR>",
        variable_end_string="</VAR>",
        autoescape=True,
    )
    render_template("resume.tex", resume_env, data)

    # Render markdown posts to html using pypandoc
    render_posts()


if __name__ == "__main__":
    main()
