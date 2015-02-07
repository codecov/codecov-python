import re

IGNORE = re.compile(r"^\/home\/travis\/virtualenv\/python")

def from_xml(xml):
    coverage, branches = {}, {}
    for _class in xml.getiterator('class'):
        # extract file name
        filename = _class.attrib['filename']
        
        if IGNORE.match(filename):
            continue
        
        lines = []
        append = lines.append
        for line in _class.getiterator('line'):
            l = line.attrib
            cc = str(l.get('condition-coverage', ''))
            append((str(l['number']), cc.split(' ',1)[1][1:-1] if cc else int(l.get('hits', 0) or 0)))
        
        if not lines:
            continue

        coverage[filename] = dict(lines)

    return dict(coverage=coverage, branches=branches)
