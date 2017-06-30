import os
import sys

try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser

try:
    from setuptools import Command
except ImportError:
    from distutils.cmd import Command

from argparse import ArgumentParser
from distutils.errors import DistutilsArgError

import codecov


class Codecov(Command):

    command_name = "codecov"

    user_options =  [

        # ======================== Basics ======================== #
        ('version', None, 'show version'),
        ('token=', 't', "Private repository token or @filename for file containing the token. Defaults to $CODECOV_TOKEN. Not required for public repositories on Travis-CI, CircleCI and AppVeyor"),
        ('files=', 'f', 'Target specific files for uploading (comma separated).'),
        ('flags=', 'F', 'Flag these uploaded files with custom labels (comma separated).'),
        ('env=', 'e', 'Store environment variables to help distinguish CI builds (comma separated).'),
        ('required', None, 'If Codecov fails it will exit 1: failing the CI build.'),
        ('name=', 'n', 'Custom defined name of the upload. Visible in Codecov UI.'),

        # ======================== gcov ======================== #
        ('gcov-root=', None, "Project root directory when preparing gcov"),
        ('gcov-glob=', None, "Paths to ignore during gcov gathering (comma separated)"),
        ('gcov-exec=', None, "gcov executable to run. Defaults to 'gcov'"),
        ('gcov-args=', None, "extra arguments to pass to gcov"),

        # ======================== Advanced ========================
        ('disable=', 'X', "Disable features. Accepting **search** to disable crawling through directories, **detect** to disable detecting CI provider, **gcov** disable gcov commands, `pycov` disables running python `coverage xml`, **fix** to disable report adjustments http://bit.ly/1O4eBpt"),
        ('root=', None, "Project directory. Default: current direcory or provided in CI environment variables"),
        ('commit=', 'c', "Commit sha, set automatically"),
        ('branch=', 'b', "Branch name"),
        ('build=', None, "Specify a custom build number to distinguish ci jobs, provided automatically for supported ci companies"),
        ('pr=', None, "Specify a custom pr number, provided automatically for supported ci companies"),
        ('tag=', None, "Git tag"),

        # ======================== Enterprise ======================== #
        ('slug=', 'r', "Specify repository slug for Enterprise ex. owner/repo"),
        ('url=', 'u', "Your Codecov endpoint"),
        ('cacert=', None, "Certificate pem bundle used to verify with your Codecov instance"),

        # ======================== Debugging ======================== #
        ('dump', None, "Dump collected data and do not send to Codecov"),
        ('verbose', 'v', "Not configured yet"),
        ('no-color', None, "Do not output with color"),

    ]

    def get_list(self, string):
        for sep in ('\n', ','):
            if sep in string:
                return [line.strip() for line in string.split(sep)]
        return []

    def initialize_options(self):

        # ======================== Basics ======================== #
        self.version = None #section.getboolean('version', fallback=False)
        self.token = None #section.get('token', fallback=None)
        self.files = None

        self.flags = None #self.get_list(section.get('flags', fallback=''))
        self.env = None #self.get_list(section.get('env', fallback=''))
        self.required = False
        self.name = None #section.get('name', fallback=None)

        # ======================== gcov ======================== #
        self.gcov_root = None #section.get('gcov-root', fallback=None)
        self.gcov_glob = None #self.get_list(section.get('gcov-glob', fallback=''))
        self.gcov_exec = None #section.get('gcov-exec', fallback=None)
        self.gcov_args = None #section.get('gcov-args', fallback=None)

        # ======================== Advanced ======================== #
        self.disable = None #[]
        self.root = None
        self.commit = None
        self.branch = None
        self.build = None
        self.pr = None
        self.tag = None

        # ======================== Enterprise ======================== #
        self.slug = None
        self.url = None
        self.cacert = None

        # ======================== Debugging ======================== #
        self.dump = False
        self.no_color = False

    def finalize_options(self):
        self.parse_conf()
        self.parse_args()

    def parse_args(self):
        argparser = ArgumentParser()
        for _long, short, _ in self.user_options:
            names = ['--'+_long.rstrip('=')]
            if short is not None:
                names.append('-'+short)
            options = {} if _long.endswith('=') else {'action': 'store_true'}
            argparser.add_argument(*names, **options)

        argparser.parse_args(
            self.distribution.script_args[1:], namespace=self)

    def parse_conf(self):

        parser = ConfigParser()
        parser.read(['setup.cfg'])
        section = parser['codecov'] if 'codecov' in parser else parser['DEFAULT']

        # ======================== Basics ======================== #
        self.version = section.getboolean('version', fallback=False)
        if 'files' in section: self.files = self.get_list(section.get('files'))
        elif 'file' in section: self.files = [section.get('file')]
        self.token = section.get('token', fallback=None)
        if 'flags' in section: self.flags = self.get_list(section.get('flags'))
        self.required = section.getboolean('required', fallback=None)
        if 'env' in section: self.env = self.get_list(section.get('env'))
        self.name = section.get('name', fallback=None)

        # ======================== gcov ======================== #
        self.gcov_root = section.get('gcov-root', fallback=None)
        if 'gcov-glob' in section: self.gcov_glob = self.get_list(section.get('gcov-glob'))
        self.gcov_exec = section.get('gcov-exec', fallback=None)
        self.gcov_args = section.get('gcov-args', fallback=None)

        # ======================== Advanced ======================== #
        if 'disable' in section: self.disable = self.get_list(section.get('disable'))
        self.root = section.get('root', fallback=None)
        self.commit = section.get('commit', fallback=None)
        self.branch = section.get('branch', fallback=None)
        self.build = section.get('build', fallback=None)
        self.pr = section.get('pr', fallback=None)
        self.tag = section.get('tag', fallback=None)

        # ======================== Enterprise ======================== #
        self.slug = section.get('slug', fallback=None)
        self.url = section.get('url', fallback=None)
        self.cacert = section.get('cacert', fallback=None)

        # ======================== Debugging ======================== #
        self.dump = section.get('dump', fallback=None)
        self.no_color = section.get('no-color', fallback=None)

    def run(self):

        self.ensure_finalized()
        if self.version:
            return codecov.main('--version')

        argv = []

        # ======================== Basics ======================== #
        if self.token: argv.extend(['--token', self.token])
        if self.files: argv.extend(['--file'] + self.files)
        if self.flags: argv.extend(['--flags'] + self.flags)
        if self.env: argv.extend(['--env'] + self.env)
        if self.required: argv.append('--required')
        if self.name: argv.extend(['--name', self.name])

        # ======================== gcov ======================== #
        if self.gcov_root is not None: argv.extend(['--gcov-root', self.gcov_root])
        if self.gcov_glob: argv.extend(['--gcov-glob'] + self.gcov_glob)
        if self.gcov_exec is not None: argv.extend(['--gcov-exec', self.gcov_exec])
        if self.gcov_args is not None: argv.extend(['--gcov-args', self.gcov_args])

        # ======================== Advanced ======================== #
        if self.disable: argv.extend(['--disable'] + self.disable)
        if self.root is not None: argv.extend(['--root', self.root])
        if self.commit is not None: argv.extend(['--commit', self.commit])
        if self.branch is not None: argv.extend(['--branch', self.branch])
        if self.build is not None: argv.extend(['--build', self.build])
        if self.pr is not None: argv.extend(['--pr', self.pr])
        if self.tag is not None: argv.extend(['--tag', self.tag])

        # ======================== Enterprise ======================== #
        if self.slug is not None: argv.extend(['--slug', self.slug])
        if self.url is not None: argv.extend(['--url', self.url])
        if self.cacert is not None: argv.extend(['--cacert', self.cacert])

        # ======================== Debugging ======================== #
        if self.dump: argv.append('--dump')
        if self.no_color: argv.append('--no-color')

        print(argv)

        # Patch sys.argv so that if argv is empty,
        # codecov does not see the options passed to setup.py
        sys._argv, sys.argv = sys.argv, []
        return_code = codecov.main(*argv)
        sys.argv = sys._argv
        del sys._argv

        if return_code:
            sys.exit(return_code)
