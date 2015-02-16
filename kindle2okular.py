#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    Convert Kindle My Clippings.txt to an Okular Review File.

    Okular Review files are generated in:
     # OKULAR_HOME/{filesize}.{filename.ext}.xml

"""
from __future__ import unicode_literals, print_function
from os.path import isfile
import kindleparse
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", '--force', dest="force", default=False, action='store_const', const=True, help="overwrite existing annotation file")
    parser.add_argument("-I", "--inline",  dest="inline", default=False, action='store_const', const=True, help="show clippings as inline note instead of highlight")
    parser.add_argument("-c", "--clippings", dest="clip_file",
                        type=str, help="clippings file")
    parser.add_argument("pdf_file", metavar="book.pdf", type=str,
                        nargs=1, help="PDF book to parse")
    args = parser.parse_args()
    overwrite = args.force

    # Filenames are always bytes
    pdf_file = bytes(args.pdf_file[0])
    clip_file = bytes(args.clip_file)
    # parse My Clippings.txt
    clippings = kindleparse.parse_clippings(clip_file)

    # generate the xml file
    destfile = kindleparse.mk_destfile(pdf_file)
    if isfile(destfile) and not overwrite:
        raise ValueError("File %r already exists: backup your delete existing copy!" % destfile)

    pdf = kindleparse.ClippablePDF(pdf_file)
    if args.inline:
        # search the clippings in your pdf
        paged_clippings = pdf.search_clippings_in_book(clippings)
        print("Creating file: ", destfile)
        kindleparse.okularwriter.create_xml_file(destfile, paged_clippings)
    else:
        book_title = pdf.get_title()
        assert book_title, "Missing book title"
        amazon_title, book_clippings = kindleparse.find_clippings(
            book_title, clippings)

        print("Creating file: ", destfile)
        kindleparse.okularwriter.create_xml_file_hl2(
            destfile, book_clippings, pdf)
