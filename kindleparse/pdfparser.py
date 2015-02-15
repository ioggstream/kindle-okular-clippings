#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    Parse a PDF file to a list of text.

    Code inspired by pdf2txt.py
"""

from pdfminer.layout import LTTextLineHorizontal
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import TextConverter
from pdfminer.cmapdb import CMapDB
from pdfminer.layout import LAParams
from StringIO import StringIO
import re
CODEC = 'utf-8'
caching = True
debug = False
PDFDocument.debug = debug
PDFParser.debug = debug
CMapDB.debug = debug
PDFResourceManager.debug = debug
PDFPageInterpreter.debug = debug
PDFDevice.debug = debug


def pdf_to_text(book_file, maxpages=0):
    """
    Return a generator list of text pages of a given file.

    :param book_file:
    :param maxpage: limit the pages to convert
    :return: a generator with the text content of the pages
    """
    outfp = StringIO()
    imagewriter = None
    laparams = LAParams()

    rsrcmgr = PDFResourceManager(caching=caching)
    with file(book_file, 'rb') as fp:
        # Create a TextConverter device writing out to our buffer
        device = TextConverter(rsrcmgr, outfp, codec=CODEC, laparams=laparams,
                               imagewriter=imagewriter)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        # Parse the pdf file, retrieving only the matching pages
        pages = PDFPage.get_pages(fp, maxpages=maxpages,
                                  caching=caching,
                                  check_extractable=True)
        for p in pages:
            interpreter.process_page(p)
            yield outfp.getvalue()
            outfp.truncate(0)

def get_clipping_position(clip, pdf_query):
    """
    Get the clipping position in a file, that is (pageid, location-4ple)
    :param clip:
    :param pdf_query: a PDFQuery object
    :return: a 2-tuple of (pageid, 4-tuple coordinates)
    """
    # cleanup the clip before searching
    clip = re.sub(r"[()]", "",  clip[:10])
    labels = pdf_query.pq(':contains("%s")' % clip)
    pageid, height, width = (float(labels[1].attrib[x]) for x in "pageid height width".split())

    for label in labels:
        if not hasattr(label, 'layout'):
            continue
        l = label.layout
        if isinstance(l, LTTextLineHorizontal):
            return int(pageid), (float(l.x0)/width, (height-float(l.y0))/height, float(l.x1)/width, (height - float(l.y1))/height)
