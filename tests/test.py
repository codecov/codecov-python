import os
import json
import unittest
import itertools
import commands

import codecov


class TestUploader(unittest.TestCase):
    url = os.getenv("DEBUG_URL", "https://codecov.io")

    def setUp(self):
        # set all environ back
        os.environ['CI'] = "true"
        for key in ("TRAVIS", "TRAVIS_BRANCH", "TRAVIS_COMMIT", "TRAVIS_BUILD_DIR", "TRAVIS_JOB_ID",
                    "CI_NAME", "CI_BRANCH", "CI_COMMIT_ID", 
                    "CIRCLECI", "CIRCLE_BRANCH", "CIRCLE_ARTIFACTS", "CIRCLE_SHA1", 
                    "SEMAPHORE", "BRANCH_NAME", "SEMAPHORE_PROJECT_DIR", "SEMAPHORE_PROJECT_HASH_ID", 
                    "DRONE", "DRONE_BRANCH", "DRONE_BUILD_DIR", "DRONE_COMMIT", 
                    "CODECOV_TOKEN"):
            os.environ[key] = ""

    def test_command(self):
        self.assertIn('usage: codecov', commands.getstatusoutput('codecov --hep')[1])

    def test_pass_1(self): self.passed(self.upload())
    def test_pass_2(self): self.passed(self.upload(travis_job_id="33116958", commit="c739768fcac68144a3a6d82305b9c4106934d31a"))
    def test_pass_3(self): self.passed(self.upload(branch="other-branch/strang_name"))

    def test_fail_1(self): self.failed(self.upload(xml=""), "no coverage.xml file could be found or generated")
    def test_fail_2(self): self.failed(self.upload(token=""), "travis_job_id or token are required")
    def test_fail_3(self): self.failed(self.upload(travis_job_id="12125215", token=""), "travis job commit and upload commit do not match")
    def test_fail_4(self): self.failed(self.upload(commit=""), "commit hash is required")
    def test_fail_5(self): self.failed(self.upload(branch=""), "branch is required")

    def test_report_accuracy(self):
        report = codecov.generate_report(os.path.join(os.path.dirname(__file__), 'xml/coverage.xml'))
        with open(os.path.join(os.path.dirname(__file__), 'json/coverage.json')) as f:
            compare = json.loads(f.read()%codecov.version)
        self.assertDictEqual(report["coverage"], compare["coverage"])
        self.assertDictEqual(report["meta"], compare["meta"])
        self.assertDictEqual(report["stats"], compare["stats"])

    def test_clover(self):
        report = codecov.generate_report(os.path.join(os.path.dirname(__file__), 'xml/clover.xml'))
        with open(os.path.join(os.path.dirname(__file__), 'json/clover.json')) as f:
            compare = json.loads(f.read())
        self.assertDictEqual(report["coverage"], compare["coverage"])
        self.assertDictEqual(report["meta"], compare["meta"])

    def test_console(self): 
        self.passed(self.command(**self.basics()))

    def test_travis(self): 
        os.environ['TRAVIS'] = "true"
        os.environ['TRAVIS_BRANCH'] = "master"
        os.environ['TRAVIS_COMMIT'] = "c739768fcac68144a3a6d82305b9c4106934d31a"
        os.environ['TRAVIS_BUILD_DIR'] = os.path.join(os.path.dirname(__file__), "xml/")
        os.environ['TRAVIS_JOB_ID'] = "33116958"
        self.passed(self.command())

    def test_codeship(self):
        os.environ['CI_NAME'] = 'codeship'
        os.environ['CI_BRANCH'] = 'master'
        os.environ['CI_COMMIT_ID'] = '743b04806ea677403aa2ff26c6bdeb85005de658'
        os.environ['CODECOV_TOKEN'] = '473c8c5b-10ee-4d83-86c6-bfd72a185a27'
        self.passed(self.command(xml=os.path.join(os.path.dirname(__file__), "xml/coverage.xml")))

    def test_circleci(self):
        os.environ['CIRCLECI'] = 'true'
        os.environ['CIRCLE_BRANCH'] = "master"
        os.environ['CIRCLE_ARTIFACTS'] = os.path.join(os.path.dirname(__file__), "xml/")
        os.environ['CIRCLE_SHA1'] = "743b04806ea677403aa2ff26c6bdeb85005de658"
        os.environ['CODECOV_TOKEN'] = '473c8c5b-10ee-4d83-86c6-bfd72a185a27'
        self.passed(self.command())

    def test_semaphore(self):
        os.environ['SEMAPHORE'] = "true"
        os.environ['BRANCH_NAME'] = "master"
        os.environ['SEMAPHORE_PROJECT_DIR'] = os.path.join(os.path.dirname(__file__), "xml/")
        os.environ['SEMAPHORE_PROJECT_HASH_ID'] = "743b04806ea677403aa2ff26c6bdeb85005de658"
        os.environ['CODECOV_TOKEN'] = '473c8c5b-10ee-4d83-86c6-bfd72a185a27'
        self.passed(self.command())

    def test_drone(self):
        os.environ['DRONE'] = "true"
        os.environ['DRONE_BRANCH'] = "master"
        os.environ['DRONE_BUILD_DIR'] = os.path.join(os.path.dirname(__file__), "xml/")
        os.environ['DRONE_COMMIT'] = "743b04806ea677403aa2ff26c6bdeb85005de658"
        os.environ['CODECOV_TOKEN'] = '473c8c5b-10ee-4d83-86c6-bfd72a185a27'
        self.passed(self.command())

    def basics(self):
        return dict(token="473c8c5b-10ee-4d83-86c6-bfd72a185a27", 
                    xml=os.path.join(os.path.dirname(__file__), "xml/coverage.xml"),
                    url=self.url,
                    commit="743b04806ea677403aa2ff26c6bdeb85005de658",
                    branch="master")

    def command(self, **kwargs):
        args = dict(url=self.url)
        args.update(kwargs)
        inline = list(itertools.chain(*[['--%s'% key, value] for key, value in args.items() if value]))
        print "\033[92m....\033[0m", inline
        return codecov.main(*inline), args

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
            self.assertRegexpMatches(fromserver['url'], r'/github/codecov/ci-repo\?ref=[a-z\d]{40}')
        self.assertEqual(fromserver['message'], 'Coverage reports upload successfully')

    def failed(self, result, why):
        fromserver, toserver = result
        self.assertEqual(fromserver['uploaded'], False)
        self.assertEqual(fromserver['message'], why)
