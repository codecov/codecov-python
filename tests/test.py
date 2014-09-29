import os
import json
import requests
import unittest
import itertools
import subprocess

import codecov


class TestUploader(unittest.TestCase):
    url = os.getenv("DEBUG_URL", "https://codecov.io")
    maxDiff = None

    def setUp(self):
        # set all environ back
        os.environ['CI'] = "true"
        for key in ("TRAVIS", "TRAVIS_BRANCH", "TRAVIS_COMMIT", "TRAVIS_BUILD_DIR", "TRAVIS_JOB_ID",
                    "CI_NAME", "CI_BRANCH", "CI_COMMIT_ID", 
                    "CIRCLECI", "CIRCLE_BRANCH", "CIRCLE_ARTIFACTS", "CIRCLE_SHA1", 
                    "SEMAPHORE", "BRANCH_NAME", "SEMAPHORE_PROJECT_DIR", "SEMAPHORE_PROJECT_HASH_ID", 
                    "DRONE", "DRONE_BRANCH", "DRONE_BUILD_DIR", "DRONE_COMMIT", "JENKINS_URL",
                    "GIT_BRANCH", "GIT_COMMIT", "WORKSPACE", "BUILD_NUMBER", "CI_BUILD_URL", "SEMAPHORE_REPO_SLUG",
                    "DRONE_BUILD_URL", "TRAVIS_REPO_SLUG", "CODECOV_TOKEN"):
            os.environ[key] = ""

    def test_command(self):
        try:
            subprocess.check_output('python -m codecov.__init__ --hep', stderr=subprocess.STDOUT, shell=True)
        except subprocess.CalledProcessError as e:
            self.assertIn(b'usage: codecov', e.output)
        else:
            raise AssertionError("Process exited with 0 status code")

    def test_pass_1(self): self.passed(self.upload())
    def test_pass_2(self): self.passed(self.upload(travis_job_id="33116958", commit="c739768fcac68144a3a6d82305b9c4106934d31a"))
    def test_pass_3(self): self.passed(self.upload(branch="other-branch/strang_name"))
    def test_pass_4(self): self.passed(self.upload(path="project"))
    def test_pass_5(self): self.passed(self.upload(path="other/folder"))

    def test_fail_1(self): self.failed(self.upload(report=""), "error no coverage report found, could not upload to codecov")
    def test_fail_2(self): self.failed(self.upload(token=""), "missing token or other required argument(s)")
    def test_fail_3(self): self.assertRaisesRegexp(requests.exceptions.HTTPError, "commit sha mismatch", self.upload, travis_job_id="12125215", token="")
    def test_fail_4(self): self.failed(self.upload(commit=""), "commit hash is required")
    def test_fail_5(self): self.failed(self.upload(branch=""), "branch is required")

    def test_report_accuracy(self):
        report = codecov.from_file(os.path.join(os.path.dirname(__file__), 'xml/cobertura/coverage.xml'))
        with open(os.path.join(os.path.dirname(__file__), 'json/coverage.json')) as f:
            compare = json.loads(f.read()%codecov.version)
        self.assertDictEqual(report["coverage"], compare["coverage"])
        self.assertDictEqual(report["meta"], compare["meta"])
        self.assertDictEqual(report["stats"], compare["stats"])

    def test_clover(self):
        report = codecov.from_file(os.path.join(os.path.dirname(__file__), 'xml/clover/clover.xml'))
        with open(os.path.join(os.path.dirname(__file__), 'json/clover.json')) as f:
            compare = json.loads(f.read()%codecov.version)
        self.assertDictEqual(report["coverage"], compare["coverage"])
        self.assertDictEqual(report["meta"], compare["meta"])

    def test_jacoco_xml(self):
        report = codecov.from_file(os.path.join(os.path.dirname(__file__), 'xml/jacoco/jacoco.xml'))
        with open(os.path.join(os.path.dirname(__file__), 'json/jacoco.json')) as f:
            compare = json.loads(f.read()%codecov.version)
        self.assertDictEqual(report, compare)

    def test_golang(self):
        result = codecov.reports.go.from_txt("""mode: count
github.com/codecov/sample_go/sample_go.go:7.14,9.2 1 1
github.com/codecov/sample_go/sample_go.go:11.26,13.2 1 1
github.com/codecov/sample_go/sample_go.go:15.19,17.2 1 0
""")
        self.assertDictEqual(result, dict(coverage={"github.com/codecov/sample_go/sample_go.go":[None, None, None, None, None, None, None, 1, 1, 1, None, 1, 1, 1, None, 0, 0, 0]},
                                          meta=dict(report="go.txt")))

        os.environ['TRAVIS'] = "true"
        os.environ['TRAVIS_BRANCH'] = "master"
        os.environ['TRAVIS_COMMIT'] = "c739768fcac68144a3a6d82305b9c4106934d31a"
        os.environ['TRAVIS_BUILD_DIR'] = os.path.join(os.path.dirname(__file__), "txt/")
        os.environ['TRAVIS_REPO_SLUG'] = 'codecov/ci-repo'
        os.environ['TRAVIS_JOB_ID'] = "33116958"
        output = subprocess.check_output("python -m codecov.__init__", shell=True)
        output = output.replace(b'\nCoverage.py warning: No data was collected.', b'')
        self.assertDictEqual(json.loads(output.decode('utf-8')), 
                             {"uploaded": True, 
                              "features": {},
                              "version": codecov.version, 
                              "url": "http://codecov.io/github/codecov/ci-repo?ref=c739768fcac68144a3a6d82305b9c4106934d31a", 
                              "message": "Coverage reports upload successfully", 
                              "coverage": 67})

    def test_console(self): 
        self.passed(self.command(**self.basics()))

    def test_jenkins(self): 
        os.environ['JENKINS_URL'] = "https://...."
        os.environ['GIT_BRANCH'] = "master"
        os.environ['GIT_COMMIT'] = "c739768fcac68144a3a6d82305b9c4106934d31a"
        os.environ['WORKSPACE'] = os.path.join(os.path.dirname(__file__), "xml/cobertura")
        os.environ['BUILD_NUMBER'] = "41"
        os.environ['CODECOV_TOKEN'] = '473c8c5b-10ee-4d83-86c6-bfd72a185a27'
        self.passed(self.command())

    def test_travis(self): 
        os.environ['TRAVIS'] = "true"
        os.environ['TRAVIS_BRANCH'] = "master"
        os.environ['TRAVIS_COMMIT'] = "c739768fcac68144a3a6d82305b9c4106934d31a"
        os.environ['TRAVIS_BUILD_DIR'] = os.path.join(os.path.dirname(__file__), "xml/cobertura")
        os.environ['TRAVIS_REPO_SLUG'] = 'codecov/ci-repo'
        os.environ['TRAVIS_JOB_ID'] = "33116958"
        os.environ['TRAVIS_JOB_NUMBER'] = "4.1"
        self.passed(self.command())

    def test_codeship(self):
        os.environ['CI_NAME'] = 'codeship'
        os.environ['CI_BRANCH'] = 'master'
        os.environ['CI_BUILD_NUMBER'] = '20'
        os.environ['CI_BUILD_URL'] = 'htts://codeship.io/build/1'
        os.environ['CI_COMMIT_ID'] = '743b04806ea677403aa2ff26c6bdeb85005de658'
        os.environ['CODECOV_TOKEN'] = '473c8c5b-10ee-4d83-86c6-bfd72a185a27'
        self.passed(self.command(report=os.path.join(os.path.dirname(__file__), "xml/cobertura/coverage.xml")))

    def test_circleci(self):
        os.environ['CIRCLECI'] = 'true'
        os.environ['CIRCLE_BUILD_NUM'] = "40"
        os.environ['CIRCLE_BRANCH'] = "add-django-tests"
        os.environ['CIRCLE_PROJECT_USERNAME'] = "FreeMusicNinja"
        os.environ['CIRCLE_PROJECT_REPONAME'] = "freemusic.ninja"
        os.environ['CIRCLE_BUILD_NUM'] = "57"
        os.environ['CIRCLE_SHA1'] = "d653b934ed59c1a785cc1cc79d08c9aaa4eba73b"
        os.environ['CODECOV_TOKEN'] = '473c8c5b-10ee-4d83-86c6-bfd72a185a27'
        self.passed(self.command(report=os.path.join(os.path.dirname(__file__), "xml/cobertura/coverage.xml")))

    def test_semaphore(self):
        os.environ['SEMAPHORE'] = "true"
        os.environ['BRANCH_NAME'] = "master"
        os.environ['SEMAPHORE_BUILD_NUMBER'] = "10"
        os.environ['SEMAPHORE_REPO_SLUG'] = 'codecov/ci-repo'
        os.environ['SEMAPHORE_PROJECT_HASH_ID'] = "743b04806ea677403aa2ff26c6bdeb85005de658"
        os.environ['CODECOV_TOKEN'] = '473c8c5b-10ee-4d83-86c6-bfd72a185a27'
        self.passed(self.command(report=os.path.join(os.path.dirname(__file__), "xml/cobertura/coverage.xml")))

    def test_drone(self):
        os.environ['DRONE'] = "true"
        os.environ['BUILD_ID'] = "10"
        os.environ['DRONE_BRANCH'] = "master"
        os.environ['DRONE_BUILD_URL'] = "htts://drone.io/github/builds/1"
        os.environ['DRONE_COMMIT'] = "743b04806ea677403aa2ff26c6bdeb85005de658"
        os.environ['CODECOV_TOKEN'] = '473c8c5b-10ee-4d83-86c6-bfd72a185a27'
        self.passed(self.command(report=os.path.join(os.path.dirname(__file__), "xml/cobertura/coverage.xml")))

    def test_min_coverage(self):
        os.environ['TRAVIS'] = "true"
        os.environ['TRAVIS_BRANCH'] = "master"
        os.environ['TRAVIS_COMMIT'] = "c739768fcac68144a3a6d82305b9c4106934d31a"
        os.environ['TRAVIS_REPO_SLUG'] = 'codecov/ci-repo'
        os.environ['TRAVIS_BUILD_DIR'] = os.path.join(os.path.dirname(__file__), "xml/cobertura")
        os.environ['TRAVIS_JOB_ID'] = "33116958"
        subprocess.check_output("python -m codecov.__init__ --min-coverage=75", shell=True)
        try:
            subprocess.check_output("python -m codecov.__init__ --min-coverage=90", shell=True)
        except subprocess.CalledProcessError as e:
            self.assertEqual(e.returncode, 1)
        else:
            raise AssertionError("Process exited with 0 status code")

    def test_cli(self):
        os.environ['TRAVIS'] = "true"
        os.environ['TRAVIS_BRANCH'] = "master"
        os.environ['TRAVIS_COMMIT'] = "c739768fcac68144a3a6d82305b9c4106934d31a"
        os.environ['TRAVIS_BUILD_DIR'] = os.path.join(os.path.dirname(__file__), "xml/cobertura")
        os.environ['TRAVIS_REPO_SLUG'] = 'codecov/ci-repo'
        os.environ['TRAVIS_JOB_ID'] = "33116958"
        output = subprocess.check_output("python -m codecov.__init__", shell=True)
        output = output.replace(b'\nCoverage.py warning: No data was collected.', b'')
        self.assertDictEqual(json.loads(output.decode('utf-8')), 
                             {"uploaded": True, 
                              "features": {},
                              "version": codecov.version, 
                              "url": "http://codecov.io/github/codecov/ci-repo?ref=c739768fcac68144a3a6d82305b9c4106934d31a", 
                              "message": "Coverage reports upload successfully", 
                              "coverage": 80})

    def basics(self):
        return dict(token="473c8c5b-10ee-4d83-86c6-bfd72a185a27", 
                    report=os.path.join(os.path.dirname(__file__), "xml/cobertura/coverage.xml"),
                    url=self.url,
                    commit="743b04806ea677403aa2ff26c6bdeb85005de658",
                    branch="master")

    def command(self, **kwargs):
        args = dict(url=self.url)
        args.update(kwargs)
        inline = list(itertools.chain(*[['--%s'% key, value] for key, value in args.items() if value]))
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
            self.assertIn('github/codecov/ci-repo?ref=%s'%toserver['commit'], fromserver['url'])
        else:
            self.assertRegexpMatches(fromserver['url'], r'/(github|bitbucket)/[\w\-\.]+/[\w\-\.]+\?ref=[a-z\d]{40}')
        self.assertEqual(fromserver['message'], 'Coverage reports upload successfully')

    def failed(self, result, why):
        fromserver, toserver = result
        self.assertEqual(fromserver['uploaded'], False)
        self.assertEqual(fromserver['message'], why)
