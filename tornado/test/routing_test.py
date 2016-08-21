from tornado.routing import HandlerMatch
from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application, RequestHandler


class SimpleRegexHandler(RequestHandler):
    def get(self, *args, **kwargs):
        self.finish('simple-regex')


class CustomRouterHandler(RequestHandler):
    def get(self, *args, **kwargs):
        self.finish(self.reverse_url('custom_router'))


class TestRouter(object):
    def __init__(self, app):
        self.app = app
        self.routes = {}

    def add_handlers(self, handlers):
        self.routes.update(handlers)

    def find_handler(self, request):
        if request.path in self.routes:
            return HandlerMatch(
                handler=self.routes[request.path](self.app, request), args=[], kwargs={}
            )

        return None

    def reverse_url(self, name, *args):
        handler_path = '/' + name
        return handler_path if handler_path in self.routes else None


class HandlerBaseTestCase(AsyncHTTPTestCase):
    def get_app(self):
        app = Application([
            ("/simple_regex", SimpleRegexHandler)
        ])

        router = TestRouter(app)
        router.add_handlers({
            "/custom_router": CustomRouterHandler
        })

        app.add_router(router)

        return app

    def test_simple_regex(self):
        response = self.fetch("/simple_regex")
        self.assertEqual(response.body, b"simple-regex")

    def test_custom_router(self):
        response = self.fetch("/custom_router")
        self.assertEqual(response.body, b"/custom_router")
