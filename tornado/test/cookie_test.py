from tornado.test.util import unittest

from tornado.cookie import PatchedSimpleCookie


class PatchedCookieTest(unittest.TestCase):

    def test_correct_cookie(self):
        cookie_parser = PatchedSimpleCookie()

        raw_cookie = '''regions=1;
                     __gfp_64b=2_Zs.24hSBFvVDWb.brHgjdmpsTCVKFjy2M_zyBcBiX.Q7;
                     _xsrf=4c983fe0c9f384e18e610be0fedb468b;
                     _xsrf=4c983fe0c9f384e18e610be0fedb468b;
                     __utma=1.670099261.1429860149.1429860149.1429860149.1;
                     __utmb=1.6.10.1429860149;
                     __utmc=1;
                     __utmz=1.1429860149.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)
                    '''

        cookie_parser.load(raw_cookie)

        self.assertEqual(cookie_parser.get('regions').value, '1')
        self.assertEqual(cookie_parser.get('__gfp_64b').value, '2_Zs.24hSBFvVDWb.brHgjdmpsTCVKFjy2M_zyBcBiX.Q7')
        self.assertEqual(cookie_parser.get('_xsrf').value, '4c983fe0c9f384e18e610be0fedb468b')
        self.assertEqual(cookie_parser.get('__utma').value, '1.670099261.1429860149.1429860149.1429860149.1')
        self.assertEqual(cookie_parser.get('__utmb').value, '1.6.10.1429860149')
        self.assertEqual(cookie_parser.get('__utmc').value, '1')
        self.assertEqual(cookie_parser.get('__utmz').value, '1.1429860149.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)')

    def test_wrong_cookie(self):
        cookie_parser = PatchedSimpleCookie()

        raw_cookie = '''__utma=1.1863264058.1397028550.1428533487.1428615011.6;
                     __utmz=1.1428615011.6.3.utmcsr=trud|utmccn=Trud|utmcmd=meta|utmctr=\x1c0AB5@%20?>%20=0@0I820=8N%20@5A=8F-418924211|utmcct=Trud;
                     __utma=1.1863264058.1397028550.1428531706.1428533487.5;
                     __utmz=1.1428533487.5.2.utmcsr=trud|utmccn=Trud|utmcmd=meta|utmctr=\x1c0AB5@%20?>%20=0@0I820=8N%20@5A=8F-418924211|utmcct=moskva;
                     '''

        cookie_parser.load(raw_cookie)

        self.assertEqual(cookie_parser.get('__utma').value, '1.1863264058.1397028550.1428531706.1428533487.5')
        # wrong cookie because of \x1c char
        self.assertEqual(cookie_parser.get('__utmz').value, '1.1428533487.5.2.utmcsr=trud|utmccn=Trud|utmcmd=meta|utmctr=')
