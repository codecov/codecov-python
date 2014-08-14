#!/usr/bin/env python
from setuptools import setup

version = '0.0.5'
classifiers = ["Development Status :: 4 - Beta",
               "Environment :: Plugins",
               "Intended Audience :: Developers",
               "License :: OSI Approved :: Apache Software License",
               "Topic :: Software Development :: Testing"]

setup(name='codecov',
      version=version,
      description="Free hosted coverage reports for pubic and private repos",
      long_description=None,
      classifiers=classifiers,
      keywords='coverage codecov code',
      author='codecov.io',
      author_email='hello@codecov.io',
      url='http://github.com/codecov/codecov-python',
      license='http://www.apache.org/licenses/LICENSE-2.0',
      packages=['codecov'],
      include_package_data=True,
      zip_safe=True,
      install_requires=["requests==2.3.0", "coverage==3.7.1"],
      entry_points={'console_scripts': ['codecov=codecov:main']})
