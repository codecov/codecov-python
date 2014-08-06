import os
import sys
import requests
import argparse

version = VERSION = __version__ = '0.0.1'

def main():
    parser = argparse.ArgumentParser(prog='codecov', add_help=True,
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog="""Example: \033[90mcodecov stevepeak timestring 817vnp1\033[0m
Read more at \033[95mhttps://codecov.io/\033[0m""")

    if os.getenv('CI') == "TRUE" and os.getenv('TRAVIS') == "TRUE":
        # http://docs.travis-ci.com/user/ci-environment/#Environment-variables
        codecov = dict(owner=[os.getenv('TRAVIS_REPO_SLUG').split('/')[0]],
                       repo=[os.getenv('TRAVIS_REPO_SLUG').split('/')[1]],
                       xml=os.path.join(os.getenv('TRAVIS_BUILD_DIR'), "coverage.xml"),
                       commit=[os.getenv('TRAVIS_COMMIT')])
    else:

        parser.add_argument('--version', action='version', version='codecov '+version+" - https://codecov.io")
        parser.add_argument('owner', nargs=1, help="repo owner name")
        parser.add_argument('repo', nargs=1, help="repo name")
        parser.add_argument('commit', nargs=1, help="commit ref")
        parser.add_argument('--token', '-t', default=os.getenv("CODECOV_TOKEN"), required=True, help="codecov repository token")
        parser.add_argument('--xml', '-x', default="coverage.xml", help="coverage xml report relative path")
        codecov = parser.parse_args()

    try:
        with open(os.path.join(os.path.dirname(__file__), codecov.xml), 'r') as f:
            coverage = f.read()
    except:
        sys.stdout.write("\033[95mWARNING\033[0m: no coverage.xml report found, could not upload to codecov\n")

    else:
        url = "https://codecov.io/%s/%s?commit=%s&token=%s" % (codecov.owner[0], codecov.repo[0], codecov.commit[0], codecov.token)
        result = requests.post(url, headers={"Accept": "application/xml"}, data=coverage)
        if result.status_code == 200:
            sys.stdout.write("codecov coverage uploaded successfuly.%s\n" % url)
        else:
            sys.stdout.write(result.text+"\n")

if __name__ == '__main__':
    main()
