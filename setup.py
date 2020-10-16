#!/usr/bin/env python
from codecs import open
import os
from setuptools import setup

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
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: Implementation :: PyPy",
    "License :: OSI Approved :: Apache Software License",
    "Topic :: Software Development :: Testing",
]

filepath = os.path.abspath(os.path.dirname(__file__))

about = {}
with open(os.path.join(filepath, "codecov", "__version__.py"), "r", "utf-8") as f:
    exec(f.read(), about)

setup(
    name=about["__title__"],
    version=about["__version__"],
    description=about["__description__"],
    long_description=None,
    classifiers=classifiers,
    keywords="coverage codecov code python java scala php",
    author=about["__author__"],
    author_email=about["__author_email__"],
    url=about["__url__"],
    license=about["__license__"],
    packages=["codecov"],
    include_package_data=True,
    zip_safe=True,
    install_requires=["requests>=2.7.9", "coverage"],
    entry_points={"console_scripts": ["codecov=codecov:main"]},
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
)
