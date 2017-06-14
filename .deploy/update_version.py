#!/usr/bin/env python3

import sys
import os
import os.path
import re
from glob import glob

semver_re = re.compile("(\d+)\.(\d+)\.(\d+)")
ver_re = re.compile("version := \"(\d+)\.(\d+)\.(\d+)\"")


VERSION_FILE = "./.version"
EXTRA_PATHS = "./.paths"

# TODO read .paths file and append
to_change = ["./build.sbt"] + \
            glob("*.sh") + \
            glob("*.yaml") + \
            glob("./deploy/*") + \
            glob("./deploy/*/*")

def exists_file(fil):
    return os.path.isfile(fil)

def check_files(files):
    good, bad = [], []
    for f in files:
        if exists_file(f):
            good.append(f)
        else:
            bad.append(f)
    return good, bad

# Update paths with custom paths
if exists_file(EXTRA_PATHS):
    paths = []
    with open(EXTRA_PATHS) as f:
        paths = f.read().split("\n")

    for x in paths:
        to_change += glob(x)

class bcolors:
    PINK = '\033[95m'
    OKBLUE = '\033[36m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_with_color(text):
    text = text.\
           replace("{blue}", bcolors.OKBLUE).\
           replace("{error}", bcolors.FAIL).\
           replace("{warning}", bcolors.WARNING).\
           replace("{ok}", bcolors.OKGREEN).\
           replace("{pink}", bcolors.PINK)
    text = "\n".join(["\t" + x for x in text.split("\n")])
    print(text + bcolors.ENDC)

def usage():
    print_with_color("{{blue}}Usage: {} (major|minor|patch)".format(sys.argv[0]))
    exit(1)

def extract_version(vpath = VERSION_FILE):
    text = ""
    if not exists_file(vpath):
        print_with_color("{{error}}File {} don't exist".format(vpath))
        exit(1)
    with open(vpath) as f:
        text = f.read()
    m = semver_re.search(text)
    if m is None:
        print_with_color("{error}Can't extrat semversion from .version content")
    # m = ver_re.search(text)
    # if m is None:
    #     print_with_color("{{error}}Can't extract version from build.sbt")
    #     exit(1)
    major = int(m.group(1))
    minor = int(m.group(2))
    patch = int(m.group(3))
    return (major, minor, patch)

def v(ma, mi, p):
    return "{}.{}.{}".format(ma, mi, p)

def update_version(prev, prox, fname):
    with open(fname, "r") as f:
        text = f.read()

    text = text.replace(prev, prox)

    with open(fname, "w") as f:
        f.write(text)

def rollback(old_old = None):
    to_roll = v(*extract_version(".version_old"))
    old_roll = v(*extract_version())
    print_with_color("{{warning}}Rollback to version {}".format(to_roll))
    correctfiles, _ = check_files(to_change)

    for fname in correctfiles:
        update_version(old_roll, to_roll, fname)
    with open(".version", "w") as f:
        f.write(to_roll)
    if old_old is not None and old_old != to_roll:
        with open(".version_old", "w") as f:
            f.write(old_old)
    else:
        os.remove(".version_old")

def update_version_main(typ):
    if typ not in ["major", "minor", "patch"]:
        usage()

    (major, minor, patch) = extract_version()

    previous = v(major, minor, patch)

    if typ == "major":
        major += 1
        minor = 0
        patch = 0
    elif typ == "minor":
        minor += 1
        patch = 0
    elif typ == "patch":
        patch += 1

    newv = v(major, minor, patch)

    correctfiles, wrongfiles = check_files(to_change)

    print_with_color("{{blue}}Changing version from {{warning}}{}{{blue}} to {{warning}}{}{{blue}}".format(previous, newv))
    if len(correctfiles) > 0:
        print()
        print_with_color("{blue}Files to change:\n-----------")
        [print_with_color("{{ok}}{}".format(f)) for f in correctfiles]
    if len(wrongfiles) > 0:
        print()
        print_with_color("{blue}Files not found:\n-----------")
        [print_with_color("{{error}}{}".format(f)) for f in wrongfiles]

    c = ""
    while c not in ["y", "n"]:
        print()
        cont_text = "\t{}Continue? [y/N]{}".format(bcolors.OKBLUE, bcolors.ENDC)
        c = input(cont_text).lower()
        if c == "":
           c = "n"
    if c == "n":
        exit(2)

    for fname in correctfiles:
        update_version(previous, newv, fname)

    with open(".version_old", 'w') as f:
        f.write(previous)
    with open(".version", 'w') as f:
        f.write(newv)


def main():
    if len(sys.argv) != 2:
        usage()

    typ = sys.argv[1].lower()

    if typ == "rollback":
        old = None
        if os.path.isfile(".version_old"):
            with open(".version_old") as f:
                old = f.read()
        rollback(old)
    else:
        update_version_main(typ)

if __name__ == "__main__":
    main()
