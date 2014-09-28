import re

# Add xrange variable to Python 3
try:
    xrange
except NameError:
    xrange = range

def from_txt(report, path=None):
    """
    mode: count
    github.com/codecov/sample_go/sample_go.go:7.14,9.2 1 1
    github.com/codecov/sample_go/sample_go.go:11.26,13.2 1 1
    github.com/codecov/sample_go/sample_go.go:15.19,17.2 1 0
    """
    pattern = re.compile(r"(?P<name>[^\:]+)\:(?P<start>\d+)\.\d+\,(?P<end>\d+)\.\d+\s\d+\s(?P<hits>\d+)")
    fill = lambda l,x: l.extend([None]*(x-len(l)))
    files = dict()
    for line in report.split('\n')[1:]:
        result = pattern.search(line)
        if result:
            data = result.groupdict()
            fill(files.setdefault(data['name'], []), int(data['end'])+1)
            for x in xrange(int(data['start']), int(data['end'])+1):
                files[data['name']][x] = int(data['hits'])
    return dict(coverage=files, meta=dict(report="go.txt"))
