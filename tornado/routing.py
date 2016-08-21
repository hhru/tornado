import re
from collections import namedtuple

from tornado import escape
from tornado.escape import utf8
from tornado.log import app_log
from tornado.util import bytes_type, import_object, unicode_type

HandlerMatch = namedtuple('HandlerMatch', ('handler', 'args', 'kwargs'))


class URLSpec(object):
    """Specifies mappings between URLs and handlers."""
    def __init__(self, pattern, handler, kwargs=None, name=None):
        """Parameters:

        * ``pattern``: Regular expression to be matched.  Any groups
          in the regex will be passed in to the handler's get/post/etc
          methods as arguments.

        * ``handler_class``: `RequestHandler` subclass to be invoked.

        * ``kwargs`` (optional): A dictionary of additional arguments
          to be passed to the handler's constructor.

        * ``name`` (optional): A name for this handler.  Used by
          `Application.reverse_url`.
        """
        if not pattern.endswith('$'):
            pattern += '$'
        self.regex = re.compile(pattern)
        assert len(self.regex.groupindex) in (0, self.regex.groups), \
            ("groups in url regexes must either be all named or all "
             "positional: %r" % self.regex.pattern)

        if isinstance(handler, str):
            # import the Module and instantiate the class
            # Must be a fully qualified name (module.ClassName)
            handler = import_object(handler)

        self.handler_class = handler
        self.kwargs = kwargs or {}
        self.name = name
        self._path, self._group_count = self._find_groups()

    def __repr__(self):
        return '%s(%r, %s, kwargs=%r, name=%r)' % \
               (self.__class__.__name__, self.regex.pattern,
                self.handler_class, self.kwargs, self.name)

    def _find_groups(self):
        """Returns a tuple (reverse string, group count) for a url.

        For example: Given the url pattern /([0-9]{4})/([a-z-]+)/, this method
        would return ('/%s/%s/', 2).
        """
        pattern = self.regex.pattern
        if pattern.startswith('^'):
            pattern = pattern[1:]
        if pattern.endswith('$'):
            pattern = pattern[:-1]

        if self.regex.groups != pattern.count('('):
            # The pattern is too complicated for our simplistic matching,
            # so we can't support reversing it.
            return (None, None)

        pieces = []
        for fragment in pattern.split('('):
            if ')' in fragment:
                paren_loc = fragment.index(')')
                if paren_loc >= 0:
                    pieces.append('%s' + fragment[paren_loc + 1:])
            else:
                pieces.append(fragment)

        return (''.join(pieces), self.regex.groups)

    def reverse(self, *args):
        assert self._path is not None, \
            "Cannot reverse url regex " + self.regex.pattern
        assert len(args) == self._group_count, "required number of arguments " \
                                               "not found"
        if not len(args):
            return self._path
        converted_args = []
        for a in args:
            if not isinstance(a, (unicode_type, bytes_type)):
                a = str(a)
            converted_args.append(escape.url_escape(utf8(a), plus=False))
        return self._path % tuple(converted_args)


class SimpleRegexRouter(object):
    def __init__(self, app):
        self.app = app
        self.handlers = []
        self.named_handlers = {}

    def add_handlers(self, host_pattern, host_handlers):
        """Appends the given handlers to our handler list.

        Host patterns are processed sequentially in the order they were
        added. All matching patterns will be considered.
        """
        if not host_pattern.endswith("$"):
            host_pattern += "$"
        handlers = []
        # The handlers with the wildcard host_pattern are a special
        # case - they're added in the constructor but should have lower
        # precedence than the more-precise handlers added later.
        # If a wildcard handler group exists, it should always be last
        # in the list, so insert new groups just before it.
        if self.handlers and self.handlers[-1][0].pattern == '.*$':
            self.handlers.insert(-1, (re.compile(host_pattern), handlers))
        else:
            self.handlers.append((re.compile(host_pattern), handlers))

        for spec in host_handlers:
            if isinstance(spec, (tuple, list)):
                assert len(spec) in (2, 3, 4)
                spec = URLSpec(*spec)
            handlers.append(spec)
            if spec.name:
                if spec.name in self.named_handlers:
                    app_log.warning(
                        "Multiple handlers named %s; replacing previous value",
                        spec.name)
                self.named_handlers[spec.name] = spec

    def find_handler(self, request):
        host = request.host.lower().split(':')[0]
        matches = []

        for pattern, handlers in self.handlers:
            if pattern.match(host):
                matches.extend(handlers)

        # Look for default host if not behind load balancer (for debugging)
        if not matches and "X-Real-Ip" not in request.headers:
            for pattern, handlers in self.handlers:
                if pattern.match(self.app.default_host):
                    matches.extend(handlers)

        if not matches:
            from tornado.web import RedirectHandler

            return HandlerMatch(
                handler=RedirectHandler(self.app, request, url="http://" + self.app.default_host + "/"),
                args=[], kwargs={}
            )

        for spec in matches:
            match = spec.regex.match(request.path)
            if match:
                handler = spec.handler_class(self.app, request, **spec.kwargs)
                args = []
                kwargs = {}

                if spec.regex.groups:
                    # None-safe wrapper around url_unescape to handle
                    # unmatched optional groups correctly
                    def unquote(s):
                        if s is None:
                            return s
                        return escape.url_unescape(s, encoding=None,
                                                   plus=False)
                    # Pass matched groups to the handler.  Since
                    # match.groups() includes both named and unnamed groups,
                    # we want to use either groups or groupdict but not both.
                    # Note that args are passed as bytes so the handler can
                    # decide what encoding to use.

                    if spec.regex.groupindex:
                        kwargs = dict(
                            (str(k), unquote(v))
                            for (k, v) in match.groupdict().items())
                    else:
                        args = [unquote(s) for s in match.groups()]

                return HandlerMatch(handler, args, kwargs)

        return None

    def reverse_url(self, name, *args):
        """Returns a URL path for handler named ``name``

        The handler must be added to the application as a named `URLSpec`.

        Args will be substituted for capturing groups in the `URLSpec` regex.
        They will be converted to strings if necessary, encoded as utf8,
        and url-escaped.
        """
        if name in self.named_handlers:
            return self.named_handlers[name].reverse(*args)

        return None
