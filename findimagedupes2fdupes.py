#!/usr/bin/python3.6

import fileinput
import sys


def processLines(prefix):
    if not prefix.endswith("/"):
        prefix += "/"

    for line in fileinput.input():
        line = line.rstrip()

        duplicates = line.split(" " + prefix)
        assert(duplicates[0].startswith(prefix))
        duplicates[0] = duplicates[0][len(prefix):]

        for duplicate in duplicates:
            print(duplicate)

        print()


if __name__ == "__main__":
    prefix = sys.argv.pop(1)
    processLines(prefix)