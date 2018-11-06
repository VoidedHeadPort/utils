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
        status['apple'] = self.generate_status_apple(metadata)
        status['photoshop'] = self.generate_status_photoshop(metadata)
        status['xmp'] = self.generate_status_xmp(metadata)
        return status

    def generate_status_char(self, metadata, tags, char):
        count = 0

        for key, value in tags.items():
            if key in metadata:
                if type(value) is bool:
                    count = count + 1
                elif type(metadata[key]) is str and \
                        value in metadata[key]:
                    count = count + 1

        if count == len(tags):
            return char
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

        # It can't be upper unless the file is also big-endian.
        # However being big-endian doesn't make it count for lower.
        if status == 'M':
            bonus_tags = {
                'File:ExifByteOrder': 'MM',  # "Big-endian"
            }

            if self.generate_status_char(metadata, bonus_tags, 'M') != 'M':
                status = status.lower()

        # There is a variety of photos that just have the DateAcquired tag
        # This makes them a 'm'
        if status == '-':
            bonus_tags = {
                'XMP:DateAcquired': True,
            }

            status = self.generate_status_char(metadata, bonus_tags, 'm')

        return status

    def generate_status_google(self, metadata):
        tags = {
            'EXIF:Software': "Google",
            'XMP:CreatorTool': "Google",
        }

        status = self.generate_status_char(metadata, tags, 'G')

        # Bonus points for being XMP Core
        if status == 'G':
            bonus_tags = {
                'XMP:XMPToolkit': "XMP Core",
            }

            if self.generate_status_char(metadata, bonus_tags, 'G') != 'G':
                status = status.lower()

        return status

    def generate_status_rotated(self, metadata):
        return '-'

    def generate_status_thumbnail(self, metadata):
        make = metadata.get('EXIF:Make')
        model = metadata.get('EXIF:Model')
        megapixels = None

        if make == "Canon" and model == "Canon PowerShot G12":
            megapixels = 9.98
        elif make == "NIKON" and model == "COOLPIX L1":
            megapixels = 5.94
        elif make == "Samsung" and model == "Galaxy Nexus":
            megapixels = 5.03
        elif make == "LGE" and model == "Nexus 4":
            megapixels = 7.99
        elif make == "LGE" and model == "Nexus 5X":
            megapixels = 12.19
        elif make == "Apple" and model == "iPhone 5":
            megapixels = 5.99
        elif make == "Apple" and model == "iPhone 5c":
            megapixels = 7.99
        elif make == "Apple" and model == "iPhone 5s":
            megapixels = 7.99
        elif make == "Nokia" and model == "6720c-1b":
            megapixels = 5.03
        elif make == "HTC" and model == "HTC Desire":
            megapixels = 4.02
        elif make == "Canon" and model == "Canon DIGITAL IXUS II":
            megapixels = 3.14
        elif make == "Canon" and model == "Canon EOS 5D Mark II":
            megapixels = 21.02
        elif make == "Samsung Techwin" and model == "<KENOX S630  / Samsung S630>":
            megapixels = 5.94
        elif make or model:
            print("Unknown Type")
        else:
            # Screenshots don't have a make or model...
            return 't'

        if megapixels and metadata['Composite:Megapixels'] < megapixels:
            return 'T'

        return '-'

    def generate_status_apple(self, metadata):
        tags = {
            'File:Comment': "AppleMark",
            'EXIF:Software': "QuickTime",
            'ICC_Profile:ProfileCMMType': 'appl', # "Apple Computer Inc."
            'ICC_Profile:PrimaryPlatform': 'APPL', # "Apple Computer Inc."
            'ICC_Profile:DeviceManufacturer': 'appl', # "Apple Computer Inc."
            'ICC_Profile:ProfileCreator': 'appl', # "Apple Computer Inc."
            'ICC_Profile:ProfileCopyright': "Apple Computer Inc.",
        }

        return self.generate_status_char(metadata, tags, 'A')

    def generate_status_photoshop(self, metadata):
        tags = {
            'Photoshop:IPTCDigest': True,
        }

        status = self.generate_status_char(metadata, tags, 'P')

        # Bonus points for being an empty hash
        if status == 'P':
            bonus_tags = {
                'Photoshop:IPTCDigest': "d41d8cd98f00b204e9800998ecf8427e",  # Empty hash
            }

            if self.generate_status_char(metadata, bonus_tags, 'P') != 'P':
                status = status.lower()

        return status

    def generate_status_xmp(self, metadata):
        tags = {
            'XMP:XMPToolkit': True,
            'XMP:CreatorTool': True,
        }

        status = self.generate_status_char(metadata, tags, 'X')

        # Bonus points for being XMP Core
        if status == 'X':
            bonus_tags = {
                'XMP:XMPToolkit': "XMP Core",
            }

            if self.generate_status_char(metadata, bonus_tags, 'X') != 'X':
                status = status.lower()

        return status

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