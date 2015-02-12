#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    Convert Kindle My Clippings.txt to an Okular Review File.

    Okular Review files are in OKULAR_HOME: their name is
    7252866.{filename.ext}.xml

    Usage:

        python kindleparse.py clippings.txt High_Performance_Python.pdf

"""
from __future__ import unicode_literals, print_function
from collections import defaultdict
import uuid
from xml.etree.ElementTree import Element, ElementTree, tostring, parse
from pyPdf import PdfFileReader

OKULAR_HOME = "~/.kde/share/apps/okular/docdata"


def usage():
    print(__doc__)
    exit(1)


def cleanup_for_match(s):
    return s.strip().lower()


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


def get_book_title_from_clippings(pdf_object, clippings):
    for k in clippings:
        if bytes(pdf_object.documentInfo['/Title']) in k:
            return k


#@loggable
def create_xml_file(filepath, paged_clippings):
    """
        Create an xml file containing the clippings
        @param filepath - filename.xml
        @param paged_clippings - an iterable of couples,
            eg [ (1, 'here comes the sun'),
                (2, 'nananana'),
                (2, 'all right'), ..]
    """
    assert filepath.endswith(".xml")
    paged_clippings_dict = defaultdict(list)
    for p, c in paged_clippings:
        paged_clippings_dict[p].append(c)

    documentInfo = Element('documentInfo', attrib={'url': filepath})
    pageList = Element('pageList')

    for p_num, p_clippings in paged_clippings_dict.items():
        print(p_clippings)
        page = Element('page', attrib={'number': str(p_num)})
        pageList.append(page)
        annotationList = Element('annotationList')
        page.append(annotationList)
        #for clip in p_clippings:
        annotation = Element('annotation', attrib={'type': '1'})
        safe_but_ugly_text = repr(b'\n'.join(p_clippings))
        base = Element('base', attrib={
            'flags': '4',
            'creationDate': "2015-02-12T14:41:18",
            'uniqueName': "okular-{%s}" % str(uuid.uuid4()),
            'color': "#ffff00",
            'author': "Roberto Polli",
            'contents': safe_but_ugly_text
        })

        boundary = Element(
            'boundary', attrib=dict(l="0", r=".3", b=".3", t=".2"))
        base.append(boundary)
        annotationList.append(annotation)
        annotation.append(base)
        text_icon = Element('text', attrib=dict(icon="Comment", type="1"))
        annotation.append(text_icon)
        #  break
    # Write the xml document
    documentInfo.append(pageList)
    xmldoc = ElementTree(element=documentInfo)
    xmldoc.write(bytes(filepath), xml_declaration=True, encoding="UTF-8")


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
        title = get_book_title_from_clippings(pdf, clippings)
        book_clippings = clippings[title]
        #print("Looking for %r clippings" % len(book_clippings))
        #print(b"Clippings: %s" % b'\n\n'.join(book_clippings))
        n, p = 0, 0
        limit_page = limit_page if limit_page else pdf.numPages
        limit_clips = limit_clips if limit_clips else len(book_clippings)
        while n < limit_clips:
            for i in range(p, limit_page):
                if n > limit_clips:
                    break

                content = pdf.pages[i].extractText()
                if content:
                    bc = book_clippings[n]
                    if find_clipping_in_page(bc, content):
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


if __name__ == '__main__':
    from sys import argv
    from os.path import basename, dirname, join as pjoin
    try:
        progname, clip_file, pdf_file = argv
    except ValueError:
        usage()

    pdf_file = bytes(pdf_file)
    # parse My Clippings.txt
    clippings = parse_clippings(clip_file)
    # search the clippings in your pdf
    paged_clippings = search_clippings_in_book(pdf_file, clippings,
                                               limit_page=50,
                                               limit_clips=50)
    # generate the xml file
    destfile = pjoin(dirname(pdf_file), b"123456.%s.xml" % basename(pdf_file))
    create_xml_file(destfile, paged_clippings)
