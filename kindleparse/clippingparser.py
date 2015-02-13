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
from collections import defaultdict

from pyPdf import PdfFileReader
import re
import pdfparser


re_spaces = re.compile("\s+")



def cleanup_for_match(s):
    if not isinstance(s, unicode):
        s = s.decode(pdfparser.codec)

    return re_spaces.sub(" ", s.strip().lower())


def loggable(wrapped_f):
    def tmp(*args, **k):
        print(wrapped_f.__name__, args, k)
        return wrapped_f(*args, **k)

    return tmp


def parse_clippings(clippings_path):
    """
    Parse a Kindle My Clippings.txt file.
    :param clippings_path: path to file
    :return: a dict of the form {'book title': ['clip1', 'clip2', ...]}

    TODO: sort clippings by position

    The content is of the following form:
    SEPARATOR
    TITLE (AUTHORS)
    - POSITION | TIMESTAMP

    COMMENT
    SEPARATOR

    eg.
    ==========
    Twisted Network Programming Essentials (Jessica McKellar and Abe Fettig)
    -  La tua evidenziazione alla posizione 461-461 | Aggiunto in data giovedì 17 aprile 2014 12:11:32

    characterized by an event loop and the use of callbacks to trigger actions when events happen.
    ==========
    """
    clippings = defaultdict(list)
    book_sep, field_sep = b'==========\r\n', b'\r\n'
    with open(clippings_path, 'rb') as fh:
        # read file, split and cleanup the entries
        entries = fh.read().split(book_sep)
        entries = (e for e in entries if e)
        # parse the entries into a dict
        for e in entries:
            try:
                title, notes, _, text = e.split(field_sep, 3)
                clippings[title].append(text.strip())
            except ValueError as ex:
                print("error with %r" % [e, ex])
                raise
    return clippings


def get_amazon_title(pdf_object, clippings):
    """
    Return the title used by kindle clippings for a given book
    :param pdf_object:
    :param clippings: a dict of all your clippings
    :return: a book title usable as a key for the clippings
    """
    for k in clippings:
        if bytes(pdf_object.documentInfo['/Title']) in k:
            return k



# @loggable
def find_clipping_in_page(clip_text, page_content):
    """

    :param clip_text:
    :param page_content:
    :return: True if the clip is in content
    """
    if not (page_content and clip_text):
        return False
    needle, haystack = map(cleanup_for_match, (clip_text, page_content))
    if not (needle and haystack):
        return False
    try:
        found = needle[:15] in haystack
    except (UnicodeDecodeError, UnicodeEncodeError) as e:
        print(e, needle, haystack)
        found = False
    return found


def search_clippings_in_book(book_file, clippings, limit_page=None, limit_clips=None):
    """ yields a generator of [ (page, "clip"), ... ]
    """

    with open(book_file, 'rb') as fh:
        pdf = PdfFileReader(fh)
        title = get_amazon_title(pdf, clippings)
        if not title:
            raise ValueError("Clippings not found for %r" % book_file)
        book_clippings = clippings[title]
        # Force evaluation of the generator...maybe there's a
        # better way to implement the following algorithm
        text_pages = list(pdfparser.pdf_to_text(book_file))

        n, p = 0, 0
        mmin = lambda x, A: min(x, len(A)) if x else len(A)
        limit_page = mmin(limit_page, text_pages)
        limit_clips = mmin(limit_clips, book_clippings)
        #
        # This algorithm is sloppy but works around the case
        # of unmatching clippings.
        # If I can't find a clip, I have to rewind to the last
        # matching page
        while n < limit_clips:
            for i in xrange(p, limit_page):
                if n >= limit_clips:
                    break
                bc = book_clippings[n]
                content = text_pages[i]
                if content and find_clipping_in_page(bc, content):
                    # clip found at the given page:
                    # - go to the next clip
                    # - start from this page
                    print("Note found, %r" % [i, bc])
                    yield i, bc
                    n += 1
                    p = i
            else:
                print("Note not found: %r" % [n, p, bc])
                n += 1




