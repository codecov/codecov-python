import re

IGNORE = re.compile(r"^\/home\/travis\/virtualenv\/python")


def from_xml(xml):
    coverage, branches = {}, {}
    for _class in xml.getiterator('class'):
        # extract file name
        filename = _class.attrib['filename']
        if IGNORE.match(filename):
            # ignore this all together
            continue

        lines = [None]*(max([int(line.attrib['number']) for line in _class.getiterator('line')] or [0])+1)
        if len(lines) == 1:
            continue

        for line in _class.getiterator('line'):
            cc = str(line.attrib.get('condition-coverage', ''))
            lines[int(line.attrib['number'])] = cc.split(' ',1)[1][1:-1] if cc else int(line.attrib.get('hits', 0) or 0)
        coverage[filename] = lines

    return dict(coverage=coverage, branches=branches)
