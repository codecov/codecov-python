import re

IGNORE = re.compile(r'^((vendor/)|(\$\{))')

def from_xml(xml):
    coverage = {}
    for f in xml.getiterator('file'):
        filename = f.attrib['name']
        if IGNORE.match(filename):
            continue
        elif f.find('line') is None:
            continue

        lines = dict([(str(line.attrib['num']), int(line.attrib['count'] or 0)) for line in f.getiterator('line')])

        if not lines:
            continue

        coverage[filename] = dict(lines)

    return dict(coverage=coverage)

