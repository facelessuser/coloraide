`functools.lru_cache` is your friend in such cases. We actually process all the images on this page with ColorAide
to simulate CVDs. The key to making it a quick and painless process was to cache repetitive operations. When
processing images, it is highly likely that you will be performing the same operations on thousands of identical
pixels. Caching the work you've already done can speed this process up exponentially in most cases. Images with an
abnormal amount of unique, non consecutive pixels may not perform as well without increasing the maximum size.

We can crawl the pixels in a file and using a simple function like below, we will only process a pixel once (at
least until our cache fills and we start having to overwrite existing colors).

=== "CVD"
    ```py
    @lru_cache(maxsize=1024 * 1024)
    def apply_cvd(deficiency, method, severity, p):
        """Apply filter."""

        has_alpha = len(p) > 3
        color = Color('srgb', [x / 255 for x in p[:3]], p[3] / 255 if has_alpha else 1)
        color.cvd(deficiency, severity, in_place=True, method=method)
        color.clip(in_place=True)
        return tuple([int(x * 255) for x in color.coords()]) + ((int(color[-1] * 255),) if has_alpha else tuple())
    ```

=== "Filters"
    ```py
    @lru_cache(maxsize=1024 * 1024)
    def apply_filter(name, amount, space, p):
        """Apply filter."""

        has_alpha = len(p) > 3
        color = Color('srgb', [x / 255 for x in p[:3]], p[3] / 255 if has_alpha else 1)
        color.filter(name, amount, in_place=True, space=space)
        color.clip(in_place=True)
        return tuple([int(x * 255) for x in color.coords()]) + ((int(color[-1] * 255),) if has_alpha else tuple())
    ```

For us, it turned a 10 minute process into a 35 second process^\*^.

\* _Tests were performed using the [Pillow][pillow] library. Results may vary depending on the size of the image, pixel
configuration, number of unique pixels, etc. Increasing the maximum size of the cache can help in certain cases._
