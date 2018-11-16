
import argparse
import difflib
import exiftool


class MetaData(dict):
    def __init__(self, data):
        super().__init__(data)
        self._keys = list(data)

    def keys(self):
        return self._keys

    def sort(self, *args, **kwargs):
        self._keys.sort(*args, **kwargs)

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._keys[key]
        else:
            return super().__getitem__(key)

    def __iter__(self):
        yield from self._keys


def parse_args():
    parser = argparse.ArgumentParser("Display a side-by-side comparison of exif data")
    parser.add_argument('-s', '--sorted', action='store_true', default=True)
    parser.add_argument('-u', '--unsorted', dest='sorted', action='store_false')
    parser.add_argument('-W', '--width', type=int, default=80)
    parser.add_argument('file', type=str)
    parser.add_argument('files', nargs='+', type=str)
    args = parser.parse_args()
    args.files.insert(0, args.file)
    del args.file
    return args


def get_metadata(files):
    # We should force exiftool to use -G1 (it gives better group names than the default -G setting)
    # Also force the results to be the text version (rather than the default -n setting)
    # Both of these are set using ["-common_args", "-G", "-n"] when start() is called on the ExifTool context manager
    # The arguments ["-a", "-G1", "--n"] should get this effect
    # This doesn't work because -common_args are added at the end - overriding my attempt at overriding the values...
    metadata = []
    with exiftool.ExifTool() as et:
        for data in et.get_metadata_batch(["-a", "-G1", "--n"] + files):
            metadata.append(MetaData(data))
    return metadata


def sort_metadata(metadata):
    # We can't sort the dictionary, we'll have to use sorted(dictionary) which returns a list of sorted keys
    for md in metadata:
        md.sort()
    return metadata


def filter_opcodes(opcodes, metadata):
    filtered = []

    for opcode in opcodes:
        tag, i1, i2, j1, j2 = opcode

        if tag != 'replace':
            filtered.append(opcode)
        else:
            i = i1
            j = j1
            while i < i2 or j < j2:
                if i < i2:
                    ik = metadata[0][i]
                    iv = str(metadata[0][ik])
                    left = ik + " : " + iv
                else:
                    ik = iv = None
                    left = ""

                if j < j2:
                    jk = metadata[1][j]
                    jv = str(metadata[1][jk])
                    right = jk + " : " + jv
                else:
                    jk = jv = None
                    right = ""

                assert(ik != jk)
                if ik != None and (jk == None or ik < jk):
                    i = i + 1
                    right = ""
                    sym = tag_symbol['delete']
                else:
                    assert(ik == None or ik > jk)
                    j = j + 1
                    left = ""
                    sym = tag_symbol['insert']

    #return filtered
    return opcodes


def calculate_diff(metadata):
    # All input will have to be sorted, otherwise it will use whatever uncontrollable order map uses
    # It's possible to have the json parser put it into an OrderedDict, however we need to get that working through the
    # exiftool plugin. More info: https://stackoverflow.com/questions/6921699/can-i-get-json-to-load-into-an-ordereddict
    # Keys are in the expected order - I believe there was a PEP that fixed dict ordering (at least for python 3.6+)
    diff = []
    for i in range(len(metadata) - 1):
        s = difflib.SequenceMatcher(None, list(metadata[i]), list(metadata[i+1]))
        opcodes = filter_opcodes(s.get_opcodes(), [metadata[i], metadata[i+1]])
        diff.append(s.get_opcodes())
    return diff


tag_symbol = {
    'replace': '|',
    'delete':  '<',
    'insert':  '>',
    'equal':   ' '
}


def print_opcode(metadata, opcode, width):
    width = int((width - 3) / 2)
    fmt = "{{:{width}.{width}}} {{}} {{:{width}.{width}}}".format(width=width)
    tag, i1, i2, j1, j2 = opcode

    if tag == 'replace':
        assert(i1 != i2)
        assert(j1 != j2)
    elif tag == 'delete':
        assert(i1 != i2)
        assert(j1 == j2)
    elif tag == 'insert':
        assert(i1 == i2)
        assert(j1 != j2)
    elif tag == 'equal':
        assert(i1 != i2)
        assert(j1 != j2)
        assert(i2 - i1 == j2 - j1)

    i = i1
    j = j1
    while i < i2 or j < j2:
        sym = tag_symbol[tag]

        if i < i2:
            ik = metadata[0][i]
            iv = str(metadata[0][ik])
            left = ik + " : " + iv
        else:
            ik = iv = None
            left = ""

        if j < j2:
            jk = metadata[1][j]
            jv = str(metadata[1][jk])
            right = jk + " : " + jv
        else:
            jk = jv = None
            right = ""

        if tag == 'replace':
            assert(ik != jk)
            if ik != None and (jk == None or ik < jk):
                i = i + 1
                right = ""
                sym = tag_symbol['delete']
            else:
                assert(ik == None or ik > jk)
                j = j + 1
                left = ""
                sym = tag_symbol['insert']
        elif tag == 'delete':
            assert(ik != None)
            assert(jk == None)
            i = i + 1
        elif tag == 'insert':
            assert(ik == None)
            assert(jk != None)
            j = j + 1
        elif tag == 'equal':
            i = i + 1
            j = j + 1
            assert(ik == jk)
            assert(iv != None and jv != None)
            if iv != jv:
                sym = tag_symbol['replace']

        print(fmt.format(left, sym, right))


def print_opcodes(metadata, opcodes, width):
    for opcode in opcodes:
        print_opcode(metadata, opcode, width)


def print_diff(metadata, diff, width):
    for i, opcodes in enumerate(diff):
        print_opcodes(metadata[i:i+2], opcodes, width)
        print()


def exif_diff(args):
    metadata = get_metadata(args.files)
    if args.sorted:
        sort_metadata(metadata)
    diff = calculate_diff(metadata)
    print_diff(metadata, diff, width=args.width)


if __name__ == "__main__":
    args = parse_args()
    exif_diff(args)