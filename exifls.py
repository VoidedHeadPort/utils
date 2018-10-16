#!/usr/bin/python3.6

from collections import OrderedDict

import os
import exiftool
import fileinput

et = exiftool.ExifTool()
et.start()

class Media:
    def __init__(self, filename):
        self.filename_ = filename
        self.metadata_ = et.get_metadata(self.filename_)
        self.status_ = self.generate_status(self.metadata_)

    def generate_status(self, metadata):
        status = OrderedDict()
        status['original'] = self.generate_status_original(metadata)
        status['microsoft'] = self.generate_status_microsoft(metadata)
        status['google'] = self.generate_status_google(metadata)
        status['rotated'] = self.generate_status_rotated(metadata)
        status['thumbnail'] = self.generate_status_thumbnail(metadata)
        return status

    def generate_status_char(self, metadata, tags, char):
        count = 0

        for key, value in tags.items():
            if key in metadata:
                if type(value) is bool:
                    count = count + 1
                elif value in metadata[key]:
                    count = count + 1

        if count == len(tags):
            return char.upper()
        elif count > 0:
            return char.lower()
        else:
            return '-'

    def generate_status_original(self, metadata):
        tags = {
            'File:ExifByteOrder': 'II', # "Little-endian"
            'EXIF:InteropIndex': 'R98', # "sRGB"
        }

        return self.generate_status_char(metadata, tags, 'O')

    def generate_status_microsoft(self, metadata):
        tags = {
            'EXIF:OffsetSchema': True, # defined
            'XMP:About': "uuid:faf5bdd5-ba3d-11da-ad31-d33d75182f1b",
            # Not all versions of Microsoft Windows Photo Viewer do this
            # 'XMP:DateAcquired': True, # defined
        }

        status = self.generate_status_char(metadata, tags, 'M')

        if status == 'M':
            bonus_tags = {
                'File:ExifByteOrder': 'MM',  # "Big-endian"
            }

            if self.generate_status_char(metadata, bonus_tags, 'M') != 'M':
                status = status.lower()

        return status

    def generate_status_google(self, metadata):
        return '-'

    def generate_status_rotated(self, metadata):
        return '-'

    def generate_status_thumbnail(self, metadata):
        return '-'

    def status_string(self):
        return ''.join(self.status_.values())

def process_lines():
    for line in fileinput.input():
        line = line.rstrip()

        if os.path.isfile(line):
            media = Media(line)
            print(media.status_string(), '\t', line)
        else:
            print(line)


if __name__ == "__main__":
    process_lines()