from __future__ import absolute_import, division, print_function, with_statement

from contextlib import closing
from hashlib import md5

from tornado import netutil
from tornado.escape import utf8
from tornado.httpclient import HTTPRequest
from tornado.stack_context import ExceptionStackContext
from tornado.testing import AsyncHTTPTestCase
from tornado.test import httpclient_test
from tornado.test.util import unittest
from tornado.web import Application, RequestHandler

try:
    import pycurl
except ImportError:
    pycurl = None

if pycurl is not None:
    from tornado.curl_httpclient import CurlAsyncHTTPClient


@unittest.skipIf(pycurl is None, "pycurl module not present")
class CurlHTTPClientCommonTestCase(httpclient_test.HTTPClientCommonTestCase):
    def get_http_client(self):
        client = CurlAsyncHTTPClient(io_loop=self.io_loop,
                                     defaults=dict(allow_ipv6=False))
        # make sure AsyncHTTPClient magic doesn't give us the wrong class
        self.assertTrue(isinstance(client, CurlAsyncHTTPClient))
        return client


class DigestAuthHandler(RequestHandler):
    def get(self):
        realm = 'test'
        opaque = 'asdf'
        # Real implementations would use a random nonce.
        nonce = "1234"
        username = 'foo'
        password = 'bar'

        auth_header = self.request.headers.get('Authorization', None)
        if auth_header is not None:
            auth_mode, params = auth_header.split(' ', 1)
            assert auth_mode == 'Digest'
            param_dict = {}
            for pair in params.split(','):
                k, v = pair.strip().split('=', 1)
                if v[0] == '"' and v[-1] == '"':
                    v = v[1:-1]
                param_dict[k] = v
            assert param_dict['realm'] == realm
            assert param_dict['opaque'] == opaque
            assert param_dict['nonce'] == nonce
            assert param_dict['username'] == username
            assert param_dict['uri'] == self.request.path
            h1 = md5(utf8('%s:%s:%s' % (username, realm, password))).hexdigest()
            h2 = md5(utf8('%s:%s' % (self.request.method,
                                     self.request.path))).hexdigest()
            digest = md5(utf8('%s:%s:%s' % (h1, nonce, h2))).hexdigest()
            if digest == param_dict['response']:
                self.write('ok')
            else:
                self.write('fail')
        else:
            self.set_status(401)
            self.set_header('WWW-Authenticate',
                            'Digest realm="%s", nonce="%s", opaque="%s"' %
                            (realm, nonce, opaque))


@unittest.skipIf(pycurl is None, "pycurl module not present")
class CurlHTTPClientTestCase(AsyncHTTPTestCase):
    def setUp(self):
        super(CurlHTTPClientTestCase, self).setUp()
        self.http_client = CurlAsyncHTTPClient(self.io_loop,
                                               defaults=dict(allow_ipv6=False))

    def get_app(self):
        return Application([
            ('/digest', DigestAuthHandler),
        ])

    def test_prepare_curl_callback_stack_context(self):
        exc_info = []

        def error_handler(typ, value, tb):
            exc_info.append((typ, value, tb))
            self.stop()
            return True

        with ExceptionStackContext(error_handler):
            request = HTTPRequest(self.get_url('/'),
                                  prepare_curl_callback=lambda curl: 1 / 0)
        self.http_client.fetch(request, callback=self.stop)
        self.wait()
        self.assertEqual(1, len(exc_info))
        self.assertIs(exc_info[0][0], ZeroDivisionError)

    def test_digest_auth(self):
        response = self.fetch('/digest', auth_mode='digest',
                              auth_username='foo', auth_password='bar')
        self.assertEqual(response.body, b'ok')

    def test_timeout_must_close_connection(self):
        server_sock, port = httpclient_test.bind_unused_port()
        client_sock = [None]

        with closing(server_sock):
            def accept_callback(conn, address):
                client_sock[0] = conn
                conn.recv(1024)

            netutil.add_accept_handler(server_sock, accept_callback, self.io_loop)
            self.http_client.fetch(HTTPRequest("http://127.0.0.1:%d/" % port, request_timeout=1), self.stop)
            response = self.wait()

            self.assertEqual(response.code, 599)

            # The socket must be closed
            client_sock[0].setblocking(0)

            try:
                self.assertEqual(client_sock[0].recv(1024), "", msg="Socket must be closed")
            except IOError as e:
                self.fail("Socket must be closed, but instead %s was raised" % e)
