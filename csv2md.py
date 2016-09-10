#!/usr/bin/env python3

from os.path import realpath, exists, splitext
from argparse import ArgumentParser
import sys
import csv

# some global variables for console output
sWarn = "WARNING"
sErr = "ERROR"
sInfo = "INFO"


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
                        help="Path to the file you want to convert into Markdown. Must be a csv-file.")
    parser.add_argument("-o", "--outfile", default=None, type=str, action="store", dest="output",
                        help="Path to the file to write the output to. If not specified, the script will create a " +
                        "new file in the same directory as the input.")
    parser.add_argument("-d", "--delimiter", default=";", type=str, action="store", dest="delimiter",
                        help="The delimiter to use when reading the csv file. The default delimiter is ';'.")
    parsed = parser.parse_args()

    # validate delimiter input
    delimiter = parsed.delimiter
    if str(delimiter).isspace() or len(delimiter) <= 0:
        print("{0}: The delimiter must contain at least one character (not whitespaces or newlines)!".format(sErr))
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

    # open infile for reading
    with open(infile) as csvfile:
        # create a new DictReader for the csvfile
        csvreader = csv.DictReader(csvfile, delimiter=delimiter)
        # initialize the output string and create the table header out of the first row
        outstring = ""
        numColumns = len(csvreader.fieldnames)
        outstring += "| " + " | ".join(csvreader.fieldnames) + " |\n"
        outstring += "| :-: " * numColumns + "|\n"

        # iterate over all table rows and add them to the outstring
        for row in csvreader:
            line = "| "
            for key in csvreader.fieldnames:
                line += str(row[key]) + " | "
            outstring += line + "\n"

    # open outfile for writing and write the output
    with open(outfile, "w") as out:
        out.write(outstring)
