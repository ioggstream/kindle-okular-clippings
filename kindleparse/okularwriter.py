from __future__ import unicode_literals, print_function, division
import uuid
from xml.etree.ElementTree import Element, ElementTree
from os.path import basename, join as pjoin, getsize, expanduser
from collections import defaultdict
from pdfparser import CODEC as PDF_CODEC, get_clipping_position

REVISION_LINE_SEP = b'&#xa;'
OKULAR_HOME = "~/.kde/share/apps/okular/docdata"


def mk_destfile(filepath):
    destdir = expanduser(OKULAR_HOME)
    size = getsize(filepath)
    return pjoin(bytes(destdir),
                 b"{size}.{name}.xml".format(
                     size=size, name=basename(filepath))
                 )





class BaseNote(Element):
    def __init__(self, **kwds):
        attrib = {
                'creationDate': "2015-02-12T14:41:18",
                'uniqueName': "okular-{%s}" % str(uuid.uuid4()),
                'color': "#ffff00",
                'author': "Roberto Polli",
        }
        for k, v in kwds.items():
            if v:
                attrib[k] = str(v)

        Element.__init__(self, 'base', attrib=attrib)


class AnnotationHL(Element):
    def __init__(self):
        Element.__init__(self, 'annotation', attrib={'type': '4'})


class AnnotationIL(Element):
    def __init__(self):
        Element.__init__(self, 'annotation', attrib={'type': '1'})

def create_highlight(points):
    """

    Highlight in Okular overlays is done via set of rectangles.

    A rectangle is made up of the coordinates of 4 points:

       D    C
       A    B


        <annotation type="4">
     <base flags="0" creationDate="2015-02-15T17:02:32"
     uniqueName="okular-{94a0dd72-78dc-4d5e-8aaa-6cb8d6fa4e31}"
      author="Roberto Polli" modifyDate="2015-02-15T17:02:32" color="#ffff00">
      <boundary l="0.143003" r="0.855975" b="0.117601" t="0.0817757"/>
     </base>
     <hl>
      <quad dx="0.208092" cx="0.309827" bx="0.309827" ax="0.208092"
      dy="0.0820106" cy="0.0820106" by="0.0996473" ay="0.0996473"
      feather="1"/>
     </hl>

    :return:
    """
    x0, y0, x1, y1 = map(str, points)
    annotation = AnnotationHL()
    base = BaseNote(flags="0")
    annotation.append(base)
    boundary = Element(
                'boundary', attrib=dict(l="0",
                                        r=".3",
                                        t="0",
                                        b="1")
            )
    base.append(boundary)
    hl = Element('hl')
    hl.append(Element('quad', attrib=dict(
        feather="1",
        ax=x0, ay=y1,
        bx=x1, by=y1,
        cx=x1, cy=y0,
        dx=x0, dy=y0
        )))
    annotation.append(hl)
    return annotation

def create_xml_file_hl(filepath, paged_clippings, pdf_query):
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
        page = Element('page', attrib={'number': str(p_num-1)})
        pageList.append(page)
        annotationList = Element('annotationList')
        page.append(annotationList)
        for pos, clip in enumerate(p_clippings):
            pageid, points = get_clipping_position(clip, pdf_query)
            annotation = create_highlight(points)
            annotationList.append(annotation)
            text_icon = Element('text', attrib=dict(icon="Comment", type="1"))
            annotation.append(text_icon)

    # Write the xml document
    documentInfo.append(pageList)
    xmldoc = ElementTree(element=documentInfo)
    xmldoc.write(bytes(filepath), xml_declaration=True, encoding="UTF-8")



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
            annotation = AnnotationIL()
            safe_but_ugly_text = clip
            try:
                safe_but_ugly_text = safe_but_ugly_text.decode(PDF_CODEC)\
                    .encode('ascii', 'xmlcharrefreplace')\
                    .replace(b"---", b"&#xa;")
            except UnicodeError:
                safe_but_ugly_text = repr(bytes(safe_but_ugly_text))
            base = BaseNote(flags=4, opacity=0.8, text=safe_but_ugly_text)

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
