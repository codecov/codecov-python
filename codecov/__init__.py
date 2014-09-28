#!/usr/bin/python

import os
import sys
import subprocess
import requests
import argparse
from json import dumps
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode
from xml.dom.minidom import parseString

version = VERSION = __version__ = '0.5.0'

# Add xrange variable to Python 3
try:
    xrange
except NameError:
    xrange = range

import reports

def from_file(path, root=None):
    try:
        with open(path, 'r') as f:
            result = to_json(f.read(), root)
            result['meta']['version'] = "codecov-python/v%s"%VERSION
            return result
    except IOError:
        return None

def from_path(path):
    # (python)
    try_to_run('coverage xml')

    accepting = set(('coverage.xml', 'coverage.txt', 'cobertura.xml', 'jacoco.xml'))
    for root, dirs, files in os.walk(path):
        if files and accepting & set(files):
            for f in files:
                if f in accepting:
                    result = from_file(os.path.join(root, f), path)
                    if result:
                        return result

def try_to_run(cmd):
    try:
        subprocess.check_output(cmd, shell=True)
    except:
        pass

def to_json(report, path):
    if report.startswith('mode: count'):
        # (go)
        return reports.go.from_txt(report, path)
    elif report.startswith('<?xml'):
        # xml
        xml = parseString(report)
        coverage = xml.getElementsByTagName('coverage')
        if coverage:
            if coverage[0].getAttribute('generated'):
                # (php) clover
                return reports.clover.from_xml(xml, path)
            else:
                # (python+) cobertura
                return reports.cobertura.from_xml(xml, path)
                
        elif xml.getElementsByTagName('sourcefile'):
            # (java+) jacoco
            return reports.jacoco.from_xml(xml, path)

    # send to https://codecov.io/upload/unknown
    raise ValueError('sorry, unrecognized report') 


def upload(report, url, path=None, **kwargs):
    try:
        args = dict(commit='', branch='', travis_job_id='')
        args.update(kwargs)
        assert args.get('branch') not in ('', None), "branch is required"
        assert args.get('commit') not in ('', None), "commit hash is required"
        assert (args.get('travis_job_id') or args.get('job') or args.get('token')) not in (None, ''), \
               "missing token or other required argument(s)"

        if report is not None:
            coverage = from_file(report, path)
        else:
            coverage = from_path(path)

        assert coverage, "error no coverage report found, could not upload to codecov"

        if kwargs.get('append_path'):
            # in case you do this:
            # cd some_folder && codecov --path=some_folder
            coverage['meta']['path'] = kwargs.pop('append_path')

        if kwargs.get('build_url'):
            coverage['meta']['build_url'] = kwargs.pop('build_url')

        url = "%s/upload/v1?%s" % (url, urlencode(dict([(k, v.strip()) for k, v in kwargs.items() if v is not None])))
        result = requests.post(url, headers={"Content-Type": "application/json"}, data=dumps(coverage))
        result.raise_for_status()
        return result.json()

    except AssertionError as e:
        return dict(message=str(e), uploaded=False, coverage=0)

def main(*argv):
    defaults = dict(commit='', branch='', travis_job_id='', path=os.getcwd() if sys.argv else None, pull_request='', build_url='')

    # -------
    # Jenkins
    # -------
    if os.getenv('JENKINS_URL'):
        # https://wiki.jenkins-ci.org/display/JENKINS/Building+a+software+project
        defaults.update(dict(branch=os.getenv('GIT_BRANCH'),
                             service='jenkins',
                             commit=os.getenv('GIT_COMMIT'),
                             build=os.getenv('BUILD_NUMBER'),
                             path=os.getenv('WORKSPACE'),
                             build_url=os.getenv('BUILD_URL')))
    # ---------
    # Travis CI
    # ---------
    elif os.getenv('CI') == "true" and os.getenv('TRAVIS') == "true":
        # http://docs.travis-ci.com/user/ci-environment/#Environment-variables
        defaults.update(dict(branch=os.getenv('TRAVIS_BRANCH'),
                             service='travis-org',
                             build=os.getenv('TRAVIS_JOB_NUMBER'),
                             pull_request=os.getenv('TRAVIS_PULL_REQUEST') if os.getenv('TRAVIS_PULL_REQUEST')!='false' else '',
                             travis_job_id=os.getenv('TRAVIS_JOB_ID'),
                             owner=os.getenv('TRAVIS_REPO_SLUG').split('/',1)[0],
                             repo=os.getenv('TRAVIS_REPO_SLUG').split('/',1)[1],
                             path=os.getenv('TRAVIS_BUILD_DIR'),
                             commit=os.getenv('TRAVIS_COMMIT')))
    # --------
    # Codeship
    # --------
    elif os.getenv('CI') == "true" and os.getenv('CI_NAME') == 'codeship':
        # https://www.codeship.io/documentation/continuous-integration/set-environment-variables/
        defaults.update(dict(branch=os.getenv('CI_BRANCH'),
                             service='codeship',
                             build=os.getenv('CI_BUILD_NUMBER'),
                             build_url=os.getenv('CI_BUILD_URL'),
                             commit=os.getenv('CI_COMMIT_ID')))
    # ---------
    # Circle CI
    # ---------
    elif os.getenv('CI') == "true" and os.getenv('CIRCLECI') == 'true':
        # https://circleci.com/docs/environment-variables
        defaults.update(dict(branch=os.getenv('CIRCLE_BRANCH'),
                             service='circleci',
                             build=os.getenv('CIRCLE_BUILD_NUM'),
                             owner=os.getenv('CIRCLE_PROJECT_USERNAME'),
                             repo=os.getenv('CIRCLE_PROJECT_REPONAME'),
                             commit=os.getenv('CIRCLE_SHA1')))
    # ---------
    # Semaphore
    # ---------
    elif os.getenv('CI') == "true" and os.getenv('SEMAPHORE') == "true":
        # https://semaphoreapp.com/docs/available-environment-variables.html
        defaults.update(dict(branch=os.getenv('BRANCH_NAME'),
                             service='semaphore',
                             build=os.getenv('SEMAPHORE_BUILD_NUMBER'),
                             owner=os.getenv('SEMAPHORE_REPO_SLUG').split('/',1)[0],
                             repo=os.getenv('SEMAPHORE_REPO_SLUG').split('/',1)[1],
                             commit=os.getenv('SEMAPHORE_PROJECT_HASH_ID')))
    # --------
    # drone.io
    # --------
    elif os.getenv('CI') == "true" and os.getenv('DRONE') == "true":
        # http://docs.drone.io/env.html
        defaults.update(dict(branch=os.getenv('DRONE_BRANCH'),
                             service='drone.io',
                             build=os.getenv('BUILD_ID'),
                             build_url=os.getenv('DRONE_BUILD_URL'),
                             commit=os.getenv('DRONE_COMMIT')))
    # ---
    # git
    # ---
    else:
        # find branch, commit, repo from git command
        branch = subprocess.check_output('git rev-parse --abbrev-ref HEAD', shell=True)
        defaults.update(dict(branch=branch if branch != 'HEAD' else 'master',
                             commit=subprocess.check_output('git rev-parse HEAD', shell=True)))

    parser = argparse.ArgumentParser(prog='codecov', add_help=True,
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog="""Read more at https://codecov.io/""")
    parser.add_argument('--version', action='version', version='codecov '+version+" - https://codecov.io")
    parser.add_argument('--commit', default=defaults.pop('commit'), help="commit ref")
    parser.add_argument('--path', help="append file path for reporting properly")
    parser.add_argument('--min-coverage', default="0", help="min coverage goal, otherwise build fails")
    parser.add_argument('--branch', default=defaults.pop('branch'), help="commit branch name")
    parser.add_argument('--token', '-t', default=os.getenv("CODECOV_TOKEN"), help="codecov repository token")
    parser.add_argument('--report', '-x', help="coverage report")
    parser.add_argument('--url', default="https://codecov.io", help="url, used for debugging")
    if argv:
        codecov = parser.parse_args(argv)
    else:
        codecov = parser.parse_args()
    
    data = upload(url=codecov.url,
                  append_path=codecov.path,
                  report=codecov.report, 
                  branch=codecov.branch, 
                  commit=codecov.commit, 
                  token=codecov.token,
                  **defaults)
    return data, int(codecov.min_coverage)

def cli():
    data, min_coverage = main()
    data['version'] = version
    sys.stdout.write(dumps(data)+"\n")
    if int(data['coverage']) >= min_coverage:
        sys.exit(0)
    else:
        sys.exit("requiring %s%% coverage, commit resulted in %s%%" % (str(min_coverage), str(data['coverage'])))

if __name__ == '__main__':
    cli()
