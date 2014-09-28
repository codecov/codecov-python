def from_xml(xml, path=None):
    coverage, branches = {}, {}
    package = xml.getElementsByTagName('coverage')[0]
    coverage.update(dict(map(_line, package.getElementsByTagName('class'))))
    branches.update(dict(map(_branch, package.getElementsByTagName('class'))))

    return dict(coverage=coverage, 
                stats=dict(branches=branches), 
                meta=dict(report="cobertura.xml"))

def _line(_class):
    """
    Lines Covered
    =============

    <class branch-rate="0" complexity="0" filename="file.py" line-rate="1" name="module">
        <methods/>
        <lines>
            <line hits="1" number="1"/>
            <line branch="true" condition-coverage="100% (2/2)" hits="1" number="2"/>
            <line branch="true" condition-coverage="500% (1/2)" hits="1" number="3"/>
            <line hits="0" number="4"/>
        </lines>
    </class>

    {
        "file.py": [None, 1, True, 0]
    }
    """
    # available: branch
    _lines = _class.getElementsByTagName('line')
    if not _lines:
        return _class.getAttribute('filename'), []

    lines = [None]*(max([int(line.getAttribute('number')) for line in  _lines])+1)
    for line in _lines:
        cc = str(line.getAttribute('condition-coverage'))
        lines[int(line.getAttribute('number'))] = True if cc and '100%' not in cc else int(line.getAttribute('hits') or 0)

    return _class.getAttribute('filename'), lines


def _branch(_class):
    """
    How many branches found
    =======================

    <class branch-rate="0" complexity="0" filename="file.py" line-rate="1" name="module">
        <methods/>
        <lines>
            <line hits="1" number="1"/>
            <line branch="true" condition-coverage="100% (2/2)" hits="1" number="2"/>
            <line branch="true" condition-coverage="500% (1/2)" hits="1" number="3"/>
            <line hits="0" number="4"/>
        </lines>
    </class>

    {
        "file.py": 2
    }
    """
    return _class.getAttribute('filename'), sum(map(lambda l: int(l.getAttribute('condition-coverage').split('/')[1][:-1]), 
                                                    filter(lambda l: l.getAttribute('branch')=='true', 
                                                           _class.getElementsByTagName('line'))))
