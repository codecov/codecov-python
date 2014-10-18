### 1.1.1
- build python coverage xml only when no reports found to fix overriding reports
- now defaulting output to **plain text**. Use `--json` to return json results
- added `jacocoTestReport.xml` to search list
- changed `--min-coverage` waiting methods to, `5 tries @ 15s` each
