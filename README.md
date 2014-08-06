## Guide

### Travis CI

> **(1)** Add the following to your Travis yml file
> **(2)** Make sure you create a **coverage.xml** file

```yml
install:
  - pip install codecov
env:
  global:
    - secure: <encrypted string of CODECOV_TOKEN=:your-repo-token>
after_success:
  codecov
```

> How to [create a secure environment variable](http://docs.travis-ci.com/user/build-configuration/#Secure-environment-variables)
