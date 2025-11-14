import datetime as dt
import json
import shutil
from pathlib import Path
from typing import TypedDict
from zoneinfo import ZoneInfo

import frontmatter
import pypandoc
from jinja2 import Environment, FileSystemLoader, select_autoescape
from slugify import slugify

SRC_PATH = Path("content")
OUTPUT_PATH = Path("pages")
TEMPLATE_PATH = Path("templates")
STATIC_DIR = Path("static")
PET_DIR = STATIC_DIR / "img" / "pets"
PET_DIR.mkdir(exist_ok=True, parents=True)


class SocialMediaLink(TypedDict):
    label: str
    url: str
    svg_path: str
    svg_data: str


class BlogPost(TypedDict):
    title: str
    date: dt.datetime
    summary: str
    file_path: str


class BlogPostIndex(TypedDict):
    posts: list[BlogPost]


class PetImage(TypedDict):
    img_path: str


class PetGallery(TypedDict):
    pet_images: list[PetImage]


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


def get_blog_metadata(file: Path) -> BlogPost:
    meta: BlogPost = frontmatter.load(file).metadata
    meta["file_path"] = f"{slugify(meta.get('title'))}.html"
    return meta


def get_blog_post_data() -> BlogPostIndex:
    post_list = [get_blog_metadata(post) for post in SRC_PATH.iterdir() if post.suffix.lower() == ".md"]
    post_list.sort(key=lambda x: x.get("date"), reverse=True)

    return {"posts": post_list}


def get_pet_data() -> PetGallery:
    return {
        "pet_images": [{"img_path": str(path).replace("static", "")} for path in PET_DIR.iterdir()],
    }


def get_portfolio_data() -> dict:
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


def render_template(template_name: str, export_path: Path, env: Environment, data: dict) -> None:
    jinja_temp = env.get_template(template_name)
    content = jinja_temp.render(**data)

    export_path.parent.mkdir(exist_ok=True, parents=True)

    with export_path.open("w", encoding="utf-8") as f:
        f.write(content)


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
            outputfile=out_path / f"{get_blog_metadata(file).get('file_path')}",
        )
        for file in SRC_PATH.iterdir()
        if file.suffix.lower() == ".md"
    ]


def main() -> None:
    clean_output_path()

    OUTPUT_PATH.mkdir(exist_ok=True)
    copy_static_to_output()

    loader = FileSystemLoader(TEMPLATE_PATH)

    # Data to pass into Jinja templates
    portfolio_data = get_portfolio_data()
    blog_data = get_blog_post_data()
    time_data = {
        "now": dt.datetime.now(tz=ZoneInfo("America/New_York")),
        "strftime": dt.datetime.strftime,
        "to_date": dt.datetime.fromisoformat,
    }
    pet_data = get_pet_data()

    data = portfolio_data | blog_data | time_data | pet_data

    # Render landing page
    index_env = Environment(loader=loader, autoescape=select_autoescape())
    render_template("index.html", OUTPUT_PATH / "index.html", index_env, data)

    # Render index of blog posts
    render_template("post_index.html", OUTPUT_PATH / "posts" / "index.html", index_env, data)

    # Render pet gallery
    render_template("pets.html", OUTPUT_PATH / "pets.html", index_env, data)

    # Render tex that will be converted to PDF later by pdflatex
    resume_env = Environment(
        loader=loader,
        block_start_string="<BLOCK>",
        block_end_string="</BLOCK>",
        variable_start_string="<VAR>",
        variable_end_string="</VAR>",
        autoescape=True,
    )
    render_template("resume.tex", OUTPUT_PATH / "resume.tex", resume_env, data)

    # Render markdown posts to html using pypandoc
    render_posts()


if __name__ == "__main__":
    main()
