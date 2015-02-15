#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
from xml.etree.ElementTree import tostring, parse

from pyPdf import PdfFileReader
from nose.tools import assert_equal, assert_in, assert_true

from kindleparse import pdf_to_text, CODEC as pdf_parser_codec, parse_clippings
from kindleparse import clippingparser
from kindleparse.okularwriter import mk_destfile, create_xml_file


clippings_file = "clippings.txt"
book_file = "sample.pdf"
amazon_title = 'High Performance MySQL, Third Edition (Baron Schwartz)'


def test_parse_clippings():
    clippings = parse_clippings(clippings_file)
    assert len(clippings) == 3


def test_get_clippings_title_for_book():
    clippings = clippingparser.parse_clippings(clippings_file)
    pdf = PdfFileReader(open(book_file, 'rb'))
    title = clippingparser.get_amazon_title(pdf, clippings)
    assert_equal(amazon_title, title)


def test_print_file():
    pdf_file = PdfFileReader(open(book_file, 'rb'))
    for p in pdf_file.pages:
        tt = p.extractText()
        if tt:
            print(tt)


def test_create_fake_okular_xml():
    f = "fake1.xml"
    create_xml_file(f, paged_clippings=zip(range(5), "abcder"))
    xml = parse(f)
    assert xml
    print(tostring(xml.getroot()))


def test_create_fake_okular_xml_2():
    f = "fake2.xml"
    create_xml_file(f, paged_clippings=zip(range(1), "a"))
    xml = parse(f)
    assert xml
    print(tostring(xml.getroot()))


def test_create_sample_okular_xml():

    destfile = mk_destfile(book_file)
    clippings = clippingparser.parse_clippings(clippings_file)
    paged_clippings = clippingparser.search_clippings_in_book(
        book_file, clippings, limit_page=20, limit_clips=10)
    create_xml_file(destfile, paged_clippings=list(paged_clippings))


def test_pdf_extract():
    expected_clip_in_page = [
        (1, 'You can buy this book at oreilly.com'),
        (18,  's troublesome. There’s nothing wrong with multiple')
    ]
    pages = list(pdf_to_text(book_file))
    for page, needle in expected_clip_in_page:
        # book pages starts at 1, while list items at 0
        item_no = page - 1
        yield assert_in, needle, pages[item_no].decode(pdf_parser_codec)


def test_find_clipping_in_page():
    expected_clip_in_page = [
        (1, 'You can buy this book at oreilly.com'),
        (18,  's troublesome. There’s nothing wrong with multiple'),
        (19, ("The locking style that offers the greatest concurrency "
              "(and carries the greatest overhead) is the use of row locks."
              " Row-level locking, as this strategy is commonly known, is")),
        (18, ("follows. Read locks on a resource are shared, or mutually nonblocking: many clients "
              "can read from a resource at the same time and not interfere with each other. Write "
              "locks, on the other hand, are exclusive—i.e., they block both read locks and other write"))
    ]

    pages = list(pdf_to_text(book_file))
    for page, needle in expected_clip_in_page:
        # book pages starts at 1, while list items at 0
        item_no = page - 1
        success = clippingparser.find_clipping_in_page(needle, pages[item_no])
        yield assert_true, success, (needle, pages[item_no])


def test_search_clipping_in_book():
    from kindleparse import pdfparser

    expected_clip_in_page = [
        (1, 'You can buy this book at oreilly.com'),
        (18,  's troublesome. There’s nothing wrong with multiple'),
        (18, ("follows. Read locks on a resource are shared, or mutually nonblocking: many clients "
              "can read from a resource at the same time and not interfere with each other. Write "
              "locks, on the other hand, are exclusive—i.e., they block both read locks and other write")),
        (19, ("The locking style that offers the greatest concurrency "
              "(and carries the greatest overhead) is the use of row locks."
              " Row-level locking, as this strategy is commonly known, is")),

    ]
    pgnos, clippings = zip(*expected_clip_in_page)
    pgnos = list(pgnos)
    pages = list(pdfparser.pdf_to_text(book_file))
    for ep, ec in clippingparser.search_clippings_in_text(clippings, pages):
        yield assert_equal, ep+1, pgnos.pop(0)
