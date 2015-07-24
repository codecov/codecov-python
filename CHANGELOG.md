### `1.2.1`
- accept any file ending in `coverge.xml`
- bring back client-side pre-processing for jacoco (they can crush)

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
- depreciate `--min-coverage`, use Github Status Update feature
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
