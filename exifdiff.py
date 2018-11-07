
import argparse
import exiftool


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
    with exiftool.ExifTool() as et:
        return et.get_metadata_batch(["-a", "-G1", "--n"] + files)


def sort_metadata(metadata):
    # We can't sort the dictionary, we'll have to use sorted(dictionary) which returns a list of sorted keys
    return metadata


def calculate_diff(metadata, sorted):
    # All input will have to be sorted, otherwise it will use whatever uncontrollable order map uses
    # It's possible to have the json parser put it into an OrderedDict, however we need to get that working through the
    # exiftool plugin. More info: https://stackoverflow.com/questions/6921699/can-i-get-json-to-load-into-an-ordereddict
    # Keys are in the expected order - I believe there was a PEP that fixed dict ordering (at least for python 3.6+)
    return {}


def print_diff(diff, width):
    pass


def exif_diff(args):
    metadata = get_metadata(args.files)
    if args.sorted:
        metadata = sort_metadata(metadata)
    diff = calculate_diff(metadata, sorted=args.sorted)
    print_diff(diff, width=args.width)


if __name__ == "__main__":
    args = parse_args()
    exif_diff(args)