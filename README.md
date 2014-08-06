codecov.io
----------

> pip install codecov

This repository is your `coverage.xml` uploader


## [Travis CI](https://travis-ci.org)

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


## [Codeship](https://www.codeship.io)

1. Add `CODECOV_TOKEN=:your-repo-token` to your [Environment Variables][3]
2. **Modify your Setup Commands** add `pip install codecov`
3. **Modify your Test Commands** add `codecov :repo`
  - ex for https://github.com/stevepeak/inquiry `codecov stevepeak/inquiry`


[1]: https://codecov.io/
[2]: http://docs.travis-ci.com/user/build-configuration/#Secure-environment-variables
[3]: https://www.codeship.io/documentation/continuous-integration/set-environment-variables/
