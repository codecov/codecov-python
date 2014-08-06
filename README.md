## Guide

### Travis CI

> Add the following to your Travis yml file

```yml
install:
  - pip install codecov
env:
  global:
    - secure: <encrypted token>
after_success:
  codecov
```

> How to [create a secure environment variable](http://docs.travis-ci.com/user/build-configuration/#Secure-environment-variables)
> **encrypted token** ex. `travis encrypt CODECOV_TOKEN=27518a78-1111-2222-3333-47c0e9846739`. 
> Locate your token at the bottom of your repository page on [codecov.io][1]

[1]: https://codecov.io/
