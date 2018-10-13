#!/usr/bin/python3.6

import fileinput
import itertools
import os


def rename(source, destination):
    if os.path.lexists(destination):
        print( '\t', 'FAILED - File already exists')
    else:
        os.renames(source, destination)
        print( '\t', 'SUCCESS!')

def processDuplicates(duplicates):
    if len(duplicates) <= 1:
        return

    original = duplicates[0]
    print(original)

    index = 1
    for duplicate in itertools.islice(duplicates, 1, None):
        while True:
            destination = '/'.join(['..', 'Pictures-Duplicates-{:03}'.format(index), original])
            # Increment the index for the next duplicate
            index = index + 1

            if not os.path.exists(destination):
                break

        print(duplicate, '->', destination, sep='\t', end=''),
        rename(duplicate, destination)
        print()

    print()


def processLines():
    duplicates = []

    for line in fileinput.input():
        line = line.rstrip()

        if line:
            duplicates.append(line)
        else:
            processDuplicates(duplicates)
            duplicates = []

    processDuplicates(duplicates)


if __name__ == "__main__":
    processLines()