#!/usr/bin/python

import os
import re
import sys
import requests
import argparse
from json import loads
from json import dumps
import xml.etree.cElementTree as etree

try:
    from urllib.parse import urlencode
except ImportError:  # pragma: no cover
    from urllib import urlencode

if sys.version_info < (2, 7):
    from future import standard_library
    standard_library.install_aliases()
    import subprocess
else:
    import subprocess

# https://urllib3.readthedocs.org/en/latest/security.html#insecureplatformwarning
try:
    import logging
    logging.captureWarnings(True)
except:
    # not py2.6 compatible
    pass


version = VERSION = __version__ = '1.3.0'


def jacoco(report):
    """
    Some Jacoco can be huge. This is way to trim them down.
    nr = line number
    mi = missed instructions
    ci = covered instructions
    mb = missed branches
    cb = covered branches
    """
    report = etree.fromstring(report)
    coverage = {}
    for package in report.getiterator('package'):
        base_name = package.attrib['name']
        for source in package.getiterator('sourcefile'):
            lines = []
            append = lines.append
            for line in source.getiterator('line'):
                l = line.attrib
                if l['mb'] != "0":
                    append((str(l['nr']), "%s/%d" % (l['cb'], int(l['mb'])+int(l['cb']))))
                elif l['cb'] != "0":
                    append((str(l['nr']), "%s/%s" % (l['cb'], l['cb'])))
                else:
                    append((str(l['nr']), int(l['ci'])))
            if not lines:
                continue

            coverage["%s/%s" % (base_name, source.attrib['name'])] = dict(lines)

    return dumps(dict(coverage=coverage))


ignored_path = re.compile(r'(/vendor)|'
                          r'(/js/generated/coverage)|'
                          r'(/__pycache__)|'
                          r'(/coverage/instrumented)|'
                          r'(/build/lib)|'
                          r'(/htmlcov)|'
                          r'(\.egg-info)|'
                          r'(/\.git)|'
                          r'(/\.tox)|'
                          r'(/\.?v?(irtual)?envs?)', re.I).search

ignored_file = re.compile('.*('
                          r'(\.coverage)|'
                          r'(\.coveragerc)|'
                          r'(\.DS_Store)|'
                          r'(\.egg)|'
                          r'(\.gcov)|'
                          r'(\.gif)|'
                          r'(\.gitignore)|'
                          r'(\.ini)|'
                          r'(\.jpeg)|'
                          r'(\.jpg)|'
                          r'(\.json)|'
                          r'(\.sav)|'
                          r'(\.rst)|'
                          r'(\.lcov)|'
                          r'(\.md)|'
                          r'(\.png)|'
                          r'(\.pyc)|'
                          r'(\.pyc)|'
                          r'(\.sh)|'
                          r'(\.tar\.gz)|'
                          r'(\.tgz)|'
                          r'(\.txt)|'
                          r'(\.xml)|'
                          r'(\.yml)'
                          ')$', re.I).match

ignored_report = re.compile('.*('
                            r'(/\.coverage.*)|'
                            r'(\.coveragerc)|'
                            r'(\.egg)|'
                            r'(\.gif)|'
                            r'(\.ini)|'
                            r'(\.jpeg)|'
                            r'(\.jpg)|'
                            r'(\.md)|'
                            r'(\.png)|'
                            r'(\.pyc)|'
                            r'(\.sh)|'
                            r'(\.tar\.gz)|'
                            r'(\.yml)|'
                            r'(coverage\.jade)|'
                            r'(include\.lst)|'
                            r'(inputFiles\.lst)|'
                            r'(createdFiles\.lst)|'
                            r'(scoverage\.measurements\..*)|'
                            r'(test_.*_coverage\.txt)|'
                            r'(conftest_.*\.c\.gcov)'
                            ')$', re.I).match

is_report = re.compile('.*('
                       r'([^/]*coverage[^/]*)|'
                       r'(\.gcov)|'
                       r'(\.lcov)|'
                       r'(\.lst)|'
                       r'(clover\.xml)|'
                       r'(cobertura\.xml)|'
                       r'(gcov\.info)|'
                       r'(jacoco[^/]*\.xml)|'
                       r'(lcov\.info)|'
                       r'(luacov\.report\.out)|'
                       r'(nosetests\.xml)|'
                       r'(report\.xml)'
                       ')$', re.I).match

opj = os.path.join  # for faster access


def write(text):
    sys.stdout.write(text + '\n')


def fopen(path):
    if sys.version_info < (3, 0):
        with open(path, 'r') as f:
            return f.read()
    else:
        try:
            with open(path, 'r', encoding='utf8') as f:
                return f.read()
        except UnicodeDecodeError:
            with open(path, 'r', encoding='ISO-8859-1') as f:
                return f.read()


def read(filepath):
    write('    + %s bytes=%d' % (filepath, os.path.getsize(filepath)))
    report = fopen(filepath)
    if 'jacoco' in filepath:
        report = jacoco(report)
    return '# path=' + filepath + '\n' + report


def build_reports(specific_files, root, bower_components):
    reports = []
    toc = []
    toc_append = toc.append

    # build toc and find
    for _root, dirs, files in os.walk(root):
        if not ignored_path(_root) and bower_components not in _root:
            # add data to tboc
            for filepath in files:
                fullpath = opj(_root, filepath)
                if not specific_files and is_report(fullpath) and not ignored_report(fullpath):
                    # found report
                    reports.append(read(filepath))
                elif not ignored_file(fullpath):
                    toc_append(fullpath.replace(root + '/', ''))

    if specific_files:
        write('    Targeting specific files')
        for filepath in specific_files:
            reports.append(read(filepath))

    else:
        # (python), try to generate a report
        if len(reports) == 0 and os.path.exists(opj(root, '.coverage')):
            write('    Calling coverage xml')
            try_to_run('coverage xml')
            if os.path.exists(opj(root, 'coverage.xml')):
                reports.append(read(opj(root, 'coverage.xml')))

            # warn when no reports found and is python
            if len(reports) == 0:
                # TODO send `coverage debug sys`
                write("    No reports found. You may need to add a coverage config file. Visit http://bit.ly/1slucpy for configuration help.")

    assert len(reports) > 0, "error no coverage report found, could not upload to codecov"

    # join reports together
    return '\n'.join(toc) + '\n<<<<<< EOF\n' + '\n<<<<<< EOF\n'.join(reports)


def try_to_run(cmd):
    try:
        subprocess.check_output(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        write('    Error running `%s`: %s' % (cmd, str(getattr(e, 'output', str(e)))))


def upload(url, root, env=None, files=None, dump=False, **query):
    try:
        if not root:
            root = os.getcwd()

        write('==> Validating arguments')
        assert query.get('branch') not in ('', None), "Branch argument is missing. Please specify via --branch=:name"
        assert query.get('commit') not in ('', None), "Commit sha is missing. Please specify via --commit=:sha"
        assert any((query.get('job'),
                   (query.get('build') and query.get('service') == 'circleci'),
                   query.get('token'))), "Missing repository upload token"

        # Read token from file
        if query.get('token') and query.get('token')[0] == '@':
            write('    Reading token from file')
            query['token'] = fopen(opj(os.getcwd(), query['token'][1:])).strip()

        write('==> Reading file network')

        # Detect .bowerrc
        # ---------------
        bower_components = '/bower_components'
        try:
            bowerrc = loads(fopen(opj(query.get('root', os.getcwd()), '.bowerrc')))
            bower_components = '/' + (bowerrc.get('directory') or 'bower_components').replace('./', '').strip('/')
            write('    .bowerrc detected, ignoring ' + bower_components)
        except:
            pass

        # Read Network
        # ------------
        reports = build_reports(files, root, bower_components)

        if env:
            write('==> Appending environment variables')
            for k in env:
                write('    + ' + k)

            reports = '\n'.join(["%s=%s" % (k, os.getenv(k, '')) for k in env]) + '\n<<<<<< ENV\n' + reports

        query['package'] = "py%s" % VERSION
        query = (urlencode(dict([(k, v.strip()) for k, v in query.items() if v not in ('', None)])))

        write('==> Uploading to Codecov')
        write('    Url: ' + url)
        write('    Query: ' + query)
        if dump:
            write('-------------------- Debug --------------------')
            write(reports)
            write('--------------------  EOF  --------------------')
            return query, reports

        result = requests.post(url + '/upload/v2?' + query, data=reports, headers={"Accept": "text/plain"})
        write('    ' + result.text)
        result.raise_for_status()
        return query, result.text

    except AssertionError as e:
        write('')
        write('Error: ' + str(e))
        return None, None


def main(*argv, **kwargs):
    write('Codeceov v'+version)
    query = dict(commit='', branch='', job='', root=None, pr='', build_url='')

    # Detect CI
    # ---------
    if not ('-h' in argv or '--help' in argv):
        write('==> Detecting CI Provider')
        # -------
        # Jenkins
        # -------
        if os.getenv('JENKINS_URL'):
            # https://wiki.jenkins-ci.org/display/JENKINS/Building+a+software+project
            # https://wiki.jenkins-ci.org/display/JENKINS/GitHub+pull+request+builder+plugin#GitHubpullrequestbuilderplugin-EnvironmentVariables
            query.update(dict(branch=os.getenv('ghprbSourceBranch') or os.getenv('GIT_BRANCH'),
                              service='jenkins',
                              commit=os.getenv('ghprbActualCommit') or os.getenv('GIT_COMMIT'),
                              pr=os.getenv('ghprbPullId', 'false'),
                              build=os.getenv('BUILD_NUMBER'),
                              root=os.getenv('WORKSPACE'),
                              build_url=os.getenv('BUILD_URL')))
            write('    Jenkins Detected')

        # ---------
        # Travis CI
        # ---------
        elif os.getenv('CI') == "true" and os.getenv('TRAVIS') == "true":
            # http://docs.travis-ci.com/user/ci-environment/#Environment-variables
            query.update(dict(branch=os.getenv('TRAVIS_BRANCH'),
                              service='travis',
                              build=os.getenv('TRAVIS_JOB_NUMBER'),
                              pr=os.getenv('TRAVIS_PULL_REQUEST'),
                              job=os.getenv('TRAVIS_JOB_ID'),
                              slug=os.getenv('TRAVIS_REPO_SLUG'),
                              root=os.getenv('TRAVIS_BUILD_DIR'),
                              commit=os.getenv('TRAVIS_COMMIT')))
            write('    Travis Detected')

        # --------
        # Codeship
        # --------
        elif os.getenv('CI') == "true" and os.getenv('CI_NAME') == 'codeship':
            # https://www.codeship.io/documentation/continuous-integration/set-environment-variables/
            query.update(dict(branch=os.getenv('CI_BRANCH'),
                              service='codeship',
                              build=os.getenv('CI_BUILD_NUMBER'),
                              build_url=os.getenv('CI_BUILD_URL'),
                              commit=os.getenv('CI_COMMIT_ID')))
            write('    Codeship Detected')

        # ---------
        # Circle CI
        # ---------
        elif os.getenv('CI') == "true" and os.getenv('CIRCLECI') == 'true':
            # https://circleci.com/docs/environment-variables
            query.update(dict(branch=os.getenv('CIRCLE_BRANCH'),
                              service='circleci',
                              build=os.getenv('CIRCLE_BUILD_NUM') + "." + os.getenv('CIRCLE_NODE_INDEX'),
                              pr=os.getenv('CIRCLE_PR_NUMBER'),
                              slug=os.getenv('CIRCLE_PROJECT_USERNAME') + "/" + os.getenv('CIRCLE_PROJECT_REPONAME'),
                              commit=os.getenv('CIRCLE_SHA1')))
            write('    Circle CI Detected')

        # ---------
        # Semaphore
        # ---------
        elif os.getenv('CI') == "true" and os.getenv('SEMAPHORE') == "true":
            # https://semaphoreapp.com/docs/available-environment-variables.html
            query.update(dict(branch=os.getenv('BRANCH_NAME'),
                              service='semaphore',
                              build="%s.%s" % (os.getenv('SEMAPHORE_BUILD_NUMBER'), os.getenv('SEMAPHORE_CURRENT_THREAD')),
                              slug=os.getenv('SEMAPHORE_REPO_SLUG'),
                              commit=os.getenv('REVISION')))
            write('    Semaphore Detected')

        # --------
        # drone.io
        # --------
        elif os.getenv('CI') == "true" and os.getenv('DRONE') == "true":
            # http://docs.drone.io/env.html
            query.update(dict(branch=os.getenv('DRONE_BRANCH'),
                              service='drone.io',
                              build=os.getenv('DRONE_BUILD_NUMBER'),
                              root=os.getenv('DRONE_BUILD_DIR'),
                              build_url=os.getenv('DRONE_BUILD_URL'),
                              commit=os.getenv('DRONE_COMMIT')))
            write('    Drone Detected')

        # --------
        # AppVeyor
        # --------
        elif os.getenv('CI') == "True" and os.getenv('APPVEYOR') == 'True':
            # http://www.appveyor.com/docs/environment-variables
            query.update(dict(branch=os.getenv('APPVEYOR_REPO_BRANCH'),
                              service="appveyor",
                              job='/'.join((os.getenv('APPVEYOR_ACCOUNT_NAME'), os.getenv('APPVEYOR_PROJECT_SLUG'), os.getenv('APPVEYOR_BUILD_VERSION'))),
                              build=os.getenv('APPVEYOR_JOB_ID'),
                              pr=os.getenv('APPVEYOR_PULL_REQUEST_NUMBER'),
                              slug=os.getenv('APPVEYOR_REPO_NAME'),
                              commit=os.getenv('APPVEYOR_REPO_COMMIT')))
            write('    AppVeyor Detected')

        # -------
        # Wercker
        # -------
        elif os.getenv('CI') == "true" and os.getenv('WERCKER_GIT_BRANCH'):
            # http://devcenter.wercker.com/articles/steps/variables.html
            query.update(dict(branch=os.getenv('WERCKER_GIT_BRANCH'),
                              service="wercker",
                              build=os.getenv('WERCKER_MAIN_PIPELINE_STARTED'),
                              slug=os.getenv('WERCKER_GIT_OWNER') + '/' + os.getenv('WERCKER_GIT_REPOSITORY'),
                              commit=os.getenv('WERCKER_GIT_COMMIT')))
            write('    Wercker Detected')

        # -------
        # Snap CI
        # -------
        elif os.getenv('CI') == "true" and os.getenv('SNAP_CI') == "true":
            # https://docs.snap-ci.com/environment-variables/
            query.update(dict(branch=os.getenv('SNAP_BRANCH') or os.getenv('SNAP_UPSTREAM_BRANCH'),
                              service="snap",
                              build=os.getenv('SNAP_PIPELINE_COUNTER'),
                              pr=os.getenv('SNAP_PULL_REQUEST_NUMBER'),
                              commit=os.getenv('SNAP_COMMIT') or os.getenv('SNAP_UPSTREAM_COMMIT')))
            write('    Snap CI Detected')

        # ------
        # Magnum
        # ------
        elif os.getenv('CI') == "true" and os.getenv('MAGNUM') == 'true':
            # https://magnum-ci.com/docs/environment
            query.update(dict(service="magnum",
                              branch=os.getenv('CI_BRANCH'),
                              build=os.getenv('CI_BUILD_NUMBER'),
                              commit=os.getenv('CI_COMMIT')))
            write('    Magnum Detected')

        # ---------
        # Shippable
        # ---------
        elif os.getenv('SHIPPABLE') == "true":
            # http://docs.shippable.com/en/latest/config.html#common-environment-variables
            query.update(dict(branch=os.getenv('BRANCH'),
                              service='shippable',
                              build=os.getenv('BUILD_NUMBER'),
                              build_url=os.getenv('BUILD_URL'),
                              pr=os.getenv('PULL_REQUEST') if os.getenv('PULL_REQUEST') != 'false' else '',
                              slug=os.getenv('REPO_NAME'),
                              commit=os.getenv('COMMIT')))
            write('    Shippable Detected')

        # ---------
        # Gitlab CI
        # ---------
        elif os.getenv('CI_SERVER_NAME') == "GitLab CI":
            # http://doc.gitlab.com/ci/examples/README.html#environmental-variables
            # https://gitlab.com/gitlab-org/gitlab-ci-runner/blob/master/lib/build.rb#L96
            query.update(dict(service='gitlab',
                              branch=os.getenv('CI_BUILD_REF_NAME'),
                              build=os.getenv('CI_BUILD_ID'),
                              slug=os.getenv('CI_BUILD_REPO').split('/', 3)[-1].replace('.git', ''),
                              root=os.getenv('CI_PROJECT_DIR'),
                              commit=os.getenv('CI_BUILD_REF')))
            write('    Gitlab CI Detected')

        # ---
        # git
        # ---
        else:
            try:
                # find branch, commit, repo from git command
                branch = subprocess.check_output('git rev-parse --abbrev-ref HEAD', shell=True)
                query.update(dict(branch=branch if branch != 'HEAD' else 'master',
                                  commit=subprocess.check_output('git rev-parse HEAD', shell=True)))
                write('    No CI Detected.')
            except:
                # may not be in a git backed repo
                pass

    # Build Parser
    # ------------
    parser = argparse.ArgumentParser(prog='codecov', add_help=True,
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog="""Upload reports to Codecov""")
    parser.add_argument('--version', '-v', action='version', version='Codecov py-v'+version+" - https://codecov.io/")
    parser.add_argument('--file', '-f', nargs="*", default=None, help="Target a specific file for uploading")
    parser.add_argument('--commit', '-c', default=None, help="commit ref")
    parser.add_argument('--slug', '-r', default=None, help="specify repository slug for Enterprise ex. codecov -r myowner/myrepo")
    parser.add_argument('--build', default=None, help="(advanced) specify a custom build number to distinguish ci jobs, provided automatically for supported ci companies")
    parser.add_argument('--branch', '-b', default=None, help="commit branch name")
    parser.add_argument('--env', '-e', nargs="*", help="store config variables for coverage builds")
    parser.add_argument('--token', '-t', default=os.getenv("CODECOV_TOKEN"), help="codecov repository token")
    parser.add_argument('--dump', action="store_true", help="Dump collected data for debugging")
    parser.add_argument('--url', '-u', default=os.getenv("CODECOV_ENDPOINT", "https://codecov.io"), help="url for enteprise customers")

    # Parse Arguments
    # ---------------
    if argv:
        codecov = parser.parse_args(argv)
    else:
        codecov = parser.parse_args()

    if codecov.build:
        query['build'] = codecov.build

    if codecov.commit:
        query['commit'] = codecov.commit

    if codecov.slug:
        query['slug'] = codecov.slug

    if codecov.branch:
        query['branch'] = codecov.branch

    # Upload
    # ------
    url, reports = upload(url=codecov.url,
                          files=codecov.file,
                          dump=codecov.dump,
                          env=codecov.env,
                          token=codecov.token,
                          **query)

    if kwargs.get('debug'):
        return dict(reports=reports, url=url, codecov=codecov, query=query)

    elif reports is None:
        sys.exit(1)


if __name__ == '__main__':
    main()
