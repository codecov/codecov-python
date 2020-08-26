# Codecov Global Python Uploader

[![codecov.io](https://codecov.io/github/codecov/codecov-python/coverage.svg?branch=master)](https://codecov.io/github/codecov/codecov-python)
![PyPI](https://img.shields.io/pypi/v/codecov)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2Fcodecov%2Fcodecov-python.svg?type=shield)](https://app.fossa.com/projects/git%2Bgithub.com%2Fcodecov%2Fcodecov-python?ref=badge_shield)
=======
| [Support][1] | [Documentation][2] | [Community Boards][3] | [Twitter][4] |
| ------------ | ------------------ | --------------------- | ------------ |

Find coverage reports for all the [languages below](#languages), gather them and submit them to Codecov.

## Codecov Features
- Reports are **automatically** combined with no extra setup. Each build is stored separately and combined.
- Multiple languages are supported in a single upload and repository.
- *Optionally* stores environment variables per build.


## Usage

```sh
pip install --user codecov && codecov -t <the-repository-upload-token>
```
or
```sh
conda install -c conda-forge codecov && codecov -t <the-repository-upload-token>
```
> `--user` argument not needed for Python projects. [See example here](https://github.com/codecov/example-python).

## Languages
> [Python](https://github.com/codecov/example-python), [C#/.net](https://github.com/codecov/example-csharp), [Java](https://github.com/codecov/example-java), [Node/Javascript/Coffee](https://github.com/codecov/example-node),
> [C/C++](https://github.com/codecov/example-c), [D](https://github.com/codecov/example-d), [Go](https://github.com/codecov/example-go), [Groovy](https://github.com/codecov/example-groovy), [Kotlin](https://github.com/codecov/example-kotlin),
> [PHP](https://github.com/codecov/example-php), [R](https://github.com/codecov/example-r), [Scala](https://github.com/codecov/example-scala), [Xtern](https://github.com/codecov/example-xtend), [Xcode](https://github.com/codecov/example-xcode), [Lua](https://github.com/codecov/example-lua) and more...

## Using `tox`?

Codecov can be set up in your `tox.ini`.

Just please make sure to pass all the necessary environment variables through:

```
[testenv]
passenv = TOXENV CI TRAVIS TRAVIS_* CODECOV_*
deps = codecov>=1.4.0
commands = codecov -e TOXENV
```
> See all the environment variables for other CI providers [here](https://github.com/codecov/codecov-python/blob/master/codecov/__init__.py#L254-L468)


## Configuration

> Below are the most commonly used settings.

| Argument |   Environment   |                                                                    Description                                                                     |
| -------- | --------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| `-t`     | `CODECOV_TOKEN` | Private repo token for uploading                                                                                                                   |
| `-e`     | `CODECOV_ENV`   | List of config vars to store for the build  |
| `-F`     |      | Flag this upload to group coverage reports. Ex. `unittests` or `integration`  |

```yaml
# public repository on Travis CI
install:
  - pip install --user codecov
# or
  - conda install -c conda-forge codecov
after_success:
  - codecov
```

```yaml
# private repository on Travis CI
install:
  - pip install codecov
# or
  - conda install -c conda-forge codecov
after_success:
  - codecov -t the-repository-upload-token
```


## CI Providers
|                       Company                       |                                                                                     Supported                                                                                      |  Token Required  |
| ----------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------- |
| [AppVeyor](https://www.appveyor.com/)                 | Yes [![Build status](https://ci.appveyor.com/api/projects/status/sw18lsj7786bw806/branch/master?svg=true)](https://ci.appveyor.com/project/stevepeak/codecov-python/branch/master) | Private only     |
| [Bamboo](https://www.atlassian.com/software/bamboo)   | `coming soon`                                                                                                                                                                      |                  |
| [Buildbot](https://buildbot.net/)                     | `coming soon` [buildbot/buildbot#1671](https://github.com/buildbot/buildbot/pull/1671)                                                                                             |                  |
| [CircleCI](https://circleci.com/)                     | Yes                                                                                                                                                                                | Private only     |
| [Codeship](https://codeship.com/)                     | Yes                                                                                                                                                                                | Public & Private |
| [Drone.io](https://drone.io/)                         | Yes                                                                                                                                                                                | Public & Private |
| [GitHub Actions](https://github.com/features/actions) | Yes [![Build status](https://github.com/codecov/codecov-python/workflows/Python%20package/badge.svg?branch=master)](https://github.com/codecov/codecov-python/actions?query=workflow%3A%22Python+package%22)                                                                                        | Public & Private |
| [Gitlab CI](https://about.gitlab.com/gitlab-ci/)      | Yes                                                                                                                                                                                | Public & Private |
| [Jenkins](https://jenkins-ci.org/)                    | Yes                                                                                                                                                                                | Public & Private |
| [Magnum CI](https://magnum-ci.com/)                   | Yes                                                                                                                                                                                | Public & Private |
| [Semaphore](https://semaphoreci.com/)                 | Yes                                                                                                                                                                                | Public & Private |
| [Shippable](https://www.shippable.com/)               | Yes                                                                                                                                                                                | Public & Private |
| [Solano Labs](https://www.solanolabs.com/)            | `coming soon`                                                                                                                                                                      |                  |
| [Travis CI](https://travis-ci.org/)                   | Yes [![Build Status](https://secure.travis-ci.org/codecov/codecov-python.svg?branch=master)](https://travis-ci.org/codecov/codecov-python)                                         | Private only     |
| [Wercker](http://wercker.com/)                        | Yes                                                                                                                                                                                | Public & Private |
| Git / Mercurial                                       | Yes (as a fallback)                                                                                                                                                                | Public & Private |


## Troubleshooting

If you're seeing an **HTTP 400 error when uploading reports to S3**, make sure you've updated to at least version 2.1.3.



[1]: https://codecov.io/support/
[2]: https://docs.codecov.io/
[3]: https://community.codecov.io/
[4]: https://twitter.com/codecov

## Copyright

> Copyright 2014-2020 codecov


## License
[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2Fcodecov%2Fcodecov-python.svg?type=large)](https://app.fossa.com/projects/git%2Bgithub.com%2Fcodecov%2Fcodecov-python?ref=badge_large)
