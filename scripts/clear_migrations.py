#!/usr/bin/python
import os
import sys
from pathlib import Path

# DANGER !!!!!!!!!!!!!!!

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPTS_DIR)
BASE_PATH = os.path.join(BASE_DIR, "coreplus")

sys.path.append(BASE_DIR)


def remove_migrations(x):
    for file in x.iterdir():
        if file.is_file() and file.name not in ["__init__.py"]:
            os.remove(file)
        else:
            continue


def get_migrations(dirname):
    for x in dirname.iterdir():
        if x.is_dir():
            if x.name == "migrations":
                remove_migrations(x)
            else:
                get_migrations(x)
        else:
            continue


def run():
    # Fetch all questions
    get_migrations(Path(BASE_PATH))


if __name__ == "__main__":
    run()
