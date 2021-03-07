# Setup

!!! warning "Currently in Alpha"
    While ColorAide is very usable, it is currently in an alpha stage. While that doesn't necessarily mean been buggy,
    it does mean the API could be unstable.

## Overview

ColorAide is a color library for Python. It was written to handle most modern CSS colors that are available and that
will be available. Most of the conversion algorithms come straight from the [CSS specifications][css-spec-convert].

In the process of developing this library, we also stumbled upon [Color.js][colorjs] which is created/maintained by the
co-authors of some of the recent CSS color specifications. This project became heavily influenced by Color.js. While our
aim was not to port that library, it did leave a clear impression on our API.

With ColorAide, colors in various spaces can be created, converted to other spaces, mixed, manipulated, and output in
different CSS formats.

```pycon3
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

## Installation

ColorAide can be installed via Python's `pip`:

```console
$ pip install coloraide
```

--8<--
refs.txt
--8<--
