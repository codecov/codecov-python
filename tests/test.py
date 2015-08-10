import os
import sys
import pickle
import requests
import itertools
from json import loads
from ddt import ddt, data
import unittest2 as unittest

import codecov


jacoco_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
<!DOCTYPE report PUBLIC "-//JACOCO//DTD Report 1.0//EN" "report.dtd">
<report name="JaCoCo Maven plug-in example for Java project">
    <sessioninfo id="Steves-MBP.local-b048b758" start="1411925087600" dump="1411925088117" />
    <package name="org/jacoco/examples/maven/java">
        <class name="org/jacoco/examples/maven/java/HelloWorld">
            <method name="&lt;init&gt;" desc="()V" line="3">
                <counter type="INSTRUCTION" missed="0" covered="3" />
                <counter type="LINE" missed="0" covered="1" />
                <counter type="COMPLEXITY" missed="0" covered="1" />
                <counter type="METHOD" missed="0" covered="1" />
            </method>
            <method name="getMessage" desc="(Z)Ljava/lang/String;" line="6">
                <counter type="INSTRUCTION" missed="2" covered="4" />
                <counter type="BRANCH" missed="1" covered="1" />
                <counter type="LINE" missed="1" covered="2" />
                <counter type="COMPLEXITY" missed="1" covered="1" />
                <counter type="METHOD" missed="0" covered="1" />
            </method>
            <counter type="INSTRUCTION" missed="2" covered="7" />
            <counter type="BRANCH" missed="1" covered="1" />
            <counter type="LINE" missed="1" covered="3" />
            <counter type="COMPLEXITY" missed="1" covered="2" />
            <counter type="METHOD" missed="0" covered="2" />
            <counter type="CLASS" missed="0" covered="1" />
        </class>
        <sourcefile name="HelloWorld.java">
            <line nr="3" mi="0" ci="3" mb="0" cb="0" />
            <line nr="6" mi="0" ci="2" mb="1" cb="1" />
            <line nr="7" mi="2" ci="0" mb="0" cb="0" />
            <line nr="9" mi="0" ci="2" mb="0" cb="0" />
            <line nr="10" mi="0" ci="2" mb="0" cb="2" />
            <counter type="INSTRUCTION" missed="2" covered="7" />
            <counter type="BRANCH" missed="1" covered="1" />
            <counter type="LINE" missed="1" covered="3" />
            <counter type="COMPLEXITY" missed="1" covered="2" />
            <counter type="METHOD" missed="0" covered="2" />
            <counter type="CLASS" missed="0" covered="1" />
        </sourcefile>
        <sourcefile name="HelloWorld.java">
            <counter type="INSTRUCTION" missed="2" covered="7" />
            <counter type="BRANCH" missed="1" covered="1" />
            <counter type="LINE" missed="1" covered="3" />
            <counter type="COMPLEXITY" missed="1" covered="2" />
            <counter type="METHOD" missed="0" covered="2" />
            <counter type="CLASS" missed="0" covered="1" />
        </sourcefile>
        <counter type="INSTRUCTION" missed="2" covered="7" />
        <counter type="BRANCH" missed="1" covered="1" />
        <counter type="LINE" missed="1" covered="3" />
        <counter type="COMPLEXITY" missed="1" covered="2" />
        <counter type="METHOD" missed="0" covered="2" />
        <counter type="CLASS" missed="0" covered="1" />
    </package>
    <counter type="INSTRUCTION" missed="2" covered="7" />
    <counter type="BRANCH" missed="1" covered="1" />
    <counter type="LINE" missed="1" covered="3" />
    <counter type="COMPLEXITY" missed="1" covered="2" />
    <counter type="METHOD" missed="0" covered="2" />
    <counter type="CLASS" missed="0" covered="1" />
</report>
"""


@ddt
class TestUploader(unittest.TestCase):
    maxDiff = None
    here = os.path.dirname(__file__)
    bowerrc = os.path.join(os.path.dirname(__file__), '../.bowerrc')
    token = os.path.join(os.path.dirname(__file__), '../.token')
    jacoco = os.path.join(os.path.dirname(__file__), '../jacoco.xml')
    filepath = os.path.join(os.path.dirname(__file__), '../coverage.xml')
    coverage = os.path.join(os.path.dirname(__file__), '../.coverage')
    defaults = dict(commit='a', branch='a', token='a')

    @classmethod
    def setUpClass(self):
        self._env = os.environ.copy()

    @classmethod
    def tearDownClass(self):
        os.environ = self._env

    def setUp(self):
        # set all environ back
        os.environ['CI'] = "true"
        for key in ("TRAVIS", "TRAVIS_BRANCH", "TRAVIS_COMMIT", "TRAVIS_BUILD_DIR", "TRAVIS_JOB_ID", "TRAVIS_PULL_REQUEST",
                    "CI_NAME", "CI_BRANCH", "CI_COMMIT_ID", "SNAP_CI", "SHIPPABLE",
                    "CI_BUILD_NUMBER", "MAGNUM", "CI_COMMIT", "APPVEYOR_ACCOUNT_NAME", "APPVEYOR_PROJECT_SLUG", "APPVEYOR_PULL_REQUEST_NUMBER",
                    "SNAP_UPSTREAM_BRANCH", "SNAP_BRANCH", "SNAP_PIPELINE_COUNTER", "SNAP_PULL_REQUEST_NUMBER", "SNAP_COMMIT", "SNAP_UPSTREAM_COMMIT",
                    "CIRCLECI", "CIRCLE_BRANCH", "CIRCLE_ARTIFACTS", "CIRCLE_SHA1", "CIRCLE_NODE_INDEX", "CIRCLE_PR_NUMBER",
                    "SEMAPHORE", "BRANCH_NAME", "SEMAPHORE_PROJECT_DIR", "REVISION",
                    "DRONE", "DRONE_BRANCH", "DRONE_BUILD_DIR", "DRONE_COMMIT", "JENKINS_URL",
                    "GIT_BRANCH", "GIT_COMMIT", "WORKSPACE", "BUILD_NUMBER", "CI_BUILD_URL", "SEMAPHORE_REPO_SLUG", "SEMAPHORE_CURRENT_THREAD",
                    "DRONE_BUILD_URL", "TRAVIS_REPO_SLUG", "CODECOV_TOKEN", "APPVEYOR", "APPVEYOR_REPO_BRANCH",
                    "APPVEYOR_BUILD_VERSION", "APPVEYOR_JOB_ID", "APPVEYOR_REPO_NAME", "APPVEYOR_REPO_COMMIT", "WERCKER_GIT_BRANCH",
                    "WERCKER_MAIN_PIPELINE_STARTED", "WERCKER_GIT_OWNER", "WERCKER_GIT_REPOSITORY",
                    "CI_BUILD_REF_NAME", "CI_BUILD_ID", "CI_BUILD_REPO", "CI_PROJECT_DIR", "CI_BUILD_REF", "CI_SERVER_NAME",
                    "ghprbActualCommit", "ghprbSourceBranch", "ghprbPullId", "WERCKER_GIT_COMMIT"):
            os.environ[key] = ""

    def tearDown(self):
        if os.path.exists(self.filepath):
            os.remove(self.filepath)
        if os.path.exists(self.coverage):
            os.remove(self.coverage)
        if os.path.exists(self.jacoco):
            os.remove(self.jacoco)
        if os.path.exists(self.bowerrc):
            os.remove(self.bowerrc)

    def set_env(self, **kwargs):
        for key in kwargs:
            os.environ[key] = str(kwargs[key])

    def run_cli(self, dump=True, *args, **kwargs):
        inline = list(itertools.chain(*[['--%s' % key, str(value)] for key, value in kwargs.items() if value]))
        if dump:
            inline.append('--dump')
        inline.extend(args)
        return codecov.main(*inline, debug=True)

    def fake_report(self):
        with open(self.filepath, 'w+') as f:
            f.write('__data__')

    @data('vendor', 'js/generated/coverage', '__pycache__', 'coverage/instrumented',
          'build/lib', 'htmlcov', '.egg-info', '.git', '.tox', 'venv', '.venv-python-2.7')
    def test_ignored_path(self, path):
        self.assertTrue(bool(codecov.ignored_path('/home/ubuntu/' + path)), path + ' should be ignored')
        self.assertTrue(bool(codecov.ignored_path('/home/ubuntu/' + path + '/more paths')), path + ' should be ignored')

    @data('.pyc', '.coverage', '.sh', '.egg', 'test_this_coverage.txt')
    def test_ignored_file(self, path):
        self.assertTrue(bool(codecov.ignored_file('/home/file/name' + path)), path + ' should be ignored')

    @data('coverage.xml', 'jacoco.xml', 'jacocoTestResults.xml', 'coverage.txt',
          'gcov.lst', 'cov.gcov', 'info.lcov', 'clover.xml', 'cobertura.xml',
          'luacov.report.out', 'gcov.info', 'nosetests.xml')
    def test_is_report(self, path):
        self.assertFalse(bool(codecov.ignored_report('/home/file/' + path)), path + ' should not be ignored')
        self.assertTrue(bool(codecov.is_report('/home/file/' + path)), path + ' should be a report')

    @data('.coverage.worker10', 'coverage.jade', 'include.lst', 'inputFiles.lst',
          'createdFiles.lst', 'scoverage.measurements.blackandwhite.xml', 'test_hello_coverage.txt',
          'conftest_blackwhite.c.gcov')
    def test_ignore_report(self, path):
        self.assertTrue(bool(codecov.ignored_report('/home/file/' + path)), path + ' should be ignored')

    def test_command(self):
        try:
            self.run_cli(True, '--help')
        except SystemExit as e:
            self.assertEqual(str(e), '0')
        else:
            raise Exception("help not shown")

    def test_exits(self):
        try:
            sys.argv = ['']
            codecov.main()
        except SystemExit as e:
            self.assertEqual(str(e), '1')
        else:
            raise Exception("did not exit")

    def test_returns_none(self):
        with open(self.filepath, 'w+') as f:
            f.write('coverage data')
        sys.argv = ['', '--commit=8ed84d96bc225deff66605486180cd555366806b',
                    '--branch=master',
                    '--token=473c8c5b-10ee-4d83-86c6-bfd72a185a27']
        self.assertEqual(codecov.main(), None)

    def test_send(self):
        with open(self.filepath, 'w+') as f:
            f.write('coverage data')
        res = self.run_cli(False, commit='a'*40, branch='master', token='473c8c5b-10ee-4d83-86c6-bfd72a185a27')
        self.assertIn('Uploaded successfully', res['reports'])

    def test_send_error(self):
        with open(self.filepath, 'w+') as f:
            f.write('coverage data')
        try:
            self.run_cli(False, token='not-a-token', commit='a'*40, branch='master')
        except requests.exceptions.HTTPError:
            pass
        else:
            raise Exception('400 never raised')

    def test_required(self):
        self.set_env(JENKINS_URL='hello')  # this is so we dont get branch for local git
        res = self.run_cli()
        self.assertEqual(res['reports'], 'Branch argument is missing. Please specify via --branch=:name')
        self.assertEqual(res['url'], None)

        res = self.run_cli(branch='master')
        self.assertEqual(res['reports'], 'Commit sha is missing. Please specify via --commit=:sha')
        self.assertEqual(res['url'], None)

        res = self.run_cli(branch='master', commit="sha")
        self.assertEqual(res['reports'], 'Missing repository upload token')
        self.assertEqual(res['url'], None)

    def test_read_token_file(self):
        with open(self.token, 'w+') as f:
            f.write('a')
        with open(self.filepath, 'w+') as f:
            f.write('coverage data')
        res = self.run_cli(token='@'+self.token, commit='a', branch='b')
        self.assertIn('token=a', res['url'])

    def test_bowerrc(self):
        with open(self.bowerrc, 'w+') as f:
            f.write('{"directory": "tests"}')
        with open(self.filepath, 'w+') as f:
            f.write('coverage data')
        res = self.run_cli(**self.defaults)
        self.assertNotIn('tests/test.py', res['reports'])

    def test_bowerrc_none(self):
        with open(self.bowerrc, 'w+') as f:
            f.write('{"other_key": "tests"}')
        with open(self.filepath, 'w+') as f:
            f.write('coverage data')
        res = self.run_cli(**self.defaults)
        self.assertIn('tests/test.py', res['reports'])

    def test_discovers(self):
        with open(self.jacoco, 'w+') as f:
            f.write(jacoco_xml)
        with open(self.filepath, 'w+') as f:
            f.write('coverage data')
        res = self.run_cli(**self.defaults)
        report = sorted(res['reports'].split('<<<<<< EOF\n'))
        self.assertEqual(report[0].splitlines()[0], '# path=coverage.xml')
        self.assertEqual(report[0].splitlines()[1], 'coverage data')
        self.assertEqual(report[1].splitlines()[0], '# path=jacoco.xml')
        self.assertEqual(loads(report[1].splitlines()[1]), {"coverage": {"org/jacoco/examples/maven/java/HelloWorld.java": {"3": 3, "9": 2, "7": 0, "6": "1/2", "10": "2/2"}}})
        self.assertIn('tests/test.py', report[2].splitlines())

    def test_jacoco(self):
        with open(self.jacoco, 'w+') as f:
            f.write(jacoco_xml)
        res = self.run_cli(file='jacoco.xml', **self.defaults)
        report = res['reports'].split('<<< EOF\n')[1].splitlines()
        self.assertEqual(report[0], '# path=jacoco.xml')
        self.assertEqual(loads(report[1]), {"coverage": {"org/jacoco/examples/maven/java/HelloWorld.java": {"3": 3, "9": 2, "7": 0, "6": "1/2", "10": "2/2"}}})

    def test_not_jacoco(self):
        with open(self.filepath, 'w+') as f:
            f.write('<data>')
        res = self.run_cli(file='coverage.xml', **self.defaults)
        res = res['reports'].split('<<< EOF\n')[1].splitlines()
        self.assertEqual(res[0], '# path=coverage.xml')
        self.assertEqual(res[1], '<data>')

    def test_run_coverage(self):
        self.skipTest('Not sure how to pull off atm')
        with open(self.coverage, 'w+') as f:
            f.write(pickle.dumps())
        res = self.run_cli(**self.defaults)
        self.assertIn('<?xml version="1.0" ?>', res['reports'])

    def test_run_coverage_fails(self):
        with open(self.coverage, 'w+') as f:
            f.write('bad data')
        res = self.run_cli(**self.defaults)
        self.assertEqual(res['reports'], 'No coverage report found')
        self.assertEqual(res['url'], None)

    def test_include_env(self):
        self.set_env(HELLO='WORLD')
        self.fake_report()
        res = self.run_cli(env='HELLO', file=self.filepath, **self.defaults)
        self.assertIn('HELLO=WORLD', res['reports'])

    def test_none_found(self):
        res = self.run_cli(**self.defaults)
        self.assertEqual(res['reports'], 'No coverage report found')
        self.assertEqual(res['url'], None)

    def test_ci_jenkins(self):
        self.set_env(BUILD_URL='https://....',
                     JENKINS_URL='https://....',
                     GIT_BRANCH='master',
                     GIT_COMMIT='c739768fcac68144a3a6d82305b9c4106934d31a',
                     WORKSPACE=self.here,
                     BUILD_NUMBER='41',
                     CODECOV_TOKEN='token')
        res = self.run_cli()
        self.assertEqual(res['query']['service'], 'jenkins')
        self.assertEqual(res['query']['commit'], 'c739768fcac68144a3a6d82305b9c4106934d31a')
        self.assertEqual(res['query']['build'], '41')
        self.assertEqual(res['query']['build_url'], 'https://....')
        self.assertEqual(res['query']['pr'], '')
        self.assertEqual(res['query']['branch'], 'master')
        self.assertEqual(res['codecov'].token, 'token')

    def test_ci_jenkins_env(self):
        self.set_env(JENKINS_URL='https://....',
                     BUILD_URL='https://....',
                     ghprbSourceBranch='master',
                     ghprbActualCommit='c739768fcac68144a3a6d82305b9c4106934d31a',
                     ghprbPullId='1',
                     WORKSPACE=self.here,
                     BUILD_NUMBER='41',
                     CODECOV_TOKEN='token')
        res = self.run_cli()
        self.assertEqual(res['query']['service'], 'jenkins')
        self.assertEqual(res['query']['commit'], 'c739768fcac68144a3a6d82305b9c4106934d31a')
        self.assertEqual(res['query']['build'], '41')
        self.assertEqual(res['query']['build_url'], 'https://....')
        self.assertEqual(res['query']['pr'], '1')
        self.assertEqual(res['query']['branch'], 'master')
        self.assertEqual(res['codecov'].token, 'token')

    def test_ci_travis(self):
        self.set_env(TRAVIS="true",
                     TRAVIS_BRANCH="master",
                     TRAVIS_COMMIT="c739768fcac68144a3a6d82305b9c4106934d31a",
                     TRAVIS_BUILD_DIR=self.here,
                     TRAVIS_REPO_SLUG='owner/repo',
                     TRAVIS_JOB_ID="33116958",
                     TRAVIS_JOB_NUMBER="4.1")
        res = self.run_cli()
        self.assertEqual(res['query']['service'], 'travis')
        self.assertEqual(res['query']['commit'], 'c739768fcac68144a3a6d82305b9c4106934d31a')
        self.assertEqual(res['query']['build'], '4.1')
        self.assertEqual(res['query']['pr'], '')
        self.assertEqual(res['query']['slug'], 'owner/repo')
        self.assertEqual(res['query']['branch'], 'master')
        self.assertEqual(res['codecov'].token, '')

    def test_ci_codeship(self):
        self.set_env(CI_NAME='codeship',
                     CI_BRANCH='master',
                     CI_BUILD_NUMBER='20',
                     CI_BUILD_URL='https://codeship.io/build/1',
                     CI_COMMIT_ID='743b04806ea677403aa2ff26c6bdeb85005de658',
                     CODECOV_TOKEN='token')
        res = self.run_cli()
        self.assertEqual(res['query']['service'], 'codeship')
        self.assertEqual(res['query']['commit'], '743b04806ea677403aa2ff26c6bdeb85005de658')
        self.assertEqual(res['query']['build'], '20')
        self.assertEqual(res['query']['build_url'], 'https://codeship.io/build/1')
        self.assertEqual(res['query']['pr'], '')
        self.assertEqual(res['query']['branch'], 'master')
        self.assertEqual(res['codecov'].token, 'token')

    def test_ci_circleci(self):
        self.set_env(CIRCLECI='true',
                     CIRCLE_BUILD_NUM='57',
                     CIRCLE_NODE_INDEX='1',
                     CIRCLE_PR_NUMBER='1',
                     CIRCLE_BRANCH='master',
                     CIRCLE_PROJECT_USERNAME='owner',
                     CIRCLE_PROJECT_REPONAME='repo',
                     CIRCLE_SHA1='d653b934ed59c1a785cc1cc79d08c9aaa4eba73b')
        res = self.run_cli()
        self.assertEqual(res['query']['service'], 'circleci')
        self.assertEqual(res['query']['commit'], 'd653b934ed59c1a785cc1cc79d08c9aaa4eba73b')
        self.assertEqual(res['query']['build'], '57.1')
        self.assertEqual(res['query']['pr'], '1')
        self.assertEqual(res['query']['slug'], 'owner/repo')
        self.assertEqual(res['query']['branch'], 'master')

    def test_ci_semaphore(self):
        self.set_env(SEMAPHORE='true',
                     BRANCH_NAME='master',
                     SEMAPHORE_BUILD_NUMBER='10',
                     SEMAPHORE_CURRENT_THREAD='1',
                     SEMAPHORE_REPO_SLUG='owner/repo',
                     REVISION='743b04806ea677403aa2ff26c6bdeb85005de658',
                     CODECOV_TOKEN='token')
        res = self.run_cli()
        self.assertEqual(res['query']['service'], 'semaphore')
        self.assertEqual(res['query']['commit'], '743b04806ea677403aa2ff26c6bdeb85005de658')
        self.assertEqual(res['query']['build'], '10.1')
        self.assertEqual(res['query']['slug'], 'owner/repo')
        self.assertEqual(res['query']['branch'], 'master')

    def test_ci_snap(self):
        self.set_env(SNAP_BRANCH='master',
                     SNAP_CI='true',
                     SNAP_PIPELINE_COUNTER='10',
                     SNAP_PULL_REQUEST_NUMBER='10',
                     SNAP_COMMIT='743b04806ea677403aa2ff26c6bdeb85005de658',
                     CODECOV_TOKEN='token')
        res = self.run_cli()
        self.assertEqual(res['query']['service'], 'snap')
        self.assertEqual(res['query']['commit'], '743b04806ea677403aa2ff26c6bdeb85005de658')
        self.assertEqual(res['query']['build'], '10')
        self.assertEqual(res['query']['pr'], '10')
        self.assertEqual(res['codecov'].token, 'token')

    def test_ci_drone(self):
        self.set_env(DRONE='true',
                     DRONE_BUILD_NUMBER='10',
                     DRONE_BRANCH='master',
                     DRONE_BUILD_URL='https://drone.io/github/builds/1',
                     DRONE_BUILD_DIR=self.here,
                     DRONE_COMMIT='743b04806ea677403aa2ff26c6bdeb85005de658',
                     CODECOV_TOKEN='token')
        res = self.run_cli()
        self.assertEqual(res['query']['service'], 'drone.io')
        self.assertEqual(res['query']['commit'], '743b04806ea677403aa2ff26c6bdeb85005de658')
        self.assertEqual(res['query']['build'], '10')
        self.assertEqual(res['query']['build_url'], 'https://drone.io/github/builds/1')
        self.assertEqual(res['codecov'].token, 'token')

    def test_ci_shippable(self):
        self.set_env(SHIPPABLE='true',
                     BUILD_NUMBER='10',
                     REPO_NAME='owner/repo',
                     BRANCH='master',
                     BUILD_URL='https://shippable.com/...',
                     COMMIT='743b04806ea677403aa2ff26c6bdeb85005de658',
                     CODECOV_TOKEN='token')
        res = self.run_cli()
        self.assertEqual(res['query']['service'], 'shippable')
        self.assertEqual(res['query']['commit'], '743b04806ea677403aa2ff26c6bdeb85005de658')
        self.assertEqual(res['query']['build'], '10')
        self.assertEqual(res['query']['slug'], 'owner/repo')
        self.assertEqual(res['query']['build_url'], 'https://shippable.com/...')
        self.assertEqual(res['codecov'].token, 'token')

    def test_ci_appveyor(self):
        self.set_env(APPVEYOR='True',
                     CI='True',
                     APPVEYOR_JOB_ID='9r2qufuu8',
                     APPVEYOR_BUILD_VERSION='1.2.3',
                     APPVEYOR_ACCOUNT_NAME='owner',
                     APPVEYOR_PROJECT_SLUG='repo',
                     APPVEYOR_PULL_REQUEST_NUMBER='1',
                     APPVEYOR_REPO_BRANCH='master',
                     APPVEYOR_REPO_NAME='owner/repo',
                     APPVEYOR_REPO_COMMIT='d653b934ed59c1a785cc1cc79d08c9aaa4eba73b',
                     CODECOV_TOKEN='token')
        res = self.run_cli()
        self.assertEqual(res['query']['service'], 'appveyor')
        self.assertEqual(res['query']['commit'], 'd653b934ed59c1a785cc1cc79d08c9aaa4eba73b')
        self.assertEqual(res['query']['job'], 'owner/repo/1.2.3')
        self.assertEqual(res['query']['build'], '9r2qufuu8')
        self.assertEqual(res['query']['slug'], 'owner/repo')
        self.assertEqual(res['query']['pr'], '1')
        self.assertEqual(res['codecov'].token, 'token')

    def test_ci_wercker(self):
        self.set_env(WERCKER_GIT_BRANCH='master',
                     WERCKER_MAIN_PIPELINE_STARTED='1399372237',
                     WERCKER_GIT_OWNER='owner',
                     WERCKER_GIT_REPOSITORY='repo',
                     WERCKER_GIT_COMMIT='d653b934ed59c1a785cc1cc79d08c9aaa4eba73b',
                     CODECOV_TOKEN='token')
        res = self.run_cli()
        self.assertEqual(res['query']['service'], 'wercker')
        self.assertEqual(res['query']['commit'], 'd653b934ed59c1a785cc1cc79d08c9aaa4eba73b')
        self.assertEqual(res['query']['build'], '1399372237')
        self.assertEqual(res['query']['slug'], 'owner/repo')
        self.assertEqual(res['codecov'].token, 'token')

    def test_ci_magnum(self):
        self.set_env(CI_BRANCH='master',
                     CI_BUILD_NUMBER='1399372237',
                     MAGNUM='true',
                     CI='true',
                     CI_COMMIT='d653b934ed59c1a785cc1cc79d08c9aaa4eba73b',
                     CODECOV_TOKEN='token')
        res = self.run_cli()
        self.assertEqual(res['query']['service'], 'magnum')
        self.assertEqual(res['query']['commit'], 'd653b934ed59c1a785cc1cc79d08c9aaa4eba73b')
        self.assertEqual(res['query']['build'], '1399372237')
        self.assertEqual(res['codecov'].token, 'token')

    def test_ci_gitlab(self):
        self.set_env(CI_BUILD_REF_NAME='master',
                     CI_BUILD_ID='1399372237',
                     CI_BUILD_REPO='https://gitlab.com/owner/repo.git',
                     CI_SERVER_NAME='GitLab CI',
                     CI_PROJECT_DIR=self.here,
                     CI_BUILD_REF='d653b934ed59c1a785cc1cc79d08c9aaa4eba73b',
                     CODECOV_TOKEN='token')
        res = self.run_cli()
        self.assertEqual(res['query']['service'], 'gitlab')
        self.assertEqual(res['query']['commit'], 'd653b934ed59c1a785cc1cc79d08c9aaa4eba73b')
        self.assertEqual(res['query']['build'], '1399372237')
        self.assertEqual(res['query']['slug'], 'owner/repo')
        self.assertEqual(res['codecov'].token, 'token')

    def test_ci_none(self):
        self.set_env(CODECOV_TOKEN='token')
        res = self.run_cli(build=10,
                           commit='d653b934ed59c1a785cc1cc79d08c9aaa4eba73b',
                           slug='owner/repo',
                           token='token')
        self.assertEqual(res['query'].get('service'), None)
        self.assertEqual(res['query']['commit'], 'd653b934ed59c1a785cc1cc79d08c9aaa4eba73b')
        self.assertEqual(res['query']['build'], '10')
        self.assertEqual(res['query']['slug'], 'owner/repo')
        self.assertEqual(res['codecov'].token, 'token')
