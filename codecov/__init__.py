#!/usr/bin/python

import os
import re
import sys
import json
import rollbar
import requests
import argparse
from json import dumps
import xml.etree.cElementTree as etree

from codecov import jacoco
from codecov import clover
from codecov import cobertura

try:
    from urllib.parse import urlencode
except ImportError:  # pragma: no cover
    from urllib import urlencode

try:
    import subprocess32 as subprocess
except ImportError:
    import subprocess

# https://urllib3.readthedocs.org/en/latest/security.html#insecureplatformwarning
try:
    import urllib3
    urllib3.disable_warnings()
except:
    pass

version = VERSION = __version__ = '1.1.9'

SKIP_DIRECTORIES = re.compile(r'\/(\..+|((Sites\/www\/bower)|node_modules|vendor|bower_components|(coverage\/instrumented)|virtualenv|venv\/(lib|bin)|build\/lib|\.git|\.egg\-info))\/').search
SKIP_FILES = re.compile(r'(\.tar\.gz|\.pyc|\.egg|(\/\..+)|\.txt)$').search

rollbar.init('856822f107db4a6a8cd84b69e242378f', environment='codeocv-python')


def build_reports(root):
    reports = []
    table_of_contents = []
    accepting = set(('coverage.xml', 'coverage.json', 'jacoco.xml', 'jacocoTestReport.xml', 'clover.xml', 'coverage.txt', 'cobertura.xml', 'lcov.info', 'gcov.info'))

    for _root, dirs, files in os.walk(root):
        if SKIP_DIRECTORIES(_root):
            continue
        # add data to tboc
        for filepath in files:
            fp = os.path.join(_root, filepath).replace(root+"/", '')
            if not (SKIP_DIRECTORIES(fp) or SKIP_FILES(fp)) and '/' in fp:
                table_of_contents.append(fp)

            # search for all .lcov|.gcov
            if filepath in accepting or filepath.endswith('.lcov') or filepath.endswith('.gcov') or filepath.endswith('.lst'):
                with open(os.path.join(_root, filepath), 'r') as f:
                    if filepath.endswith('xml'):
                        xml = etree.fromstring(f.read())
                        if filepath in ('jacoco.xml', 'jacocoTestReport.xml'):
                            reports.append(dumps(jacoco.from_xml(xml)))
                        elif xml.attrib.get('generated'):
                            reports.append(dumps(clover.from_xml(xml)))
                        else:
                            reports.append(dumps(cobertura.from_xml(xml)))
                        del xml
                    else:
                        reports.append(f.read())

    # (python), try to generate a report
    if len(reports) == 0:
        try_to_run('coverage xml')
        if os.path.exists(os.path.join(root, 'coverage.xml')):
            with open(os.path.join(root, 'coverage.xml'), 'r') as f:
                reports.append(dumps(cobertura.from_xml(etree.fromstring(f.read()))))

        # warn when no reports found and is python
        if len(reports) == 0:
            # TODO send `coverage debug sys` to rollbar
            sys.stdout.write("No reports found. You may need to add a coverage config file. Visit http://bit.ly/1slucpy for configuration help.")

    assert len(reports) > 0, "error no coverage report found, could not upload to codecov"

    # join reports together
    return "\n<<<<<< EOF\n".join(["\n".join(table_of_contents)] + reports)


def try_to_run(cmd):
    try:
        subprocess.check_output(cmd, shell=True)
    except:
        sys.stdout.write("Error running `%s`. Codecov team will be notified" % cmd)


def upload(url, root, env=None, **kwargs):
    try:
        if not root:
            root = os.getcwd()
        args = dict(commit='', branch='', job='')
        args.update(kwargs)
        assert args.get('branch') not in ('', None), "branch is required"
        assert args.get('commit') not in ('', None), "commit hash is required"
        assert any((args.get('job'),
                   (args.get('build') and args.get('service') == 'circleci'),
                   args.get('token'))), "missing token or other required argument(s)"

        reports = build_reports(root)

        if env:
            reports = "\n<<<<<< ENV\n".join(("\n".join(["%s=%s" % (k, os.getenv(k, '')) for k in env]), reports))

        kwargs['package'] = "codecov-v%s" % VERSION

        url = "%s/upload/v2?%s" % (url, urlencode(dict([(k, v.strip()) for k, v in kwargs.items() if v is not None])))

        result = requests.post(url, data=reports)
        if result.status_code != 200:
            sys.stdout.write(result.text)
        result.raise_for_status()
        return result.json()

    except AssertionError as e:
        rollbar.report_exc_info()
        return dict(message=str(e), uploaded=False, coverage=0)


def main(*argv):
    defaults = dict(commit='', branch='', job='', root=None, pull_request='', build_url='')

    # -------
    # Jenkins
    # -------
    if os.getenv('JENKINS_URL'):
        # https://wiki.jenkins-ci.org/display/JENKINS/Building+a+software+project
        defaults.update(dict(branch=os.getenv('ghprbSourceBranch') or os.getenv('GIT_BRANCH'),
                             service='jenkins',
                             commit=os.getenv('ghprbActualCommit') or os.getenv('GIT_COMMIT'),
                             build=os.getenv('BUILD_NUMBER'),
                             pull_request=os.getenv('ghprbPullId'),
                             root=os.getenv('WORKSPACE'),
                             build_url=os.getenv('BUILD_URL')))
    # ---------
    # Travis CI
    # ---------
    elif os.getenv('CI') == "true" and os.getenv('TRAVIS') == "true":
        # http://docs.travis-ci.com/user/ci-environment/#Environment-variables
        defaults.update(dict(branch=os.getenv('TRAVIS_BRANCH'),
                             service='travis-org',
                             build=os.getenv('TRAVIS_JOB_NUMBER'),
                             pull_request=os.getenv('TRAVIS_PULL_REQUEST') if os.getenv('TRAVIS_PULL_REQUEST') != 'false' else '',
                             job=os.getenv('TRAVIS_JOB_ID'),
                             slug=os.getenv('TRAVIS_REPO_SLUG'),
                             root=os.getenv('TRAVIS_BUILD_DIR'),
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
                             slug=os.getenv('SEMAPHORE_REPO_SLUG'),
                             commit=os.getenv('REVISION')))
    # --------
    # drone.io
    # --------
    elif os.getenv('CI') == "true" and os.getenv('DRONE') == "true":
        # http://docs.drone.io/env.html
        defaults.update(dict(branch=os.getenv('DRONE_BRANCH'),
                             service='drone.io',
                             build=os.getenv('DRONE_BUILD_NUMBER'),
                             build_url=os.getenv('DRONE_BUILD_URL'),
                             commit=os.getenv('DRONE_COMMIT')))
    # --------
    # AppVeyor
    # --------
    elif os.getenv('CI') == "True" and os.getenv('APPVEYOR') == 'True':
        # http://www.appveyor.com/docs/environment-variables
        defaults.update(dict(branch=os.getenv('APPVEYOR_REPO_BRANCH'),
                             service="appveyor",
                             job=os.getenv("APPVEYOR_BUILD_VERSION"),
                             build=os.getenv('APPVEYOR_JOB_ID'),
                             slug=os.getenv('APPVEYOR_REPO_NAME'),
                             commit=os.getenv('APPVEYOR_REPO_COMMIT')))
    # -------
    # Wercker
    # -------
    elif os.getenv('CI') == "true" and os.getenv('WERCKER_GIT_BRANCH'):
        # http://devcenter.wercker.com/articles/steps/variables.html
        defaults.update(dict(branch=os.getenv('WERCKER_GIT_BRANCH'),
                             service="wercker",
                             build=os.getenv('WERCKER_MAIN_PIPELINE_STARTED'),
                             owner=os.getenv('WERCKER_GIT_OWNER'),
                             repo=os.getenv('WERCKER_GIT_REPOSITORY'),
                             commit=os.getenv('WERCKER_GIT_COMMIT')))
    # ------
    # Magnum
    # ------
    elif os.getenv('CI') == "true" and os.getenv('MAGNUM') == 'true':
        # https://magnum-ci.com/docs/environment
        defaults.update(dict(service="magnum",
                             branch=os.getenv('CI_BRANCH'),
                             build=os.getenv('CI_BUILD_NUMBER'),
                             commit=os.getenv('CI_COMMIT')))
    # ---------
    # Shippable
    # ---------
    elif os.getenv('SHIPPABLE') == "true":
        # http://docs.shippable.com/en/latest/config.html#common-environment-variables
        defaults.update(dict(branch=os.getenv('BRANCH'),
                             service='shippable',
                             build=os.getenv('BUILD_NUMBER'),
                             build_url=os.getenv('BUILD_URL'),
                             pull_request=os.getenv('PULL_REQUEST') if os.getenv('PULL_REQUEST') != 'false' else '',
                             slug=os.getenv('REPO_NAME'),
                             commit=os.getenv('COMMIT')))
    # ---------
    # Gitlab CI
    # ---------
    elif os.getenv('CI_SERVER_NAME') == "GitLab CI":
        # http://doc.gitlab.com/ci/examples/README.html#environmental-variables
        # https://gitlab.com/gitlab-org/gitlab-ci-runner/blob/master/lib/build.rb#L96
        defaults.update(dict(service='gitlab',
                             branch=os.getenv('CI_BUILD_REF_NAME'),
                             build=os.getenv('CI_BUILD_ID'),
                             slug=os.getenv('CI_BUILD_REPO').split('/', 3)[-1].replace('.git', ''),
                             root=os.getenv('CI_PROJECT_DIR'),
                             commit=os.getenv('CI_BUILD_REF')))
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
    parser.add_argument('--version', '-v', action='version', version='codecov-python v'+version+" - https://codecov.io/")
    parser.add_argument('--commit', '-c', default=defaults.pop('commit', None), help="commit ref")
    parser.add_argument('--slug', '-r', default=defaults.pop('slug', None), help="specify repository slug for Enterprise ex. codecov -r myowner/myrepo")
    parser.add_argument('--branch', '-b', default=defaults.pop('branch', None), help="commit branch name")
    parser.add_argument('--json', action="store_true", default=False, help="output json data only")
    parser.add_argument('--env', '-e', nargs="*", help="store config variables for coverage builds")
    parser.add_argument('--token', '-t', default=os.getenv("CODECOV_TOKEN"), help="codecov repository token")
    parser.add_argument('--url', '-u', default=os.getenv("CODECOV_ENDPOINT", "https://codecov.io"), help="url for enteprise customers")
    if argv:
        codecov = parser.parse_args(argv)
    else:
        codecov = parser.parse_args()

    data = upload(url=codecov.url, branch=codecov.branch, commit=codecov.commit, token=codecov.token, env=codecov.env, slug=codecov.slug, **defaults)
    return data, codecov


def cli():
    try:
        defaults = dict(uploaded=False, url="n/a", version=version, message="unknown")
        data, codecov = main()
        defaults.update(data)
        if codecov.json:
            sys.stdout.write(json.dumps(defaults))
        else:
            sys.stdout.write("Uploaded: %(uploaded)s\nReport URL: %(url)s\nUpload Version: codecov-v%(version)s\nMessage: %(message)s\n" % defaults)
    except:
        rollbar.report_exc_info()
        raise


if __name__ == '__main__':
    cli()
