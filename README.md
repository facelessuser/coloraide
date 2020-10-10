[![Donate via PayPal][donate-image]][donate-link]
[![Discord][discord-image]][discord-link]
[![Build][github-ci-image]][github-ci-link]
[![Coverage Status][codecov-image]][codecov-link]
![License][license-image-mit]
<!-- [![PyPI Version][pypi-image]][pypi-link]
[![PyPI - Python Version][python-image]][pypi-link] -->

# ColorAide

This is still a work in progress.

## Overview

ColorAide is a color library for Python. It was written to handle most modern CSS colors that are available and that
will be available. Most of the conversion algorithms come straight from the [CSS specifications][css-spec-convert].

In the process of developing this library, we also stumbled upon [`colorjs`][colorjs] which is created/maintained by the
co-authors of some of the recent CSS color specifications. This project became heavily influenced by Color.js. While our
aim was not to port that library, it did leave a clear impression on our API. We also leveraged the work related to
gamut mapping and color interpolation.

Currently this project is in an early stage, and while usable, some things may change as we get closer to a stable
release.

With ColorAide, you can specify a color, convert it to other color spaces, mix it with other colors, output it in
different CSS formats, and various other things.

```py
>>> from coloraide import Color
>>> c = Color("red")
>>> c.to_string()
'rgb(255 0 0)'
>>> c.convert('hsl').to_string()
'hsl(0 100% 50%)'
>>> c.set("lch.chroma", 30).to_string()
'rgb(173.81 114.29 97.218)'
>>> Color("blue").mix("yellow", space="lch").to_string()
'rgb(255 65.751 107.47)'
```

[css-spec-convert]: https://drafts.csswg.org/css-color/#color-conversion-code
[colorjs]: https://github.com/LeaVerou/color.js

# Documentation

https://facelessuser.github.com/coloraide

## License

MIT

[github-ci-image]: https://github.com/facelessuser/coloraide/workflows/build/badge.svg?branch=master&event=push
[github-ci-link]: https://github.com/facelessuser/coloraide/actions?query=workflow%3Abuild+branch%3Amaster
[discord-image]: https://img.shields.io/discord/678289859768745989?logo=discord&logoColor=aaaaaa&color=mediumpurple&labelColor=333333
[discord-link]:https://discord.gg/TWs8Tgr
[codecov-image]: https://img.shields.io/codecov/c/github/facelessuser/coloraide/master.svg?logo=codecov&logoColor=aaaaaa&labelColor=333333
[codecov-link]: https://codecov.io/github/facelessuser/coloraide
[pypi-image]: https://img.shields.io/pypi/v/coloraide.svg?logo=pypi&logoColor=aaaaaa&labelColor=333333
[pypi-link]: https://pypi.python.org/pypi/coloraide
[python-image]: https://img.shields.io/pypi/pyversions/coloraide?logo=python&logoColor=aaaaaa&labelColor=333333
[license-image-mit]: https://img.shields.io/badge/license-MIT-blue.svg?labelColor=333333
[donate-image]: https://img.shields.io/badge/Donate-PayPal-3fabd1?logo=paypal
[donate-link]: https://www.paypal.me/facelessuser
