import os
import json
import requests
import unittest2 as unittest
import itertools

import codecov

try:
    import subprocess32 as subprocess
except ImportError:
    import subprocess


class TestUploader(unittest.TestCase):
    url = os.getenv("DEBUG_URL", "https://codecov.io")
    maxDiff = None
    a_report = os.path.join(os.path.dirname(__file__), "coverages/xml/cobertura/")
    upload_token = "473c8c5b-10ee-4d83-86c6-bfd72a185a27"

    def setUp(self):
        # set all environ back
        os.environ['CI'] = "true"
        os.environ['CODECOV_ENDPOINT'] = self.url
        for key in ("TRAVIS", "TRAVIS_BRANCH", "TRAVIS_COMMIT", "TRAVIS_BUILD_DIR", "TRAVIS_JOB_ID",
                    "CI_NAME", "CI_BRANCH", "CI_COMMIT_ID",
                    "CI_BUILD_NUMBER", "MAGNUM", "CI_COMMIT", "APPVEYOR_ACCOUNT_NAME", "APPVEYOR_PROJECT_SLUG", "APPVEYOR_PULL_REQUEST_NUMBER",
                    "CIRCLECI", "CIRCLE_BRANCH", "CIRCLE_ARTIFACTS", "CIRCLE_SHA1",
                    "SEMAPHORE", "BRANCH_NAME", "SEMAPHORE_PROJECT_DIR", "REVISION",
                    "DRONE", "DRONE_BRANCH", "DRONE_BUILD_DIR", "DRONE_COMMIT", "JENKINS_URL",
                    "GIT_BRANCH", "GIT_COMMIT", "WORKSPACE", "BUILD_NUMBER", "CI_BUILD_URL", "SEMAPHORE_REPO_SLUG",
                    "DRONE_BUILD_URL", "TRAVIS_REPO_SLUG", "CODECOV_TOKEN", "APPVEYOR", "APPVEYOR_REPO_BRANCH",
                    "APPVEYOR_BUILD_VERSION", "APPVEYOR_JOB_ID", "APPVEYOR_REPO_NAME", "APPVEYOR_REPO_COMMIT", "WERCKER_GIT_BRANCH",
                    "WERCKER_MAIN_PIPELINE_STARTED", "WERCKER_GIT_OWNER", "WERCKER_GIT_REPOSITORY",
                    "CI_BUILD_REF_NAME", "CI_BUILD_ID", "CI_BUILD_REPO", "CI_PROJECT_DIR", "CI_BUILD_REF", "CI_SERVER_NAME",
                    "ghprbActualCommit", "ghprbSourceBranch", "ghprbPullId", "WERCKER_GIT_COMMIT"):
            os.environ[key] = ""

    def set_env(self, **kwargs):
        """Fake config variables
        """
        for key in kwargs:
            os.environ[key] = str(kwargs[key])

    def basics(self):
        """Default information for testing
        """
        return dict(token=self.upload_token,
                    root=os.path.join(os.path.dirname(__file__), "coverages/"),
                    url=self.url,
                    commit="743b04806ea677403aa2ff26c6bdeb85005de658",
                    branch="master")

    def command(self, **kwargs):
        args = dict(url=self.url)
        args.update(kwargs)
        inline = list(itertools.chain(*[['--%s' % key, value] for key, value in args.items() if value]))
        data, passes = codecov.main(*inline)
        return data, args

    def upload(self, **kwargs):
        args = self.basics()
        args.update(kwargs)
        return codecov.upload(**args), args

    def passed(self, result):
        fromserver, toserver = result
        self.assertEqual(fromserver['uploaded'], True, fromserver)
        if toserver.get('commit'):
            self.assertIn('github/codecov/ci-repo?ref=%s' % toserver['commit'], fromserver['url'])
        else:
            self.assertRegexpMatches(fromserver['url'], r'/(github|gitlab|bitbucket)/[\w\-\.]+/[\w\-\.]+\?ref=[a-z\d]{40}')
        self.assertEqual(fromserver['message'], 'Coverage reports upload successfully')

    def failed(self, result, why):
        fromserver, toserver = result
        self.assertEqual(fromserver['uploaded'], False)
        self.assertEqual(fromserver['message'], why)

    def test_command(self):
        output = subprocess.check_output('python -m codecov.__init__ --help', shell=True)
        self.assertIn(b'usage: codecov', output)

    def test_required(self):
        output = subprocess.check_output('python -m codecov.__init__', stderr=subprocess.STDOUT, shell=True)
        self.assertIn("Message: missing token or other required argument(s)", output.decode('utf-8'))

    def test_pass_1(self):
        self.passed(self.upload())

    def test_pass_2(self):
        self.passed(self.upload(job="33116958", commit="c739768fcac68144a3a6d82305b9c4106934d31a"))

    def test_pass_3(self):
        self.passed(self.upload(branch="other-branch/strang_name"))

    def test_fail_1(self):
        self.failed(self.upload(root="/somwhere/not/found"), "error no coverage report found, could not upload to codecov")

    def test_fail_2(self):
        self.failed(self.upload(token=""), "missing token or other required argument(s)")

    def test_fail_3(self):
        self.assertRaises(requests.exceptions.HTTPError, self.upload, job="12125215", token="")

    def test_fail_4(self):
        self.failed(self.upload(commit=""), "commit hash is required")

    def test_fail_5(self):
        self.failed(self.upload(branch=""), "branch is required")

    def test_console(self):
        kwargs = self.basics()
        kwargs.pop('root')
        self.passed(self.command(**kwargs))

    def test_ci_jenkins(self):
        self.set_env(JENKINS_URL="https://....",
                     GIT_BRANCH="master",
                     GIT_COMMIT="c739768fcac68144a3a6d82305b9c4106934d31a",
                     WORKSPACE=self.a_report,
                     BUILD_NUMBER="41",
                     CODECOV_TOKEN=self.upload_token)
        self.passed(self.command())

    def test_ci_jenkins_env(self):
        self.set_env(JENKINS_URL="https://....",
                     ghprbSourceBranch="master",
                     ghprbActualCommit="c739768fcac68144a3a6d82305b9c4106934d31a",
                     ghprbPullId="1",
                     WORKSPACE=self.a_report,
                     BUILD_NUMBER="41",
                     CODECOV_TOKEN=self.upload_token)
        self.passed(self.command())

    def test_ci_travis(self):
        self.set_env(TRAVIS="true",
                     TRAVIS_BRANCH="master",
                     TRAVIS_COMMIT="c739768fcac68144a3a6d82305b9c4106934d31a",
                     TRAVIS_BUILD_DIR=self.a_report,
                     TRAVIS_REPO_SLUG='codecov/ci-repo',
                     TRAVIS_JOB_ID="33116958",
                     TRAVIS_JOB_NUMBER="4.1")
        self.passed(self.command())

    def test_ci_codeship(self):
        self.set_env(CI_NAME='codeship',
                     CI_BRANCH='master',
                     CI_BUILD_NUMBER='20',
                     CI_BUILD_URL='https://codeship.io/build/1',
                     CI_COMMIT_ID='743b04806ea677403aa2ff26c6bdeb85005de658',
                     CODECOV_TOKEN=self.upload_token)
        self.passed(self.command())

    def test_ci_circleci(self):
        self.set_env(CIRCLECI='true',
                     CIRCLE_BUILD_NUM="57",
                     CIRCLE_BRANCH="add-django-tests",
                     CIRCLE_PROJECT_USERNAME="FreeMusicNinja",
                     CIRCLE_PROJECT_REPONAME="freemusic.ninja",
                     CIRCLE_SHA1="d653b934ed59c1a785cc1cc79d08c9aaa4eba73b")
        self.passed(self.command())

    def test_ci_semaphore(self):
        self.set_env(SEMAPHORE="true",
                     BRANCH_NAME="master",
                     SEMAPHORE_BUILD_NUMBER="10",
                     SEMAPHORE_REPO_SLUG='codecov/ci-repo',
                     REVISION="743b04806ea677403aa2ff26c6bdeb85005de658",
                     CODECOV_TOKEN=self.upload_token)
        self.passed(self.command())

    def test_ci_drone(self):
        self.set_env(DRONE="true",
                     BUILD_ID="10",
                     DRONE_BRANCH="master",
                     DRONE_BUILD_URL="https://drone.io/github/builds/1",
                     DRONE_COMMIT="743b04806ea677403aa2ff26c6bdeb85005de658",
                     CODECOV_TOKEN=self.upload_token)
        self.passed(self.command())

    def test_ci_shippable(self):
        self.set_env(SHIPPABLE="true",
                     BUILD_NUMBER="10",
                     REPO_NAME='codecov/ci-repo',
                     BRANCH="master",
                     BUILD_URL="https://shippable.com/...",
                     COMMIT="743b04806ea677403aa2ff26c6bdeb85005de658",
                     CODECOV_TOKEN=self.upload_token)
        self.passed(self.command())

    def test_ci_appveyor(self):
        self.set_env(APPVEYOR='True',
                     CI='True',
                     APPVEYOR_JOB_ID="9r2qufuu8",
                     APPVEYOR_BUILD_VERSION="1.2.3",
                     APPVEYOR_ACCOUNT_NAME="owner",
                     APPVEYOR_PROJECT_SLUG="repo",
                     APPVEYOR_PULL_REQUEST_NUMBER="1",
                     APPVEYOR_REPO_BRANCH="add-django-tests",
                     APPVEYOR_REPO_NAME="FreeMusicNinja/freemusic.ninja",
                     APPVEYOR_REPO_COMMIT="d653b934ed59c1a785cc1cc79d08c9aaa4eba73b",
                     CODECOV_TOKEN=self.upload_token)
        self.passed(self.command())

    def test_ci_wercker(self):
        self.set_env(WERCKER_GIT_BRANCH="add-django-tests",
                     WERCKER_MAIN_PIPELINE_STARTED="1399372237",
                     WERCKER_GIT_OWNER="FreeMusicNinja",
                     WERCKER_GIT_REPOSITORY="freemusic.ninja",
                     WERCKER_GIT_COMMIT="d653b934ed59c1a785cc1cc79d08c9aaa4eba73b",
                     CODECOV_TOKEN=self.upload_token)
        self.passed(self.command())

    def test_ci_magnum(self):
        self.set_env(CI_BRANCH="add-django-tests",
                     CI_BUILD_NUMBER="1399372237",
                     MAGNUM="true",
                     CI="true",
                     CI_COMMIT="d653b934ed59c1a785cc1cc79d08c9aaa4eba73b",
                     CODECOV_TOKEN=self.upload_token)
        self.passed(self.command())

    def test_ci_gitlab(self):
        self.set_env(CI_BUILD_REF_NAME="add-django-tests",
                     CI_BUILD_ID="1399372237",
                     CI_BUILD_REPO="https://gitlab.com/owner/repo.git",
                     CI_SERVER_NAME="GitLab CI",
                     CI_PROJECT_DIR=self.a_report,
                     CI_BUILD_REF="d653b934ed59c1a785cc1cc79d08c9aaa4eba73b",
                     CODECOV_TOKEN=self.upload_token)
        self.passed(self.command())

    def test_cli(self):
        self.set_env(TRAVIS="true",
                     TRAVIS_BRANCH="master",
                     TRAVIS_COMMIT="c739768fcac68144a3a6d82305b9c4106934d31a",
                     TRAVIS_BUILD_DIR=self.a_report,
                     TRAVIS_REPO_SLUG='codecov/ci-repo',
                     TRAVIS_JOB_ID="33116958")
        output = subprocess.check_output("python -m codecov.__init__", shell=True)
        output = output.replace(b'\nCoverage.py warning: No data was collected.', b'')
        output = output.decode('utf-8')
        output = output.splitlines()
        self.assertEqual(output[0], "Uploaded: True")
        self.assertRegexpMatches(output[1], r"Report URL: https?://[\w\-\.]+(\:?\d*|\.io)?/github/codecov/ci-repo\?ref=c739768fcac68144a3a6d82305b9c4106934d31a$")
        self.assertEqual(output[2], "Upload Version: codecov-v%s" % codecov.version)
        self.assertEqual(output[3], "Message: Coverage reports upload successfully")

    def test_cli_json(self):
        self.set_env(TRAVIS="true",
                     TRAVIS_BRANCH="master",
                     TRAVIS_COMMIT="c739768fcac68144a3a6d82305b9c4106934d31a",
                     TRAVIS_BUILD_DIR=self.a_report,
                     TRAVIS_REPO_SLUG='codecov/ci-repo',
                     TRAVIS_JOB_ID="33116958")
        output = subprocess.check_output("python -m codecov.__init__ --json", shell=True)
        output = output.replace(b'\nCoverage.py warning: No data was collected.', b'')
        output = json.loads(output.decode('utf-8'))
        self.assertTrue(output['uploaded'])
        self.assertEqual(output['version'], codecov.version)
        self.assertRegexpMatches(output['url'], r"\/github\/codecov\/ci-repo\?ref\=c739768fcac68144a3a6d82305b9c4106934d31a$")
        self.assertEqual(output["message"], "Coverage reports upload successfully")
