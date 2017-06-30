
import os
import tempfile
import contextlib

try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser

try:
    from setuptools.dist import Distribution
except ImportError:
    from distutil.dist import Distribution

from mock import patch
import unittest2 as unittest

import codecov
from codecov.distcmd import Codecov


class TestDistutilsCommand(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.initdir = os.getcwd()
        cls.tempdir = tempfile.gettempdir()
        os.chdir(cls.tempdir)

    @classmethod
    def tearDownClass(cls):
        os.chdir(cls.initdir)

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
            command = Codecov(dist)
            try:
                command.run()
            except SystemExit as se:
                self.assertNotEqual(se, 0)
                self.fail('Command failed.')

    def test_plain_required(self):
        # No setup.cfg, --required argument

        with self.environ(None, '--required') as dist:
            command = Codecov(dist)
            with self.assertRaises(SystemExit):
                command.run()

    def test_setupcfg_required(self):
        # setup.cfg with required=true, no argument

        setup_cfg = {'required': True}
        with self.environ(setup_cfg) as dist:
            command = Codecov(dist)
            with self.assertRaises(SystemExit):
                command.run()
