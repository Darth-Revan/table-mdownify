#!/usr/bin/env python3

from os.path import realpath, exists, splitext
from argparse import ArgumentParser
import sys
import csv

# some global variables for console output
sWarn = "WARNING"
sErr = "ERROR"
sInfo = "INFO"

# import ODSReader script 'ODSReader.py' written by Marco Conti
try:
    import ODSReader as ods
except ImportError:
    print("{0}: Cannot import ODSReader.py!".format(sErr))
    sys.exit(1)


def gen_outname(infile):
    """
    Takes the path of the input file, removes the current extension, adds the extension for Markdown (.md) and returns
    the resulting path as string.

    Keyword arguments:
    infile -- a file path as string

    Returns:
    The input file path with its extension replaced by '.md'
    """
    name, extension = splitext(infile)
    return name + ".md"


def ask_overwrite():
    """
    Displays a simple command line message asking the user if he wants to overwrite an existing file. If the user input
    equals 'Y' or 'y' the function returns 'True'. With different inputs or in case of a KeyboardInterrupt the function
    returns 'False'.

    Returns:
    True -- If input equals 'Y' or 'y'
    False -- If input is different or a KeyboardInterrupt occurs
    """
    try:
        user_input = input("Do you want to overwrite the file? (Y/N) ").lower()
        if user_input == "y":
            return True
    except KeyboardInterrupt:
        return False
    return False


if __name__ == "__main__":
    # create a new argument parser and add arguments
    parser = ArgumentParser()
    parser.add_argument("-i", "--infile", required=True, type=str, action="store", dest="input",
                        help="Path to the file you want to convert into Markdown. Must be a ods-file.")
    parser.add_argument("-o", "--outfile", default=None, type=str, action="store", dest="output",
                        help="Path to the file to write the output to. If not specified, the script will create a " +
                        "new file in the same directory as the input.")
    parser.add_argument("-s", "--sheet", default="Sheet 1", type=str, action="store", dest="sheet",
                        help="The name of the spreadsheet to convert. Default value is 'Sheet 1'.")
    parser.add_argument("-c", "--clonespanned", action="store_true", dest="clone",
                        help="If set spanned columns will be cloned. Default value is False.")
    parsed = parser.parse_args()

    # validate sheetname input
    sheetname = parsed.sheet
    if str(sheetname).isspace() or len(sheetname) <= 0:
        print("{0}: The sheetname must contain at least one character (not whitespaces or newlines)!".format(sErr))
        sys.exit(1)

    # validate infile
    infile = realpath(parsed.input)
    if not exists(infile):
        print("{0}: Input file '{1}' does not exist! Terminating...".format(sErr, infile))
        sys.exit(1)

    # validate outfile
    outfile = realpath(parsed.output) if parsed.output else gen_outname(infile)
    if exists(outfile):
        print("{0}: Output file '{1}' already exists!".format(sWarn, outfile))
        if not ask_overwrite():
            print("{0}: Not allowed to overwrite file. Terminating...".format(sInfo))
            sys.exit(0)

    # load input file and search for the requested sheet
    doc = ods.ODSReader(infile, clonespannedcolumns=parsed.clone)
    try:
        table = doc.getSheet(sheetname)
    except KeyError:
        print("{0}: The sheet '{1}' does not exist in the specified file!".format(sErr, sheetname))
        sys.exit(1)

    # initialize output string and add the table header
    outstring = ""
    numColumns = len(table[0])
    outstring += "| " + " | ".join(table[0]) + " |\n"
    outstring += "| :-: " * numColumns + "|\n"

    # add rows to the outstring
    for row in table[1:]:
        outstring += "| " + " | ".join(row) + " |\n"

    # write outstring to the output file
    with open(outfile, "w") as out:
        out.write(outstring)
