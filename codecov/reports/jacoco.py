import os
from xml.dom.minidom import parseString

def from_xml(xml, path=None):
    """
    nr = line number
    mi = missed instructions
    ci = covered instructions
    mb = missed branches
    cb = covered branches
    """
    # read pom.xml for sourceDirectory and append to file name
    if path:
        with open(os.path.join(path, 'pom.xml'), 'r') as pom:
            src = parseString(pom.read()).getElementsByTagName("sourceDirectory")[0].lastChild.nodeValue + "/"
    else:
        src = ""

    coverage, stats = {}, {"branches":{},"methods":{},"classes":{},"instructions":{}}
    for package in xml.getElementsByTagName('package'):
        for sourcefile in package.getElementsByTagName('sourcefile'):
            file_name = "%s%s/%s" % (src, package.getAttribute('name'), sourcefile.getAttribute('name'))
            lines = [(int(f.getAttribute('nr')), True if f.getAttribute('cb')!='0' else int(f.getAttribute('ci'))) for f in sourcefile.getElementsByTagName('line')]
            coverage[file_name] = [None] * (max(map(lambda a: a[0], lines))+1)
            for line in lines:
                coverage[file_name][line[0]] = line[1]
            for c in sourcefile.getElementsByTagName('counter'):
                typ = dict(INSTRUCTION="instructions",BRANCH="branches",METHOD="methods",CLASS="classes").get(c.getAttribute('type'))
                if typ:
                    stats[typ][file_name] = int(c.getAttribute('missed')) + int(c.getAttribute('covered'))
    return dict(coverage=coverage, 
                stats=stats,
                meta=dict(report="jacoco.xml"))
