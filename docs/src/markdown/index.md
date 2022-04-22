# Introduction

!!! warning "Currently a Prerelease"
    While ColorAide is very usable and out of the alpha stage, it is currently in a prerelease state. This simply means
    the API could still be in flux to some degree. ColorAide is still technically waiting for some issues related to CSS
    color syntax and behavior to be decided by the CSS Working Group.

## What is ColorAide?

ColorAide is a color library for Python with the intent of providing an easy to use interface to work with colors.

```playground
from coloraide import Color
Color('lch(75% 50 0)').steps('lch(75% 50 300)', steps=8, space='lch', hue='longer')
```

ColorAide is a continually evolving project, but was created with a number of specific goals in mind:

- Be generally easy to pick up for the average user.

- Support modern CSS color spaces and syntax as well as a number of popular non-CSS color spaces.

- Provide a plugin API to extend color spaces and more.

- Provide a number of useful utilities such as interpolation, color distancing, blending, gamut mapping, etc.

- Allow users to configure defaults to their liking.

There are many color libraries out there, and ColorAide is not meant to be the _one_ library to replace all other color
libraries. ColorAide focuses on not only trying to be accurate with its colors, but also to be easy to use. Not all
color libraries are easy to pick up and use and can require a user to manage a color's illuminant, be aware of and
manage the full conversion chain to get one color convert to another, and other various intricacies. ColorAide tries to
handle a lot of this so you can go straight to using the colors.

There are some great scientific libraries out there for working with colors. Two libraries that stand out are
[Colour Science][colour-science] and [Colorio][colorio], both of which are fantastic libraries, but are definitely more
geared towards scientific endeavors. They provide a wealth of various spaces, illuminants, access to complex color space
visualizers, and numerous esoteric tools. They use Numpy to greatly speed up calculations as well. If you want to learn
more about colors, these are great libraries to play with, but can be a little more cumbersome to use for the average
user.

While ColorAide could certainly be used to analyze colors, it does not aim to provide scientific tools and mainly
focuses on making color usage easy and accessible in projects using colors. It may in the future add optional Numpy
support to facilitate faster mathematical operations, but we also wanted to ensure that ColorAide could be used as a
pure Python library anywhere as well.

## Installation

ColorAide can be installed via Python's `pip`:

```console
$ pip install coloraide
```
