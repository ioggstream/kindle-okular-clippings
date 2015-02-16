"""
    Dependency chain:
        okularwriter -> pdfparser -> clippingparser
"""
__author__ = 'rpolli'
__all__ = [
    "ClippablePDF", "parse_clippings", "OKULAR_HOME",
    "create_xml_file", "mk_destfile", "search_clippings_in_book", "find_clippings"
    "create_xml_file_hl2"

]
from clippablepdf import ClippablePDF, CODEC
from okularwriter import OKULAR_HOME, mk_destfile, create_xml_file, create_xml_file_hl
from clippingparser import parse_clippings, find_clippings
