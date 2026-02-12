---
title: Pathlib vs os
date: 2026-02-12
summary: What are the differences between Python's pathlib and os modules? Which one should you use? How do you go from one to the other?
---
# File management in Python
If you search how to do any kind of file management on Python, you'll come across two modules: `pathlib` and `os` (`os.path` in particular). I will say that in most cases, you will want to use `pathlib`. It provides a more modern and "pythonic" way of interacting with files. You'll often find older tutorials and stack overflow answers using `os.path`. While these are still valid ways to do things, you'll often find it a little clunky and unintuitive.

# The old way
Before Python 3.4, the primary way to interact with files on your system via Python was to use `os.path`. Let's say you want to generate a list of files/directories based on an input file. The input file looks like the following:

```
# input.txt
test1.txt
test2.txt
testdir1/
testdir2/test3.md
```

In order to read this file and create all the necessary files and directories using `os`, you'd have to do the following:

```Python
import os
import contextlib


def get_inputs() -> list[str] | None:
    input_file = "input.txt"
    if not os.path.exists(input_file):
        print("Input file does not exist.")
        return None

    with open(input_file, "r", encoding="utf-8") as f:
        data = f.read().splitlines()

    return data


def create_file(file_name: str) -> None:
    with open(file_name, "a", encoding="utf-8"):
        pass


def create_files(data: list[str]) -> None:
    for item in data:
        if "/" not in item:
            create_file(item)
            continue

        # Assume only one level deep
        dir_name, file_name = item.split("/")
        with contextlib.suppress(FileExistsError):
            os.mkdir(dir_name)
        if file_name != "":
            create_file(item)
```

I'm sure this isn't the best way to do things even with the `os` module. However, this is likely the easiest to follow. You'll notice that I have to do some checks to see if "/" is in the input name and change my behavior. This code also assumes that there's at most one "/" in the input. I'm sure there's a way around this, but it's going to get complicated really fast.

The cleanup script will look like this:

```Python
def cleanup() -> None:
    for dirpath, dirnames, filenames in os.walk("."):
        for file in filenames:
            if "test" not in file:
                continue

            file_path = os.path.join(dirpath, file)
            os.unlink(file_path)

        if "test" in dirpath:
            os.rmdir(dirpath)
```

Honestly, while I was writing this example, I was so unsure of what was going to happen that I had to constantly go back and forth between writing the script and testing the code. Unless you're forced to use an older version of Python, you should stay away from this madness.

# The new way
There are many features that `pathlib` brings that makes our job a lot easier, one of which is converting a file into an object. This means you can access properties and methods associated with the file or directory. Let's try to do the same thing as the examples above, but using `pathlib` instead.

```Python
from pathlib import Path


def get_inputs() -> list[Path]:
    return [Path(item) for item in Path("input.txt").read_text("utf-8").splitlines()]


def create_files(data: list[Path]) -> None:
    for item in data:
        if item.parent != Path("."):
            item.parent.mkdir(exist_ok=True)

        if item.suffix == "":
            item.mkdir(exist_ok=True)
        else:
            item.touch()
```

You can immediately see the benefit of having files as Python objects. We can access the parent folder by calling the `parent` property. We can also use `mkdir` and `touch` on the file object. Also notice that simply reading text from a file is a built-in method. No longer do you need to use `with open(file_name) as f:...`. If you need to do something a little more complex, you can still use `open` on the `Path` object. Alternatively, `open` is a method you can call on the `Path` object directly like so:

```Python
with Path("test1.txt").open("r", encoding="utf-8") as f:
  ...
```

Let's now look at the cleanup script:

```Python
def cleanup() -> None:
    test_files = Path(".").rglob("test*")

    # Delete files first
    for item in test_files:
        if item.is_file():
            item.unlink()

    test_dirs = Path(".").rglob("test*")
    for item in test_dirs:
        item.rmdir()
```

We use `rglob` to recursively glob all files starting with "test". Then we first delete all files to empty out all the test directories. Checking whether the `Path` is a file is as simple as calling `is_file()`. Then, we can call `rmdir` on the now emptied test directories.

# Just use pathlib
As you can see from this trivial example, the methods and properties offered by `pathlib` makes file management much simpler compared to `os`. In most cases, you will want to use `pathlib` over `os` for your sanity's sake. Not only does it offer cross-platform compatibility, it also allows you to create `Path` objects by chaining "/". For example,

```Python
from pathlib import Path

d1 = Path("testdir1")
d2 = d1 / "subdir1" / "subdir2"
d2.mkdir(exists_ok=True, parents=True)

f = d2 / "testfile1.txt"
f.touch()
```

# When to use os
There are still certain operations that you will need to use `os` for, however. The main one being `chown`. Because `chown` requires administrator privileges, `pathlib` does not offer such a method. Essentially, anything that requires elevated privileges will require you to use `os`. In all other cases, you will want to use `pathlib` for your file management needs in Python.

