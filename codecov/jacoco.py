import re

LINE = re.compile(r'(\<line(?:\s[a-z]{2}\=\"\d+\")+\s?\/\>)', re.M)


def Parts(p):
    return tuple(p.replace('"','').split('=',1))


def Line(line):
    try:
        line = dict(map(Parts, line[6:-2].strip().split(' ')))
    except ValueError:
        return (0,None)
    else:
        if (line['mb'], line['cb']) != ("0", "0"):
            return int(line['nr']), ("%s/%d" % (line['cb'], int(line['mb'])+int(line['cb'])))
        else:
            return int(line['nr']), (int(line['ci']) if line['ci']!='0' else 0)


def from_xml(report):
    """
    nr = line number
    mi = missed instructions
    ci = covered instructions
    mb = missed branches
    cb = covered branches
    """
    coverage = {}
    for package in report.split('<package name="')[1:]:
        base_name = package.split('"', 1)[0]
        for source in package.split('<sourcefile name="')[1:]:
            file_name = "%s/%s" % (base_name, source.split('"', 1)[0])

            # -----
            # Lines
            # -----
            lns = map(Line, LINE.findall(source))
            lines = [None]*(max(lns, key=lambda a: a[0])[0]+1)
            for ln, x in lns: lines[ln] = x
            if not lines: continue
            coverage[file_name] = lines

    return dict(coverage=coverage)
