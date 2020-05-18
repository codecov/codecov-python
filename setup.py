#!/usr/bin/env python
from setuptools import setup

version = "2.1.1"
classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Environment :: Plugins",
    "Intended Audience :: Developers",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: Implementation :: PyPy",
    "License :: OSI Approved :: Apache Software License",
    "Topic :: Software Development :: Testing",
]

setup(
    name="codecov",
    version=version,
    description="Hosted coverage reports for GitHub, Bitbucket and Gitlab",
    long_description=None,
    classifiers=classifiers,
    keywords="coverage codecov code python java scala php",
    author="@codecov",
    author_email="hello@codecov.io",
    url="https://github.com/codecov/codecov-python",
    license="http://www.apache.org/licenses/LICENSE-2.0",
    packages=["codecov"],
    include_package_data=True,
    zip_safe=True,
    install_requires=["requests>=2.7.9", "coverage"],
    entry_points={"console_scripts": ["codecov=codecov:main"]},
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
)
