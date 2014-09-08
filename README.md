[codecov][1] [![Build Status](https://secure.travis-ci.org/codecov/codecov-python.svg?branch=master)](http://travis-ci.org/codecov/codecov-python) [![codecov.io](https://codecov.io/github/codecov/codecov-python/coverage.svg?branch=master)](https://codecov.io/github/codecov/codecov-python)
----------

```sh
pip install codecov
```

## Usage

```sh
pip install codecov
codecov --token=<repo token>
```

# [![travis-org](https://avatars2.githubusercontent.com/u/639823?v=2&s=50)](https://travis-ci.org) Travis C
> Append to your `.travis.yml`

```yml
install:
    pip install codecov
after_success:
    codecov
```

> ### Start testing with [Travis](https://travis-ci.org/)

# [![codeship](https://avatars1.githubusercontent.com/u/2988541?v=2&s=50)](https://codeship.io/) Codeship
> Append to your `Test Commands` *after* your test commands

```sh
pip install codecov
codecov --token=<repo token>
```

> ### Start testing with [Codeship](https://codeship.io/)


# [![circleci](https://avatars0.githubusercontent.com/u/1231870?v=2&s=50)](https://circleci.com/) Circle CI
> Append to your `circle.yml` file

```yml
test:
    post:
        - pip install codecov
        - codecov --token=<repo token>
```
> ### Start testing with [Circle CI](https://circleci.com/)

# Manually
> In shell, from your **project root**

```sh
pip install codecov
codecov --token=<repo token>
```


| [https://codecov.io/][1] | [@codecov][2] | [hello@codecov.io][3] |
| ------------------------ | ------------- | --------------------- |

-----


[1]: https://codecov.io/
[2]: https://twitter.com/codecov
[3]: mailto:hello@codecov.io

## Copyright

> Copyright 2014 codecov
