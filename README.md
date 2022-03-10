[![Donate via PayPal][donate-image]][donate-link]
[![Discord][discord-image]][discord-link]
[![Build][github-ci-image]][github-ci-link]
[![Coverage Status][codecov-image]][codecov-link]
[![PyPI Version][pypi-image]][pypi-link]
[![PyPI - Python Version][python-image]][pypi-link]
![License][license-image-mit]

# ColorAide

> **This is still a work in progress.**
>
> While ColorAide is very usable and out of the alpha stage, it is currently in a prerelease > state. This simply means
> the API could still be in flux to some degree. ColorAide is still technically waiting for > some issues related to CSS
> color syntax and behavior to be decided by the CSS Working Group.

## Overview

ColorAide is a color library for Python with the intent of providing an easy to use interface to work with colors.

```python
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

ColorAide is a continually evolving project, but was created with a number of specific goals in mind:

- Be generally easy to pick up for the average user.

- Support modern CSS color spaces and syntax as well as a number of popular non-CSS color spaces.

- Provide a plugin API to extend color spaces and more.

- Provide a number of useful utilities such as interpolation, color distancing, blending, gamut mapping, etc.

- Allow users to configure defaults to their liking.

With ColorAide, you can specify a color, convert it to other color spaces, mix it with other colors, output it in
different CSS formats, and much more!

# Documentation

https://facelessuser.github.io/coloraide

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
