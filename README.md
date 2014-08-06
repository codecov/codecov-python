codecov.io
----------

> pip install codecov

This repository is your `coverage.xml` uploader

# Setup

> After you signup, locate your **repository token** at the bottom of your repository page at [codecov.io][1]


## [Travis CI](https://travis-ci.org)

> Add the following to your `.travis.yml` file

```yml
install:
  pip install codecov
after_success:
  codecov
```


## [Codeship](https://www.codeship.io)

1. Add `CODECOV_TOKEN=:your-repo-token` to your [Environment Variables][3]
2. **Modify your Setup Commands** add `pip install codecov`
3. **Modify your Test Commands** add `codecov :repo`
  - ex for https://github.com/stevepeak/inquiry `codecov stevepeak/inquiry`


[1]: https://codecov.io/
[2]: http://docs.travis-ci.com/user/build-configuration/#Secure-environment-variables
[3]: https://www.codeship.io/documentation/continuous-integration/set-environment-variables/
