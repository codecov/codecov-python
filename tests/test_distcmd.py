
import os
import tempfile
import shutil
import subprocess
import contextlib

try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser

try:
    from setuptools.dist import Distribution
except ImportError:
    from distutil.dist import Distribution

try:
    from io import StringIO
except ImportError:
    from StringIO import StringIO

from mock import patch
import unittest2 as unittest

from codecov import main, __version__
from codecov.distcmd import codecov


class TestDistutilsCommand(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.initdir = os.getcwd()
        cls.tempdir = 'tmp'
        if not os.path.isdir('tmp'):
            os.mkdir('tmp')
        os.chdir(cls.tempdir)

    @classmethod
    def tearDownClass(cls):
        os.chdir(cls.initdir)
        shutil.rmtree('tmp')

    @contextlib.contextmanager
    def environ(self, setup_cfg=None, *args, **variables):

        args = ['codecov'] + list(args)

        if setup_cfg is not None:
            parser = ConfigParser()
            parser.add_section('codecov')
            for k, v in setup_cfg.items():
                parser.set('codecov', k, str(v))
            with open('setup.cfg', 'w') as f:
                parser.write(f)

        yield Distribution({'script_name': 'setup.py',
                            'script_args': args or ['codecov']})

        #finally:
        if os.path.isfile('setup.cfg'):
            os.remove('setup.cfg')

    def test_plain(self):
        # No setup.cfg, no argument, just like running 'codecov' directly

        with self.environ() as dist:
            command = codecov(dist)
            try:
                command.run()
            except SystemExit as se:
                self.assertNotEqual(se, 0)
                self.fail('Command failed.')

    def test_plain_required(self):
        # No setup.cfg, --required argument

        with self.environ(None, '--required') as dist:
            command = codecov(dist)
            with self.assertRaises(SystemExit):
                command.run()

    def test_setupcfg_required(self):
        # setup.cfg with required=true, no argument

        setup_cfg = {'required': True}
        with self.environ(setup_cfg) as dist:
            command = codecov(dist)
            with self.assertRaises(SystemExit):
                command.run()

    def test_lists(self):
        # files and disable in setup.cfg, env in arguments

        setup_cfg = {
            'disable': 'search, detect, gcov, pycov', # single line list
            'files': # multi line string
                '''
                some random file
                /some/root/file
                '''
        }

        with self.environ(setup_cfg, '--env', 'CI,TRAVIS') as dist:
            command = codecov(dist)
            command.ensure_finalized()

            files = vars(command).get('files')
            env = vars(command).get('env')
            disable = vars(command).get('disable')

            self.assertEqual(files, ['some random file', '/some/root/file'])
            self.assertEqual(env, ['CI', 'TRAVIS'])
            self.assertEqual(disable, ['search', 'detect', 'gcov', 'pycov'])

    def test_lists_2(self):
        setup_cfg = {'file': 'some single file'}

        with self.environ(setup_cfg, '--gcov-glob', 'test*') as dist:
            command = codecov(dist)
            command.ensure_finalized()

            files = vars(command).get('files')
            gcov_glob = vars(command).get('gcov_glob')

            self.assertEqual(files, ['some single file'])
            self.assertEqual(gcov_glob, ['test*'])



    def test_version(self):
        with self.environ(None, '--version') as dist:
            command = codecov(dist)
            with patch('sys.stdout', new_callable=StringIO) as stdout:
                command.run()
                version = 'Codecov py-v{}'.format(__version__)
                self.assertIn(version, stdout.getvalue())
