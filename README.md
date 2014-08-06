codecov.io
----------

> pip install codecov

This repository is your `coverage.xml` uploader


## Travis CI

> Add the following to your `.travis.yml` file

```yml
install:
  - pip install codecov
env:
  global:
    - secure: <encrypted token>
after_success:
  codecov
```

> [**<encrypted token>**][2] ex. `travis encrypt CODECOV_TOKEN=27518a78-1111-2222-3333-47c0e9846739` 
> locate your token at the bottom of your repository page on [codecov.io][1]

[1]: https://codecov.io/
[2]: http://docs.travis-ci.com/user/build-configuration/#Secure-environment-variables
