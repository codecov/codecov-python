### `2.1.11`

#### Fixes
- #305 Added option to disable printing of gcov-out
- #308 Handle exceptions that don't have a returncode

#### Dependencies and Misc
- #301 Update to Python 3.9

### `2.1.10`

#### Fixes
- [#148](https://github.com/codecov/codecov-python/pull/148) Output elapsed time with S3 upload
- [#153](https://github.com/codecov/codecov-python/pull/153) Improve error reporting in the "try_run" function and correctly include original command output in the error message
- [#295](https://github.com/codecov/codecov-python/pull/295) Added sleep between upload retries.
- [#297](https://github.com/codecov/codecov-python/pull/297) Ignore emacs lisp files
- [#298](https://github.com/codecov/codecov-python/pull/298) Fix error try_to_run using | without shell=True (fix #284)

#### Dependencies and Misc
- [#290](https://github.com/codecov/codecov-python/pull/290) Bump coverage from 4.5.4 to 5.2.1
- [#291](https://github.com/codecov/codecov-python/pull/291) Update python versions
- [#292](https://github.com/codecov/codecov-python/pull/292) Add license scan report and status
- [#294](https://github.com/codecov/codecov-python/pull/294) Update README with accurate links
- [#296](https://github.com/codecov/codecov-python/pull/296) Bump coverage from 5.2.1 to 5.3

### `2.1.9`

- [#289](https://github.com/codecov/codecov-python/pull/289)Remove token restriction as it is changed server-side

### `2.1.8`

- [#285](https://github.com/codecov/codecov-python/pull/285)Add support for CODECOV_FLAGS
- [#276](https://github.com/codecov/codecov-python/pull/276)Add ability to specify number of upload retries

### `2.1.7`

- [#279](https://github.com/codecov/codecov-python/pull/279) Fix pinned coverage version

### `2.1.6`

- [#275](https://github.com/codecov/codecov-python/pull/275) Fix GitHub Actions implementation

### `2.1.5`

- [#273](https://github.com/codecov/codecov-python/pull/273) Implement retries on Codecov API calls
- [#265](https://github.com/codecov/codecov-python/pull/265) Add GitHub Actions CI detection
- [#267](https://github.com/codecov/codecov-python/pull/267) Add CODECOV_NAME as default for name

### `2.1.4`

- [#260](https://github.com/codecov/codecov-python/pull/260) Enforce black formatting
- [#169](https://github.com/codecov/codecov-python/pull/169) Fix command line quoting on Windows
- [#216](https://github.com/codecov/codecov-python/pull/216) Fix GitLab CI project directory detection on Windows
- [#264](https://github.com/codecov/codecov-python/pull/264) Fix GitLab CI post version 9
- [#262](https://github.com/codecov/codecov-python/pull/262) Check text for NoneType on writes
- [#266](https://github.com/codecov/codecov-python/pull/266) Include the cacert in the PUT call when uploading to S3
- [#263](https://github.com/codecov/codecov-python/pull/263) Fixed gcov not being found in certain instances

### `2.1.3`

- Fix find command not working on Windows
- Add support for gzipping reports
- Dynamic syncing of version

### `2.1.1`

- Fix command when neither hg or git are not available

### `2.1.0`

- Remove x-amz-acl header
- Reformat with Black

### `2.0.22`

- Cleaning TOC generation

### `2.0.21`

- fixed string issues

### `2.0.20`

- fixed broken subprocess handling

### `2.0.19`

- fixed broken subprocess handling

### `2.0.18`

- fixed broken subprocess handling

### `2.0.17`

- fixed reported command injection vulnerability.

### `2.0.16`

- fixed reported command injection vulnerability.

### `2.0.15`

- add `-X s3` to disable direct to S3 uploading

### `2.0.14`

- fixed coverage combine

### `2.0.13`

- fix encoding issues

### `2.0.12`

- revert merge commit fix, back to old way

### `2.0.11`

- fix merge commit when it's a pull request
- remove snapci, business closed
- skip vendor directories for gcov parsing
- run coverage combine not merge
- fix report encoding

### `2.0.10`

- fix uploading when reports contain characters outside of latin-1
- remove reduced_redundancy header from

### `2.0.7`

- Add `--name/-n` to cli
- Add support for Jenkins Blue
- Fix environment variable joining
- Add Greenhouse CI detection
- Fix GitLab detection
- Add default `VCS_*` environment
- Auto-merge py-coverage
- Remove Xcode processing support, please use bash uploader.
- Support yaml:token and yaml:slug

### `2.0.5`

- Use `%20` for encoding spaces [appveyor] https://github.com/codecov/codecov-python/pull/66

### `2.0.4`

- fix detecting merge commits on all CI, not just Travis

### `2.0.3`

- add `-F` to flagging uploads [new feature]
- fixed some reports ascii chars
- added `--pr` flag for manually specifing pulls
- added `--tag` flag for manually git tags
- added env detection for Travis
- added buildkite detection
- added teamcity detection
- added more snapci detection
- detect `codecov.yml` file detection
- depreciating xcode support, use [bash uploader](https://github.com/codecov/codecov-bash)
- hide token from stdout

### `1.6.4`

- fix gitlab project directory
- fallback on git branch/commit
- fix using gcov_exec

### `1.6.0`

- depreciate `--no-fail` now a default
- add `--required` to fail the build if Codecov fails
- added `--cacerts` for enterprise customers
- added fix reports http://bit.ly/1O4eBpt

### `1.5.0`

- fix retreiving mercurial commit
- add support for swift/xcode7 profdata
- now uploading direct-to-s3 to improve product performance
- not require branch, will default to `master` (the default branch)
- fix drone.io commit number, which is not a full 40 sha.

### `1.4.1`

- added `--no-fail` to prevent failing builds when missing configuration or Codecov errors

### `1.4.0`

- Ignore other known bad files/paths
- Added test suite to test against example repositories
- Using `coverage xml -i` to ignore No source for code errors
- Cleaned up command output with help and colors
- Added `gcov` processing, see `codecov --help` for more info.

### `1.3.1`

- Ignore other known bad files/paths
- Fix issue with decoding files in py3+

### `1.3.0`

- Refactor project to be a global uploader for more reports

### `1.2.3`

- Remove `test-results.xml`, not a coverage file
- Add CircleCI container numbers

### `1.2.2`

- bring back client-side pre-processing for jacoco (they can crush)

### `1.2.1`

- accept any file ending in `coverge.xml`

### `1.2.0`

- accept `nosetests.xml` and `test-results.xml` files
- no longer do client side pre-processing, upload raw
- capture SEMAPHORE_CURRENT_THREAD

### `1.1.13`

- added --build arg for advanced usage

### `1.1.10`

- fix package for 2.6 on windows
- fix showing `--help` when called in non-git backed repo
- fix AppVeyor public repos

### `1.1.8`

- support GitLab CI Runner
- added rollbar to help bugs if presented
- added more filepath matching
- pep8 cleanup
- added Shippable ci

### `1.1.7`

- support for D lang added, special thanks to @ColdenCullen
- Wercker CI supported by @Robpol86
- fixed Drone build number

### `1.1.6`

- fix semaphore commit revision number
- preprocess reports from xml

### `1.1.5`

- search for all `lcov|gcov` files
- depreciate `--min-coverage`, use GitHub Status Update feature
- pre-process xml => json

### `1.1.4`

- added support for pyhton 2.6 by @Robpol86
- added AppVeyor support by @Robpol86

### `1.1.3`

- added more ignore paths

### `1.1.2`

- search for `lcov.info` files
- pause for `.1` before checking for min-coverage
- accept `--env` variables which are stored in front-end for build specs

### `1.1.1`

- build python coverage xml only when no reports found to fix overriding reports
- now defaulting output to **plain text**. Use `--json` to return json results
- added `jacocoTestReport.xml` to search list
- changed `--min-coverage` waiting methods to, `5 tries @ 15s` each
- added `Sites/www/bower` and `node_modules` to ignored table of contents
