#!/usr/bin/python3.6

from datetime import datetime
import exiftool
import fileinput
import os
import sys

et = exiftool.ExifTool()
et.start()

EXIF_DATE_FORMAT = '%Y:%m:%d %H:%M:%S'
FILE_DATE_FORMAT = '%Y:%m:%d %H:%M:%S%z'

def parseFileDate(date):
    # Remove the colon from the UTC offset
    date = date[:-3] + date[-2:]
    return datetime.strptime(date, FILE_DATE_FORMAT)

def parseExifDate(date):
    return datetime.strptime(date, EXIF_DATE_FORMAT)

MODIFY_TAGS = ['EXIF:ModifyDate', 'QuickTime:ModifyDate']
CREATE_TAGS = ['EXIF:CreateDate', 'EXIF:DateTimeOriginal', 'QuickTime:CreateDate']

def calculateModifiedMinutes(filePath):
    metadata = et.get_metadata(filePath)
    fileModifyDate = parseFileDate(metadata['File:FileModifyDate'])

    modifyDate = None
    for tag in MODIFY_TAGS + CREATE_TAGS:
        if tag in metadata:
            modifyDate = parseExifDate(metadata[tag]).replace(tzinfo=fileModifyDate.tzinfo)
            if metadata['File:MIMEType'] == 'video/mp4':
                # The 'QuickTime:ModifyDate' of an mp4 is in UTC.
                # Convert to the same utcoffset as fileModifyDate
                modifyDate = modifyDate + fileModifyDate.tzinfo.utcoffset(None)
            comparisonModifyDate = fileModifyDate
            break

    if not modifyDate:
        # Thumbnail jpeg files don't have a normal modifyDate, just use the fileCreateDate
        modifyDate = parseFileDate(metadata['File:FileCreateDate'])
        comparisonModifyDate = fileModifyDate

    if modifyDate:
        modifiedAge = comparisonModifyDate - modifyDate
        modifiedMinutes = int(modifiedAge.total_seconds() / 60)
    # else:
    #     # mov files have QuickTime:CreateDate and QuickTime:ModifyDate
    #     # They also have QuickTime:(Track|Media)(Create|Modify)Date tags
    #
    #     # Some jpg files only have EXIF:CreateDate and EXIF:DateTimeOriginal (no EXIF:ModifyDate)
    #     # In that case, calculate File:FileModifyDate - EXIF:CreateDate
    #
    #     # mp4 files have QuickTime:CreateData and QuickTime:ModifyDate
    #     # They also have QuickTime:(Track|Media)(Create|Modify)Date tags
    #
    #     print("File is missing modifyDate ({}): {}".format(comparisonModifyDate, path))

    return modifiedMinutes

# if len(sys.argv) == 1:
#     sys.argv.append(".")
#
# for top in sys.argv[1:]:
#     for root, dirs, files in os.walk(top):
#         for file in files:
#             filePath = os.path.join(root, file)
#             modifiedMinutes = calculateModifiedMinutes(filePath)
#             print(modifiedMinutes, '\t', filePath)

def process_lines():
    for line in fileinput.input():
        line = line.rstrip()

        if os.path.isfile(line):
            modifiedMinutes = calculateModifiedMinutes(line)
            print(modifiedMinutes, '\t', line)
        else:
            print(line)


if __name__ == "__main__":
    process_lines()