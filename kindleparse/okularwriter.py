from __future__ import unicode_literals, print_function, division
import uuid
from xml.etree.ElementTree import Element, ElementTree
from os.path import basename, join as pjoin, getsize, expanduser
from collections import defaultdict
from pdfparser import CODEC as PDF_CODEC

REVISION_LINE_SEP = b'&#xa;'
OKULAR_HOME = "~/.kde/share/apps/okular/docdata"


def mk_destfile(filepath):
    destdir = expanduser(OKULAR_HOME)
    size = getsize(filepath)
    return pjoin(bytes(destdir),
                 b"{size}.{name}.xml".format(
                     size=size, name=basename(filepath))
                 )


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
        for pos, clip in enumerate(p_clippings):
            annotation = Element('annotation', attrib={'type': '1'})
            safe_but_ugly_text = clip
            try:
                safe_but_ugly_text = safe_but_ugly_text.decode(PDF_CODEC)\
                    .encode('ascii', 'xmlcharrefreplace')\
                    .replace(b"---", b"&#xa;")

            except UnicodeError:
                safe_but_ugly_text = repr(bytes(safe_but_ugly_text))
            base = Element('base', attrib={
                'flags': '4',
                'opacity': '0.8',
                'creationDate': "2015-02-12T14:41:18",
                'uniqueName': "okular-{%s}" % str(uuid.uuid4()),
                'color': "#ffff00",
                'author': "Roberto Polli",
                'contents': safe_but_ugly_text
            })

            top, bottom = .2*(1+pos/3), .2*(1+(pos+1)/3)
            boundary = Element(
                'boundary', attrib=dict(l="0",
                                        r=".3",
                                        t=str(top),
                                        b=str(bottom))
            )
            base.append(boundary)
            annotationList.append(annotation)
            annotation.append(base)
            text_icon = Element('text', attrib=dict(icon="Comment", type="1"))
            annotation.append(text_icon)

    # Write the xml document
    documentInfo.append(pageList)
    xmldoc = ElementTree(element=documentInfo)
    xmldoc.write(bytes(filepath), xml_declaration=True, encoding="UTF-8")
