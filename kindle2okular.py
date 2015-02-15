#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    Convert Kindle My Clippings.txt to an Okular Review File.

    Okular Review files are generated in:
     # OKULAR_HOME/{filesize}.{filename.ext}.xml

    Usage:

        #python clippingparser.py clippings.txt sample.pdf
        #okular sample.pdf

"""
from __future__ import unicode_literals, print_function
from os.path import isfile
from kindleparse import *

# Overwrite existing annotation file
overwrite = False


def usage():
    print(__doc__)
    exit(1)

if __name__ == '__main__':
    from sys import argv

    try:
        progname, clip_file, pdf_file = argv
    except ValueError:
        usage()

    # Filenames are always bytes
    pdf_file = bytes(pdf_file)
    # parse My Clippings.txt
    clippings = parse_clippings(clip_file)
    # search the clippings in your pdf
    paged_clippings = search_clippings_in_book(pdf_file, clippings)
    # generate the xml file
    destfile = mk_destfile(pdf_file)
    if isfile(destfile) and not overwrite:
        raise ValueError("File %r already exists: backup your delete existing copy!" % destfile)
    print("Creating file: ", destfile)
    create_xml_file(destfile, paged_clippings)
