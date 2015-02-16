#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    Parse a PDF file to a list of text.

    Code inspired by pdf2txt.py

    Uses clippingparser
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
from pyPdf import PdfFileReader
import pdfquery
import re
import clippingparser
from pdfquery.cache import FileCache
CODEC = 'utf-8'
PDF_PAGE_FIELDS = "page_index height width".split(
    )  # get those fields from PDF
re_parens = re.compile(r"[()]")

caching = True
debug = False
PDFDocument.debug = debug
PDFParser.debug = debug
CMapDB.debug = debug
PDFResourceManager.debug = debug
PDFPageInterpreter.debug = debug
PDFDevice.debug = debug


class ClippablePDF():
    def __init__(self, book_file):
        self.book_file = book_file
        self.pdf_query = pdfquery.PDFQuery(book_file
                                           #                                   , parse_tree_cacher=FileCache("/tmp/")
                                           )
        self.pdf_query.load(None)
        with open(book_file, 'rb') as fh:
            pdf = PdfFileReader(fh)
            self.num_pages = pdf.getNumPages()

    def get_title(self):
        """
        Get the book title from a pdf file
        :param book_file:
        :return:
        """
        return self.pdf_query.doc.info[0].get('Title')

    def pdf_to_text(self, maxpages=0):
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
        with file(self.book_file, 'rb') as fp:
            # Create a TextConverter device writing out to our buffer
            device = TextConverter(
                rsrcmgr, outfp, codec=CODEC, laparams=laparams,
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

    def get_clipping_position(self, clip):
        """
        Get the clipping position in a file, that is (page_index, rectangle)
        where rectangle is a 4-ple of points
        :param clip:
        :param pdf_query: a PDFQuery object
        :return: a 2-tuple of (page_index, 4-tuple coordinates)
        """

        # cleanup the clip before searching
        clip = re_parens.sub("",  clip[:10])
        q = ':contains("' + clip.decode(CODEC) + '")'
        labels = self.pdf_query.pq(q)
        # Labels is made of
        # [ <page>, ..., <LTTextLineHorizontal> ]
        # so we get page infos and find the right text object
        if not labels:
            return
        # Beware of PDFQuery.pageid as it varies after subsequent calls
        #  of PDFQuery.load
        page_index, height, width = (
            float(labels[1].attrib[x]) for x in PDF_PAGE_FIELDS)

        for label in labels:
            # Find and element which
            if not hasattr(label, 'layout'):
                continue
            l = label.layout
            if isinstance(l, LTTextLineHorizontal):
                # Coordinates are relative to the page size and
                # y-cordinates are reversed respect to PDF format
                return int(page_index), (float(l.x0)/width,
                                         (height-float(l.y0))/height,
                                         float(l.x1)/width,
                                         (height - float(l.y1))/height)

    def search_clippings_in_book(self, clippings, limit_page=None, limit_clips=None):
        """
        Wrapper around the testable search_clippings_in_text
        :param book_file:
        :param clippings:
        :param limit_page:
        :param limit_clips:
        :return:
        """
        book_title = self.get_title()
        title, book_clippings = clippingparser.find_clippings(
            book_title, clippings)
        if not title:
            raise ValueError("Clippings not found for %r" % self.book_file)
        # Force evaluation of the generator...maybe there's a
        # better way to implement the following algorithm
        text_pages = list(self.pdf_to_text())
        return clippingparser.search_clippings_in_text(book_clippings, text_pages)
