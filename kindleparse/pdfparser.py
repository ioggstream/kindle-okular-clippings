#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    Parse a PDF file to a list of text
"""


from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import TextConverter
from pdfminer.cmapdb import CMapDB
from pdfminer.layout import LAParams
from StringIO import StringIO

codec = 'utf-8'
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
        device = TextConverter(rsrcmgr, outfp, codec=codec, laparams=laparams,
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

