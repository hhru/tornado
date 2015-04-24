try:
    import Cookie  # py2
except ImportError:
    import http.cookies as Cookie  # py3


class PatchedSimpleCookie(Cookie.SimpleCookie):
    """A dictionary of Cookie.Morsel objects.
    Due the bug in Cookie module (http://bugs.python.org/issue2193) colon in cookie's name
    will throw an exception in Python < 3.3. We do not want to miss all the cookies when one of them is invalid.
    """
    def load(self, rawdata):
        self.bad_cookies = set()
        self._BaseCookie__set = self._loose_set
        Cookie.SimpleCookie.load(self, rawdata)
        self._BaseCookie__set = self._strict_set

        for key in self.bad_cookies:
            del self[key]

    _strict_set = Cookie.BaseCookie._BaseCookie__set

    def _loose_set(self, key, real_value, coded_value):
        try:
            self._strict_set(key, real_value, coded_value)
        except (Cookie.CookieError, AttributeError):
            self.bad_cookies.add(key)
            dict.__setitem__(self, key, None)


_tc = Cookie.SimpleCookie()
try:
    _tc.load(str('foo:bar=1'))
    SimpleCookie = Cookie.SimpleCookie
except Cookie.CookieError:
    SimpleCookie = PatchedSimpleCookie
