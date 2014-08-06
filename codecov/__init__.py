import os
import sys
import commands
import requests
import argparse
from json import dumps
from xml.dom.minidom import parseString

version = VERSION = __version__ = '0.0.2'


def generate_report(path):
    try:
        with open(path, 'r') as f:
            return generate_json(f.read())
    except:
        try:
            commands.getstatusoutput('coverage xml')
        except:
            return None
        else:
            with open(path, 'r') as f:
                return generate_json(f.read())

def generate_json(xml):
    coverage = parseString(xml).getElementsByTagName('coverage')[0]
    for package in coverage.getElementsByTagName('package'):
        if package.getAttribute('name') == '':
            files = dict([clazz(_class) for _class in coverage.getElementsByTagName('class')])
            branches = sum(map(lambda f: f['b'], files.values()))
            run = sum(map(lambda f: f['r'], files.values()))
            missing = sum(map(lambda f: f['m'], files.values()))
            excluded = 0 # not sure how to get this value
            partial = sum(map(lambda f: f['p'], files.values()))
            return {
                "branch-rate": coverage.getAttribute('branch-rate'),
                "timestamp": coverage.getAttribute('timestamp'),
                "version": coverage.getAttribute('version'),
                "line-rate": coverage.getAttribute('line-rate'),
                "totals": {
                    "b": branches,
                    "r": run,
                    "m": missing,
                    "e": excluded,
                    "p": partial,
                    "s": sum([run, missing, partial]),
                    "cov": ("%d" % int(round(float(run)/float(run+missing+partial)*100))) if run else "0"
                },
                "files": files
            }

def clazz(_class):
    # available: branch
    lines = map(lambda line: dict([(attr[0], line.getAttribute(attr)) for attr in ('number', 'condition-coverage', 'hits')]), 
                _class.getElementsByTagName('line'))
    run = sum([1 for line in lines if int(line['h']) > 0])
    missing = sum([1 for line in lines if int(line['h']) == 0])
    excluded = 0 # not sure how to get this value
    partial = sum([1 for line in lines if line['c']])
    branches = sum([int(line['c'].split('/')[-1][:-1]) for line in lines if line['c']])

    return _class.getAttribute('filename'), {
        "br": _class.getAttribute('branch-rate'),
        "c": _class.getAttribute('complexity'),
        "f": _class.getAttribute('filename'),
        "b": branches,
        "r": run,
        "m": missing,
        "e": excluded,
        "p": partial,
        "s": sum([run, missing, partial]),
        "cov": ("%d" % int(round(float(run)/float(run+missing+partial)*100))) if run else "0",
        "lr": _class.getAttribute('line-rate'),
        # "name": _class.getAttribute('name'),
        "lines": lines}


def main():
    if os.getenv('CI') == "TRUE" and os.getenv('TRAVIS') == "TRUE":
        # http://docs.travis-ci.com/user/ci-environment/#Environment-variables
        codecov = dict(owner=[os.getenv('TRAVIS_REPO_SLUG').split('/')[0]],
                       repo=[os.getenv('TRAVIS_REPO_SLUG').split('/')[1]],
                       xml=os.path.join(os.getenv('TRAVIS_BUILD_DIR'), "coverage.xml"),
                       commit=[os.getenv('TRAVIS_COMMIT')])

    else:
        parser = argparse.ArgumentParser(prog='codecov', add_help=True,
                                         formatter_class=argparse.RawDescriptionHelpFormatter,
                                         epilog="""Example: \033[90mcodecov stevepeak timestring 817vnp1\033[0m
    Read more at \033[95mhttps://codecov.io/\033[0m""")
        parser.add_argument('--version', action='version', version='codecov '+version+" - https://codecov.io")
        parser.add_argument('owner', nargs=1, help="repo owner name")
        parser.add_argument('repo', nargs=1, help="repo name")
        parser.add_argument('commit', nargs=1, help="commit ref")
        parser.add_argument('--token', '-t', default=os.getenv("CODECOV_TOKEN"), required=True, help="codecov repository token")
        parser.add_argument('--xml', '-x', default="coverage.xml", help="coverage xml report relative path")
        parser.add_argument('--url', default="https://codecov.io", help="url, used for debugging")
        codecov = parser.parse_args()

    try:
        coverage = generate_report(codecov.xml)
        if not coverage:
            sys.stdout.write("\033[95mWARNING\033[0m: no coverage.xml report found, could not upload to codecov\n")
    except:
        sys.stdout.write("\033[95mERROR\033[0m: failed to process report for codecov\n")
        raise

    else:
        url = "%s/%s/%s?commit=%s&version=%s&token=%s" % (codecov.url, codecov.owner[0], codecov.repo[0], codecov.commit[0], version, codecov.token)
        result = requests.post(url, headers={"Accept": "application/json"}, data=dumps(coverage))
        if result.status_code == 200:
            sys.stdout.write("codecov coverage uploaded successfuly to \033[95m%s/%s/%s?ref=%s\033[0m\n" % (codecov.url, codecov.owner[0], codecov.repo[0], codecov.commit[0]))
        else:
            sys.stdout.write(result.text+"\n")


if __name__ == '__main__':
    main()
