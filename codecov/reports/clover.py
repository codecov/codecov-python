def from_xml(xml, path=None):
    coverage = {}
    for f in xml.getElementsByTagName('coverage')[0].getElementsByTagName('file'):
        _lines = f.getElementsByTagName('line')
        if not _lines:
            return f.getAttribute('file'), []

        lines = [None]*(max([int(line.getAttribute('num')) for line in  _lines])+1)
        for line in _lines:
            lines[int(line.getAttribute('num'))] = int(line.getAttribute('count') or 0)

        coverage[f.getAttribute('name')] = lines

    return dict(coverage=coverage, meta=dict(report="clover.xml"))
