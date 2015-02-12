#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
from pyPdf import PdfFileReader
from xml.etree.ElementTree import tostring, parse
from kindleparse import parse_clippings, get_book_title_from_clippings
clippings_file = "clippings.txt"
book_file = "High_Performance_Python.pdf"


def test_parse_clippings():
    clippings = parse_clippings(clippings_file)
    assert len(clippings) > 10


def test_get_clippings_title_for_book():
    clippings = parse_clippings(clippings_file)
    pdf = PdfFileReader(open(book_file, 'rb'))
    title = get_book_title_from_clippings(pdf, clippings)
    assert 'High Performance Python (Micha Gorelick and Ian Ozsvald)' == title


def test_find_clipping_in_page():
    from kindleparse import find_clipping_in_page
    clip = 'this book is primarily aimed at people with a cpu-bound problem,'
    pdf = PdfFileReader(open(book_file, 'rb'))
    content = pdf.pages[9].extractText()
    assert find_clipping_in_page(clip, content)


def test_create_fake_okular_xml():
    f = "fake1.xml"
    from kindleparse import create_xml_file
    create_xml_file(f, paged_clippings=zip(range(5), "abcder"))
    xml = parse(f)
    assert xml
    print(tostring(xml.getroot()))


def test_create_fake_okular_xml_2():
    f = "fake2.xml"
    from kindleparse import create_xml_file
    create_xml_file(f, paged_clippings=zip(range(1), "a"))
    xml = parse(f)
    assert xml
    print(tostring(xml.getroot()))


def test_create_sample_okular_xml():
    from kindleparse import parse_clippings, search_clippings_in_book, create_xml_file
    clippings = parse_clippings(clippings_file)
    paged_clippings = search_clippings_in_book(
        book_file, clippings, limit_page=20, limit_clips=10)
    create_xml_file("foo2.xml", paged_clippings=list(paged_clippings))
