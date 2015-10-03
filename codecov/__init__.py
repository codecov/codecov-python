#!/usr/bin/python

import os
import re
import sys
import requests
import argparse
from json import loads, dumps
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


version = VERSION = __version__ = '1.5.0'

COLOR = True


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
                          r'(/node_modules)|'
                          r'(\.egg-info)|'
                          r'(/\.git)|'
                          r'(/\.hg)|'
                          r'(/\.tox)|'
                          r'(/\.?v?(irtual)?envs?)', re.I).search

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
                            r'(\.whl)|'
                            r'(\.cpp)|'
                            r'(\.pyc?)|'
                            r'(\.cfg)|'
                            r'(\.js)|'
                            r'(\.html)|'
                            r'(\.sh)|'
                            r'(\.tar\.gz)|'
                            r'(\.yml)|'
                            r'(\.xcconfig)|'
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


def write(text, color=None):
    global COLOR
    if COLOR:
        text = text.replace('==>', '\033[90m==>\033[0m')
        text = text.replace('XX>', '\033[31mXX>\033[0m')
        if text[:6] == 'Error:':
            text = '\033[41mError:\033[0m\033[91m%s\033[0m' % text[6:]
        elif text[:4] == 'Tip:':
            text = '\033[42mTip:\033[0m\033[32m%s\033[0m' % text[4:]
        elif text.strip()[:4] == 'http':
            text = '\033[92m%s\033[0m' % text
        elif text[:7] == 'Codecov':
            text = """
      _____          _
     / ____|        | |
    | |     ___   __| | ___  ___ _____   __
    | |    / _ \ / _` |/ _ \/ __/ _ \ \ / /
    | |___| (_) | (_| |  __/ (_| (_) \ V /
     \_____\___/ \__,_|\___|\___\___/ \_/
                                    %s\n""" % text.split(' ')[1]
        elif color == 'red':
            text = '\033[91m%s\033[0m' % text
        elif color == 'green':
            text = '\033[92m%s\033[0m' % text

    sys.stdout.write(text + '\n')


def fopen(path):
    try:
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
    except Exception as e:
        # on none of that works. just print the issue and continue
        write('    - Ignored: ' + str(e))


def read(filepath):
    try:
        report = fopen(filepath)
        if report is None:
            return
        if 'jacoco' in filepath:
            report = jacoco(report)
        write('    + %s bytes=%d' % (filepath, os.path.getsize(filepath)))
        return '# path=' + filepath + '\n' + report
    except Exception as e:
        # Ex: No such file or directory, skip them
        write('    - Ignored: ' + str(e))


def try_to_run(cmd):
    try:
        return subprocess.check_output(cmd, shell=True).decode('utf-8')
    except subprocess.CalledProcessError as e:
        write('    Error running `%s`: %s' % (cmd, str(getattr(e, 'output', str(e)))))


def main(*argv, **kwargs):
    root = os.getcwd()

    # Build Parser
    # ------------
    parser = argparse.ArgumentParser(prog='codecov', add_help=True,
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog="""Upload reports to Codecov""")
    basics = parser.add_argument_group('======================== Basics ========================')
    basics.add_argument('--version', '-v', action='version', version='Codecov py-v'+version+" - https://codecov.io/")
    basics.add_argument('--token', '-t', default=os.getenv("CODECOV_TOKEN"), help="Private repository token. Not required for public repos on Travis, CircleCI and AppVeyor")
    basics.add_argument('--file', '-f', nargs="*", default=None, help="Target a specific file for uploading")
    basics.add_argument('--env', '-e', nargs="*", default=os.getenv("CODECOV_ENV"), help="Store environment variables to help distinguish CI builds. Example: http://bit.ly/1ElohCu")
    basics.add_argument('--no-fail', action="store_true", default=False, help="If Codecov fails do not fail CI build.")

    gcov = parser.add_argument_group('======================== gcov ========================')
    gcov.add_argument('--gcov-root', default=None, help="Project root directory when preparing gcov")
    gcov.add_argument('--gcov-glob', nargs="*", default=[], help="Paths to ignore during gcov gathering")
    gcov.add_argument('--gcov-exec', default='gcov', help="gcov executable to run. Defaults to 'gcov'")
    gcov.add_argument('--gcov-args', default='', help="extra arguments to pass to gcov")

    advanced = parser.add_argument_group('======================== Advanced ========================')
    advanced.add_argument('-X', '--disable', nargs="*", default=[], help="Disable features. Accepting `search` to disable crawling through directories, `detect` to disable detecting CI provider, `gocv` disable gcov commands")
    advanced.add_argument('--root', default=None, help="Project directory. Default: current direcory or provided in CI environment variables")
    advanced.add_argument('--commit', '-c', default=None, help="Commit sha, set automatically")
    advanced.add_argument('--branch', '-b', default=None, help="Branch name")
    advanced.add_argument('--build', default=None, help="Specify a custom build number to distinguish ci jobs, provided automatically for supported ci companies")

    enterprise = parser.add_argument_group('======================== Enterprise ========================')
    enterprise.add_argument('--slug', '-r', default=os.getenv("CODECOV_SLUG"), help="Specify repository slug for Enterprise ex. owner/repo")
    enterprise.add_argument('--url', '-u', default=os.getenv("CODECOV_URL", "https://codecov.io"), help="Your Codecov endpoint")

    debugging = parser.add_argument_group('======================== Debugging ========================')
    debugging.add_argument('--dump', action="store_true", help="Dump collected data and do not send to Codecov")
    debugging.add_argument('--no-color', action="store_true", help="Do not output with color")

    # Parse Arguments
    # ---------------
    if argv:
        codecov = parser.parse_args(argv)
    else:
        codecov = parser.parse_args()

    global COLOR
    COLOR = not codecov.no_color

    write('Codecov v'+version)
    query = dict(commit='', branch='', job='', pr='', build_url='',
                 token=codecov.token)
    language = None

    # Detect CI
    # ---------
    if 'detect' in codecov.disable:
        write('XX> Detecting CI provider disabled.')

    else:
        write('==> Detecting CI provider')
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
                              build_url=os.getenv('BUILD_URL')))
            root = os.getenv('WORKSPACE') or root
            write('    Jenkins Detected')

        # ---------
        # Travis CI
        # ---------
        elif os.getenv('CI') == "true" and os.getenv('TRAVIS') == "true":
            # http://docs.travis-ci.com/user/environment-variables/#Default-Environment-Variables
            query.update(dict(branch=os.getenv('TRAVIS_BRANCH'),
                              service='travis',
                              build=os.getenv('TRAVIS_JOB_NUMBER'),
                              pr=os.getenv('TRAVIS_PULL_REQUEST'),
                              job=os.getenv('TRAVIS_JOB_ID'),
                              slug=os.getenv('TRAVIS_REPO_SLUG'),
                              commit=os.getenv('TRAVIS_COMMIT')))
            root = os.getenv('TRAVIS_BUILD_DIR') or root
            write('    Travis Detected')
            language = (list(filter(lambda l: os.getenv('TRAVIS_%s_VERSION' % l.upper()),
                                    ('dart', 'go', 'haxe', 'jdk', 'julia', 'node', 'otp',
                                     'perl', 'php', 'python', 'r', 'ruby', 'rust', 'scala'))) + [''])[0]

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
                              job=os.getenv('CIRCLE_BUILD_NUM') + "." + os.getenv('CIRCLE_NODE_INDEX'),
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
                              build=os.getenv('SEMAPHORE_BUILD_NUMBER') + '.' + os.getenv('SEMAPHORE_CURRENT_THREAD'),
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
                              build_url=os.getenv('DRONE_BUILD_URL'),
                              commit=subprocess.check_output("git rev-parse HEAD || hg id -i --debug | tr -d '+'", shell=True)))
            root = os.getenv('DRONE_BUILD_DIR') or root
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
                              pr=os.getenv('PULL_REQUEST'),
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
                              commit=os.getenv('CI_BUILD_REF')))
            root = os.getenv('CI_PROJECT_DIR') or root
            write('    Gitlab CI Detected')

        # ---
        # git
        # ---
        else:
            try:
                # find branch, commit, repo from git command
                branch = subprocess.check_output('git rev-parse --abbrev-ref HEAD || hg branch', shell=True)
                query.update(dict(branch=branch if branch != 'HEAD' else '',
                                  commit=subprocess.check_output("git rev-parse HEAD || hg id -i --debug | tr -d '+'", shell=True)))
                write('    No CI Detected. Using git/mercurial')
            except:  # pragma: no cover
                # may not be in a git backed repo
                pass

    # Update Query
    # ------------
    if codecov.build:
        query['build'] = codecov.build

    if codecov.commit:
        query['commit'] = codecov.commit

    if codecov.slug:
        query['slug'] = codecov.slug

    if codecov.branch:
        query['branch'] = codecov.branch

    if codecov.root:
        root = codecov.root

    # Upload
    # ------
    try:
        write('==> Prepairing upload')

        # Read token from file
        # --------------------
        if query.get('token') and query.get('token')[0] == '@':
            write('    Reading token from file')
            query['token'] = fopen(opj(os.getcwd(), query['token'][1:])).strip()

        assert query.get('commit') not in ('', None), "Commit sha is missing. Please specify via --commit=:sha"
        assert query.get('job') or query.get('token'), "Missing repository upload token"

        # Build TOC
        # ---------
        toc = str((try_to_run('cd %s && git ls-files' % root) or try_to_run('git ls-files')
                   or try_to_run('cd %s && hg locate' % root) or try_to_run('hg locate')
                   or '').strip())

        # Processing gcov
        # ---------------
        if 'gcov' in codecov.disable:
            write('XX> Skip processing gcov')

        else:
            write('==> Processing gcov (disable by -X gcov)')
            if os.path.isdir(os.path.expanduser('~/Library/Developer/Xcode/DerivedData')):
                write('    Found OSX DerivedData')
                try_to_run("find ~/Library/Developer/Xcode/DerivedData -name '*.gcda' -exec %s %s {} +" % (codecov.gcov_exec, codecov.gcov_args))

                # xcode7
                profdata = try_to_run("find ~/Library/Developer/Xcode/DerivedData -name 'Coverage.profdata' | head -1")
                if profdata:
                    _dir = os.path.dirname(profdata)
                    for _type in ('app', 'framework', 'xctest'):
                        _file = try_to_run('find "%s" -name "*.%s" | head -1' % (_dir, _type))
                        if _file:
                            _proj = _file.split('/')[-2].split('.')[0]
                            try_to_run('xcrun llvm-cov show -instr-profile "%s" "%s/%s" > "%s.coverage.txt"' % (profdata, _file, _proj, _type))

            cmd = "find %s -type f -name '*.gcno' %s -exec %s %s {} +" % (
                  codecov.gcov_root or root, " ".join(map(lambda a: "-not -path '%s'" % a, codecov.gcov_glob)),
                  codecov.gcov_exec, codecov.gcov_args)
            write('    Executing gcov (%s)' % cmd)
            try_to_run(cmd)

        # Collect Reports
        # ---------------
        write('==> Collecting reports')
        reports = []

        if 'search' in codecov.disable:
            write('XX> Searching for reports disabled')
        else:

            # Detect .bowerrc
            # ---------------
            bower_components = '/bower_components'
            bowerrc = opj(root, '.bowerrc')
            if os.path.exists(bowerrc):
                write('    Detecting .bowerrc file')
                try:
                    bower_components = '/' + (loads(fopen(bowerrc)).get('directory') or 'bower_components').replace('./', '').strip('/')
                    write('    .bowerrc detected, ignoring ' + bower_components)
                except Exception as e:
                    write('    .bowerrc parsing error: ' + str(e))

            # Find reports
            # ------------
            write('    Seaching for reports')
            for _root, dirs, files in os.walk(root):
                # need to replace('\\', '/') for Windows
                if not ignored_path(_root.replace('\\', '/')) and bower_components not in _root.replace('\\', '/'):
                    # add data to tboc
                    for filepath in files:
                        fullpath = opj(_root, filepath)
                        if not codecov.file and is_report(fullpath.replace('\\', '/')) and not ignored_report(fullpath.replace('\\', '/')):
                            # found report
                            reports.append(read(fullpath))

        # Read Reports
        # ------------
        if codecov.file:
            write('    Targeting specific files')
            reports.extend(filter(bool, map(read, codecov.file)))

        else:
            # Call `coverage xml` when .coverage exists
            # -----------------------------------------
            # Ran from current directory
            if os.path.exists(opj(os.getcwd(), '.coverage')) and not os.path.exists(opj(os.getcwd(), 'coverage.xml')):
                write('    Generating coverage xml reports for Python')
                # using `-i` to ignore "No source for code" error
                try_to_run('coverage xml -i')
                reports.append(read(opj(os.getcwd(), 'coverage.xml')))

        reports = list(filter(bool, reports))
        assert len(reports) > 0, "No coverage report found"

        # Storing Environment
        # -------------------
        env = ''
        if codecov.env:
            write('==> Appending environment variables')
            for k in codecov.env:
                write('    + ' + k)

            env = '\n'.join(["%s=%s" % (k, os.getenv(k, '')) for k in codecov.env]) + '\n<<<<<< ENV'

        # join reports together
        reports = '\n'.join((env, (toc or ''), '<<<<<< network',
                             '\n<<<<<< EOF\n'.join(reports),
                             '<<<<<< EOF'))

        query['package'] = "py" + VERSION
        urlargs = (urlencode(dict([(k, v.strip()) for k, v in query.items() if v not in ('', None)])))

        if codecov.dump:
            write('-------------------- Debug --------------------')
            write(reports)
            write('--------------------  EOF  --------------------')
            result = None
        else:
            write('==> Uploading')
            write('    .url ' + codecov.url)
            write('    .query ' + urlargs)

            s3 = None
            try:
                res = requests.post('%s/upload/v3?%s' % (codecov.url, urlargs))
                assert res.status_code == 200
                res = res.text.strip().split()
                result, upload_url = res[0], res[1]

                s3 = requests.put(upload_url, data=reports, headers={'Content-Type': 'plain/text', 'x-amz-acl': 'public-read'})
                assert s3.status_code == 200
                write('    ' + result)

            except AssertionError:
                write('    Direct to s3 failed. Using backup v2 endpoint.')
                # just incase, try traditional upload
                res = requests.post('%s/upload/v2?%s' % (codecov.url, urlargs),
                                    data='\n'.join((reports, s3.reason if s3 else '', s3.text if s3 else '')),
                                    headers={"Accept": "text/plain"})
                res.raise_for_status()

                write('    ' + res.text)
                res.raise_for_status()
                result = res.text

    except AssertionError as e:
        write('Error: ' + str(e))
        if kwargs.get('debug'):
            raise

        write('')
        # detect language
        if language:
            write('Tip: See an example %s repo: https://github.com/codecov/example-%s' % (language, language))
        else:
            write('Tip: See all example repositories: https://github.com/codecov?query=example')

        write('Support channels:', 'green')
        write('  Email:   hello@codecov.io\n'
              '  Gitter:  https://gitter.im/codecov/support\n'
              '  Twitter: @codecov\n')
        sys.exit(0 if codecov.no_fail else 1)

    else:
        if kwargs.get('debug'):
            return dict(reports=reports, codecov=codecov, query=query, urlargs=urlargs, result=result)


if __name__ == '__main__':
    main()
