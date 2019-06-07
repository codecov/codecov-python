import os
import sys
import pickle
import itertools
from ddt import ddt, data
from mock import patch, Mock
import unittest

import subprocess

import codecov


@ddt
class TestUploader(unittest.TestCase):
    maxDiff = None
    here = os.path.dirname(__file__)
    bowerrc = os.path.join(os.path.dirname(__file__), '../.bowerrc')
    token = os.path.join(os.path.dirname(__file__), '../.token')
    jacoco = os.path.join(os.path.dirname(__file__), '../jacoco.xml')
    filepath = os.path.join(os.path.dirname(__file__), 'coverage.xml')
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
                    "CI_NAME", "CI_BRANCH", "CI_COMMIT_ID", "SHIPPABLE",
                    "CI_BUILD_NUMBER", "MAGNUM", "CI_COMMIT", "APPVEYOR_ACCOUNT_NAME", "APPVEYOR_PROJECT_SLUG", "APPVEYOR_PULL_REQUEST_NUMBER",
                    "CIRCLECI", "CIRCLE_BRANCH", "CIRCLE_ARTIFACTS", "CIRCLE_SHA1", "CIRCLE_NODE_INDEX", "CIRCLE_PR_NUMBER",
                    "SEMAPHORE", "BRANCH_NAME", "SEMAPHORE_PROJECT_DIR", "REVISION",
                    "BUILDKITE", "BUILDKITE_BUILD_NUMBER", "BUILDKITE_JOB_ID", "BUILDKITE_BRANCH", "BUILDKITE_PROJECT_SLUG", "BUILDKITE_COMMIT",
                    "DRONE", "DRONE_BRANCH", "DRONE_BUILD_DIR", "JENKINS_URL", "TRAVIS_TAG",
                    "GIT_BRANCH", "GIT_COMMIT", "WORKSPACE", "BUILD_NUMBER", "CI_BUILD_URL", "SEMAPHORE_REPO_SLUG", "SEMAPHORE_CURRENT_THREAD",
                    "DRONE_BUILD_LINK", "TRAVIS_REPO_SLUG", "CODECOV_TOKEN", "APPVEYOR", "APPVEYOR_REPO_BRANCH",
                    "APPVEYOR_BUILD_VERSION", "APPVEYOR_JOB_ID", "APPVEYOR_REPO_NAME", "APPVEYOR_REPO_COMMIT", "WERCKER_GIT_BRANCH",
                    "WERCKER_MAIN_PIPELINE_STARTED", "WERCKER_GIT_OWNER", "WERCKER_GIT_REPOSITORY",
                    "CI_BUILD_REF_NAME", "CI_BUILD_ID", "CI_BUILD_REPO", "CI_PROJECT_DIR", "CI_BUILD_REF", "CI_SERVER_NAME",
                    "ghprbActualCommit", "ghprbSourceBranch", "ghprbPullId", "WERCKER_GIT_COMMIT", "CHANGE_ID"):
            os.environ[key] = ""

    def tearDown(self):
        self.delete(self.filepath, self.coverage, self.jacoco, self.bowerrc)
        self.delete('hello', 'hello.c', 'hello.gcda', 'hello.c.gcov', 'hello.gcno')

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

    def delete(self, *paths):
        for path in paths:
            if os.path.exists(path):
                os.remove(path)
            path = os.path.join(os.path.dirname(__file__), '../', path)
            if os.path.exists(path):
                os.remove(path)

    @data('vendor', 'node_modules', 'js/generated/coverage', '__pycache__', 'coverage/instrumented',
          'build/lib', 'htmlcov', '.egg-info', '.git', '.tox', 'venv', '.venv-python-2.7')
    def test_ignored_path(self, path):
        self.assertTrue(bool(codecov.ignored_path('/home/ubuntu/' + path)), path + ' should be ignored')
        self.assertTrue(bool(codecov.ignored_path('/home/ubuntu/' + path + '/more paths')), path + ' should be ignored')

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

    def test_exits_0(self):
        try:
            sys.argv = ['']
            codecov.main()
        except SystemExit as e:
            self.assertEqual(str(e), '0')
        else:
            raise Exception("did not exit")

    def test_exits_1(self):
        try:
            sys.argv = ['']
            codecov.main('--required')
        except SystemExit as e:
            self.assertEqual(str(e), '1')
        else:
            raise Exception("did not exit")

    @unittest.skipIf(os.getenv('CI') == "True" and os.getenv('APPVEYOR') == 'True', 'Skip AppVeyor CI test')
    def test_returns_none(self):
        with patch('requests.post') as post:
            with patch('requests.put') as put:
                post.return_value = Mock(status_code=200, text='target\ns3')
                put.return_value = Mock(status_code=200)
                with open(self.filepath, 'w+') as f:
                    f.write('coverage data')
                sys.argv = ['', '--commit=8ed84d96bc225deff66605486180cd555366806b',
                            '--branch=master',
                            '--token=473c8c5b-10ee-4d83-86c6-bfd72a185a27']
                self.assertEqual(codecov.main(), None)
                assert post.called and put.called

    @unittest.skipIf(os.getenv('CI') == "True" and os.getenv('APPVEYOR') == 'True', 'Skip AppVeyor CI test')
    def test_send(self):
        with patch('requests.post') as post:
            with patch('requests.put') as put:
                post.return_value = Mock(status_code=200, text='target\ns3')
                put.return_value = Mock(status_code=200)
                with open(self.filepath, 'w+') as f:
                    f.write('coverage data')
                res = self.run_cli(False, commit='a'*40, branch='master', token='<token>')
                self.assertEqual(res['result'].strip(), 'target')
                assert 'https://codecov.io/upload/v4?' in post.call_args[0][0]
                assert 'commit=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa' in post.call_args[0][0]
                assert 'token=%3Ctoken%3E' in post.call_args[0][0]
                assert 'branch=master' in post.call_args[0][0]
                assert u'tests/test.py'.encode("utf-8") in put.call_args[1]['data']

    def test_send_error(self):
        with patch('requests.post') as post:
            post.return_value = Mock(status_code=400, text='error')
            with open(self.filepath, 'w+') as f:
                f.write('coverage data')
            try:
                self.run_cli(False, token='not-a-token', commit='a'*40, branch='master')
            except Exception:
                pass
            else:
                raise Exception('400 never raised')

    @data((dict(commit='sha'), 'Missing repository upload token'), )
    def test_require_branch(self, dd):
        (kwargs, reason) = dd
        # this is so we dont get branch for local git
        self.set_env(JENKINS_URL='hello')
        try:
            self.run_cli(**kwargs)
        except AssertionError as e:
            self.assertEqual(str(e), reason)
        else:
            raise Exception("Did not raise AssertionError")

    @unittest.skipIf(os.getenv('CI') == "True" and os.getenv('APPVEYOR') == 'True', 'Skip AppVeyor CI test')
    def test_read_token_file(self):
        with open(self.token, 'w+') as f:
            f.write('a')
        with open(self.filepath, 'w+') as f:
            f.write('coverage data')
        res = self.run_cli(token='@'+self.token, commit='a', branch='b')
        self.assertIn('token=a', res['urlargs'])

    def test_bowerrc(self):
        with open(self.bowerrc, 'w+') as f:
            f.write('{"directory": "tests"}')
        with open(self.filepath, 'w+') as f:
            f.write('coverage data')
        try:
            self.run_cli(**self.defaults)
        except AssertionError as e:
            self.assertEqual(str(e),  "No coverage report found")
        else:
            raise Exception("Did not raise AssertionError")

    def test_disable_search(self):
        self.fake_report()
        try:
            self.run_cli(disable='search', token='a', branch='b', commit='c')
        except AssertionError as e:
            self.assertEqual(str(e), "No coverage report found")
        else:
            raise Exception("Did not raise AssertionError")

    @unittest.skipIf(os.getenv('CI') == "True" and os.getenv('APPVEYOR') == 'True', 'Skip AppVeyor CI test')
    def test_prefix(self):
        self.fake_report()
        res = self.run_cli(prefix='/foo/bar/', dump=True, token='a', branch='b', commit='c')
        assert '\nfoo/bar/.gitignore' in res['reports']

    def write_c(self):
        c = '\n'.join(('#include <stdio.h>',
                       'static int t = 1;'
                       'int main()', '{',
                       'if (t)', 'printf("on this line\\n");',
                       'else', 'printf("but not here\\n");',
                       'return 0;', '}'))
        with open(os.path.join(os.path.dirname(__file__), '../hello.c'), 'w+') as f:
            f.write(c)
        codecov.try_to_run('clang -coverage -O0 hello.c -o hello && ./hello')

    def test_disable_gcov(self):
        if self._env.get('TRAVIS') == 'true':
            self.write_c()
            try:
                self.run_cli(disable='gcov', token='a', branch='b', commit='c')
            except AssertionError as e:
                self.assertEqual(os.path.exists('hello.c.gcov'), False)
                self.assertEqual(str(e), "No coverage report found")
            else:
                raise Exception("Did not raise AssertionError")
        else:
            self.skipTest("Skipped, works on Travis only.")

    def test_gcov(self):
        self.skipTest("Need to fix this test...")
        # if self._env.get('TRAVIS') == 'true':
        #     self.write_c()
        #     output = self.run_cli(token='a', branch='b', commit='c')
        #     self.assertEqual(os.path.exists('hello.c.gcov'), True)
        #     report = output['reports'].split('<<<<<< network\n')[1].splitlines()
        #     self.assertIn('hello.c.gcov', report[0])
        # else:
        #     self.skipTest("Skipped, works on Travis only.")

    def test_disable_detect(self):
        self.set_env(JENKINS_URL='a', GIT_BRANCH='b', GIT_COMMIT='c', CODECOV_TOKEN='d')
        self.fake_report()
        try:
            self.run_cli(disable='detect')
        except AssertionError as e:
            self.assertEqual(str(e), "Commit sha is missing. Please specify via --commit=:sha")
        else:
            raise Exception("Did not raise AssertionError")

    @unittest.skipIf(os.getenv('CI') == "True" and os.getenv('APPVEYOR') == 'True', 'Skip AppVeyor CI test')
    def test_bowerrc_none(self):
        with open(self.bowerrc, 'w+') as f:
            f.write('{"other_key": "tests"}')
        with open(self.filepath, 'w+') as f:
            f.write('coverage data')
        res = self.run_cli(**self.defaults)
        self.assertIn('tests/test.py', res['reports'])

    @unittest.skipIf(os.getenv('CI') == "True" and os.getenv('APPVEYOR') == 'True', 'Skip AppVeyor CI test')
    def test_discovers(self):
        with open(self.jacoco, 'w+') as f:
            f.write('<jacoco></jacoco>')
        with open(self.filepath, 'w+') as f:
            f.write('coverage data')
        res = self.run_cli(**self.defaults)
        self.assertIn('coverage.xml', res['reports'])
        self.assertIn('coverage data', res['reports'])
        self.assertIn('jacoco.xml', res['reports'])
        self.assertIn('<jacoco></jacoco>', res['reports'])

    def test_not_jacoco(self):
        with open(self.filepath, 'w+') as f:
            f.write('<data>')
        res = self.run_cli(file='tests/coverage.xml', **self.defaults)
        res = res['reports'].split('<<<<<< network\n')[1].splitlines()
        self.assertEqual(res[0], '# path=tests/coverage.xml')
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
        try:
            self.run_cli(**self.defaults)
        except AssertionError as e:
            self.assertEqual(str(e), 'No coverage report found')
        else:
            raise Exception("Did not raise AssertionError")

    def test_include_env(self):
        self.set_env(HELLO='WORLD')
        self.fake_report()
        res = self.run_cli(env='HELLO', file=self.filepath, **self.defaults)
        self.assertIn('HELLO=WORLD', res['reports'])

    def test_none_found(self):
        try:
            self.run_cli(**self.defaults)
        except AssertionError as e:
            self.assertEqual(str(e), "No coverage report found")
        else:
            raise Exception("Did not raise AssertionError")

    @unittest.skipUnless(os.getenv('JENKINS_URL'), 'Skip Jenkins CI test')
    def test_ci_jenkins(self):
        self.set_env(BUILD_URL='https://....',
                     JENKINS_URL='https://....',
                     GIT_BRANCH='master',
                     GIT_COMMIT='c739768fcac68144a3a6d82305b9c4106934d31a',
                     BUILD_NUMBER='41',
                     CODECOV_TOKEN='token')
        self.fake_report()
        res = self.run_cli()
        self.assertEqual(res['query']['service'], 'jenkins')
        self.assertEqual(res['query']['commit'], 'c739768fcac68144a3a6d82305b9c4106934d31a')
        self.assertEqual(res['query']['build'], '41')
        self.assertEqual(res['query']['build_url'], 'https://....')
        self.assertEqual(res['query']['pr'], '')
        self.assertEqual(res['query']['branch'], 'master')
        self.assertEqual(res['codecov'].token, 'token')

    @unittest.skipUnless(os.getenv('JENKINS_URL'), 'Skip Jenkins CI test')
    def test_ci_jenkins_env(self):
        self.set_env(JENKINS_URL='https://....',
                     BUILD_URL='https://....',
                     ghprbSourceBranch='master',
                     ghprbActualCommit='c739768fcac68144a3a6d82305b9c4106934d31a',
                     ghprbPullId='1',
                     BUILD_NUMBER='41',
                     CODECOV_TOKEN='token')
        self.fake_report()
        res = self.run_cli()
        self.assertEqual(res['query']['service'], 'jenkins')
        self.assertEqual(res['query']['commit'], 'c739768fcac68144a3a6d82305b9c4106934d31a')
        self.assertEqual(res['query']['build'], '41')
        self.assertEqual(res['query']['build_url'], 'https://....')
        self.assertEqual(res['query']['pr'], '1')
        self.assertEqual(res['query']['branch'], 'master')
        self.assertEqual(res['codecov'].token, 'token')

    @unittest.skipUnless(os.getenv('JENKINS_URL'), 'Skip Jenkins CI test')
    def test_ci_jenkins_blue_ocean(self):
        self.set_env(JENKINS_URL='https://....',
                     BUILD_URL='https://....',
                     BRANCH_NAME='master',
                     CHANGE_ID='1',
                     BUILD_NUMBER='41',
                     CODECOV_TOKEN='token')
        self.fake_report()
        res = self.run_cli()
        self.assertEqual(res['query']['service'], 'jenkins')
        self.assertEqual(res['query']['commit'], codecov.check_output(("git", "rev-parse", "HEAD")))
        self.assertEqual(res['query']['build'], '41')
        self.assertEqual(res['query']['build_url'], 'https://....')
        self.assertEqual(res['query']['pr'], '1')
        self.assertEqual(res['query']['branch'], 'master')
        self.assertEqual(res['codecov'].token, 'token')

    @unittest.skipUnless(os.getenv('CI') == 'true'
                         and os.getenv('TRAVIS') == "true"
                         and os.getenv('SHIPPABLE') != 'true',
                         'Skip Travis CI test')
    def test_ci_travis(self):
        self.set_env(TRAVIS="true",
                     TRAVIS_BRANCH="master",
                     TRAVIS_COMMIT="c739768fcac68144a3a6d82305b9c4106934d31a",
                     TRAVIS_REPO_SLUG='owner/repo',
                     TRAVIS_JOB_ID="33116958",
                     TRAVIS_TAG="v1.1.1",
                     TRAVIS_JOB_NUMBER="4.1")
        self.fake_report()
        res = self.run_cli()
        self.assertEqual(res['query']['service'], 'travis')
        self.assertEqual(res['query']['commit'], 'c739768fcac68144a3a6d82305b9c4106934d31a')
        self.assertEqual(res['query']['build'], '4.1')
        self.assertEqual(res['query']['pr'], '')
        self.assertEqual(res['query']['tag'], 'v1.1.1')
        self.assertEqual(res['query']['slug'], 'owner/repo')
        self.assertEqual(res['query']['branch'], 'master')
        self.assertEqual(res['codecov'].token, '')

    @unittest.skipUnless(os.getenv('CI') == 'true' and os.getenv('CI_NAME') == 'codeship', 'Skip Codeship CI test')
    def test_ci_codeship(self):
        self.set_env(CI_NAME='codeship',
                     CI_BRANCH='master',
                     CI_BUILD_NUMBER='20',
                     CI_BUILD_URL='https://codeship.io/build/1',
                     CI_COMMIT_ID='743b04806ea677403aa2ff26c6bdeb85005de658',
                     CODECOV_TOKEN='token')
        self.fake_report()
        res = self.run_cli()
        self.assertEqual(res['query']['service'], 'codeship')
        self.assertEqual(res['query']['commit'], '743b04806ea677403aa2ff26c6bdeb85005de658')
        self.assertEqual(res['query']['build'], '20')
        self.assertEqual(res['query']['build_url'], 'https://codeship.io/build/1')
        self.assertEqual(res['query']['pr'], '')
        self.assertEqual(res['query']['branch'], 'master')
        self.assertEqual(res['codecov'].token, 'token')

    @unittest.skipUnless(os.getenv('CI') == 'true' and os.getenv('CIRCLECI') == 'true', 'Skip Circle CI test')
    def test_ci_circleci(self):
        self.set_env(CIRCLECI='true',
                     CIRCLE_BUILD_NUM='57',
                     CIRCLE_NODE_INDEX='1',
                     CIRCLE_PR_NUMBER='1',
                     CIRCLE_BRANCH='master',
                     CIRCLE_PROJECT_USERNAME='owner',
                     CIRCLE_PROJECT_REPONAME='repo',
                     CIRCLE_SHA1='d653b934ed59c1a785cc1cc79d08c9aaa4eba73b')
        self.fake_report()
        res = self.run_cli()
        self.assertEqual(res['query']['service'], 'circleci')
        self.assertEqual(res['query']['commit'], 'd653b934ed59c1a785cc1cc79d08c9aaa4eba73b')
        self.assertEqual(res['query']['build'], '57.1')
        self.assertEqual(res['query']['pr'], '1')
        self.assertEqual(res['query']['slug'], 'owner/repo')
        self.assertEqual(res['query']['branch'], 'master')

    @unittest.skipUnless(os.getenv('CI') == 'true' and os.getenv('BUILDKITE') == 'true', 'Skip BuildKit CI test')
    def test_ci_buildkite(self):
        self.set_env(CI='true',
                     BUILDKITE='true',
                     BUILDKITE_BUILD_NUMBER='57',
                     BUILDKITE_JOB_ID='1',
                     BUILDKITE_BRANCH='master',
                     BUILDKITE_PROJECT_SLUG='owner/repo',
                     BUILDKITE_COMMIT='d653b934ed59c1a785cc1cc79d08c9aaa4eba73b',
                     CODECOV_TOKEN='token')
        self.fake_report()
        res = self.run_cli()
        self.assertEqual(res['query']['service'], 'buildkite')
        self.assertEqual(res['query']['commit'], 'd653b934ed59c1a785cc1cc79d08c9aaa4eba73b')
        self.assertEqual(res['query']['build'], '57.1')
        self.assertEqual(res['query']['slug'], 'owner/repo')
        self.assertEqual(res['query']['branch'], 'master')
        self.assertEqual(res['codecov'].token, 'token')

    @unittest.skipUnless(os.getenv('CI') == 'true' and os.getenv('SEMAPHORE') == 'true', 'Skip Semaphore CI test')
    def test_ci_semaphore(self):
        self.set_env(SEMAPHORE='true',
                     BRANCH_NAME='master',
                     SEMAPHORE_BUILD_NUMBER='10',
                     SEMAPHORE_CURRENT_THREAD='1',
                     SEMAPHORE_REPO_SLUG='owner/repo',
                     REVISION='743b04806ea677403aa2ff26c6bdeb85005de658',
                     CODECOV_TOKEN='token')
        self.fake_report()
        res = self.run_cli()
        self.assertEqual(res['query']['service'], 'semaphore')
        self.assertEqual(res['query']['commit'], '743b04806ea677403aa2ff26c6bdeb85005de658')
        self.assertEqual(res['query']['build'], '10.1')
        self.assertEqual(res['query']['slug'], 'owner/repo')
        self.assertEqual(res['query']['branch'], 'master')

    @unittest.skipUnless(os.getenv('CI') == "drone" and os.getenv('DRONE') == "true", 'Skip Drone CI test')
    def test_ci_drone(self):
        self.set_env(CI='drone',
                     DRONE='true',
                     DRONE_BUILD_NUMBER='10',
                     DRONE_BRANCH='master',
                     DRONE_BUILD_LINK='https://drone.io/github/builds/1',
                     CODECOV_TOKEN='token')
        self.fake_report()
        res = self.run_cli()
        self.assertEqual(res['query']['service'], 'drone.io')
        self.assertEqual(res['query']['commit'], codecov.check_output(("git", "rev-parse", "HEAD")))
        self.assertEqual(res['query']['build'], '10')
        self.assertEqual(res['query']['build_url'], 'https://drone.io/github/builds/1')
        self.assertEqual(res['codecov'].token, 'token')

    @unittest.skipUnless(os.getenv('SHIPPABLE') == "true", 'Skip Shippable CI test')
    def test_ci_shippable(self):
        self.set_env(SHIPPABLE='true',
                     BUILD_NUMBER='10',
                     REPO_NAME='owner/repo',
                     BRANCH='master',
                     BUILD_URL='https://shippable.com/...',
                     COMMIT='743b04806ea677403aa2ff26c6bdeb85005de658',
                     CODECOV_TOKEN='token')
        self.fake_report()
        res = self.run_cli()
        self.assertEqual(res['query']['service'], 'shippable')
        self.assertEqual(res['query']['commit'], '743b04806ea677403aa2ff26c6bdeb85005de658')
        self.assertEqual(res['query']['build'], '10')
        self.assertEqual(res['query']['slug'], 'owner/repo')
        self.assertEqual(res['query']['build_url'], 'https://shippable.com/...')
        self.assertEqual(res['codecov'].token, 'token')

    # @unittest.skipUnless(os.getenv('CI') == "True" and os.getenv('APPVEYOR') == 'True', 'Skip AppVeyor CI test')
    @unittest.skip('Skip AppVeyor test')
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
        self.fake_report()
        res = self.run_cli(file=self.filepath)
        self.assertEqual(res['query']['service'], 'appveyor')
        self.assertEqual(res['query']['commit'], 'd653b934ed59c1a785cc1cc79d08c9aaa4eba73b')
        self.assertEqual(res['query']['job'], 'owner/repo/1.2.3')
        self.assertEqual(res['query']['build'], '9r2qufuu8')
        self.assertEqual(res['query']['slug'], 'owner/repo')
        self.assertEqual(res['query']['pr'], '1')
        self.assertEqual(res['codecov'].token, 'token')

    @unittest.skipUnless(os.getenv('CI') == "true" and os.getenv('WERCKER_GIT_BRANCH'), 'Skip Wercker CI test')
    def test_ci_wercker(self):
        self.set_env(WERCKER_GIT_BRANCH='master',
                     WERCKER_MAIN_PIPELINE_STARTED='1399372237',
                     WERCKER_GIT_OWNER='owner',
                     WERCKER_GIT_REPOSITORY='repo',
                     WERCKER_GIT_COMMIT='d653b934ed59c1a785cc1cc79d08c9aaa4eba73b',
                     CODECOV_TOKEN='token')
        self.fake_report()
        res = self.run_cli()
        self.assertEqual(res['query']['service'], 'wercker')
        self.assertEqual(res['query']['commit'], 'd653b934ed59c1a785cc1cc79d08c9aaa4eba73b')
        self.assertEqual(res['query']['build'], '1399372237')
        self.assertEqual(res['query']['slug'], 'owner/repo')
        self.assertEqual(res['codecov'].token, 'token')

    @unittest.skipUnless(os.getenv('CI') == "true" and os.getenv('MAGNUM') == 'true', 'Skip Magnum CI test')
    def test_ci_magnum(self):
        self.set_env(CI_BRANCH='master',
                     CI_BUILD_NUMBER='1399372237',
                     MAGNUM='true',
                     CI='true',
                     CI_COMMIT='d653b934ed59c1a785cc1cc79d08c9aaa4eba73b',
                     CODECOV_TOKEN='token')
        self.fake_report()
        res = self.run_cli()
        self.assertEqual(res['query']['service'], 'magnum')
        self.assertEqual(res['query']['commit'], 'd653b934ed59c1a785cc1cc79d08c9aaa4eba73b')
        self.assertEqual(res['query']['build'], '1399372237')
        self.assertEqual(res['codecov'].token, 'token')

    @unittest.skipUnless(os.getenv('CI_SERVER_NAME', '').startswith("GitLab"), 'Skip GitLab CI test')
    def test_ci_gitlab(self):
        self.set_env(CI_BUILD_REF_NAME='master',
                     CI_BUILD_ID='1399372237',
                     CI_BUILD_REPO='https://gitlab.com/owner/repo.git',
                     CI_SERVER_NAME='GitLab CI',
                     CI_BUILD_REF='d653b934ed59c1a785cc1cc79d08c9aaa4eba73b',
                     HOME='/',
                     CI_PROJECT_DIR=os.getcwd().strip('/'),
                     CODECOV_TOKEN='token')
        self.fake_report()
        res = self.run_cli()
        self.assertEqual(res['query']['service'], 'gitlab')
        self.assertEqual(res['query']['commit'], 'd653b934ed59c1a785cc1cc79d08c9aaa4eba73b')
        self.assertEqual(res['query']['build'], '1399372237')
        self.assertEqual(res['query']['slug'], 'owner/repo')
        self.assertEqual(res['codecov'].token, 'token')

    @unittest.skip('Skip CI None')
    def test_ci_none(self):
        self.set_env(CODECOV_TOKEN='token')
        self.fake_report()
        res = self.run_cli(build=10,
                           commit='d653b934ed59c1a785cc1cc79d08c9aaa4eba73b',
                           slug='owner/repo',
                           token='token')
        self.assertEqual(res['query'].get('service'), None)
        self.assertEqual(res['query']['commit'], 'd653b934ed59c1a785cc1cc79d08c9aaa4eba73b')
        self.assertEqual(res['query']['build'], '10')
        self.assertEqual(res['query']['slug'], 'owner/repo')
        self.assertEqual(res['codecov'].token, 'token')
