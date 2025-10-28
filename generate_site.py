from pathlib import Path

import markdown

OUTPUT_FOLDER = Path("docs")
INPUT_FOLDER = Path("src")


def md_to_html(file: Path) -> None:
    with file.open(encoding="utf-8", errors="replace") as f:
        text = f.read()

    html = markdown.markdown(text)
    new_file = OUTPUT_FOLDER / f"{file.stem}.html"

    with new_file.open(encoding="utf-8", mode="w") as f:
        f.write(html)


def main() -> None:
    for file in INPUT_FOLDER.iterdir():
        md_to_html(file)


if __name__ == "__main__":
    main()
