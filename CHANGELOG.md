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
