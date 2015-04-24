from tornado.test.util import unittest

from tornado.cookie import PatchedSimpleCookie


class PatchedCookieTest(unittest.TestCase):

    def test_correct_cookie(self):
        cookie_parser = PatchedSimpleCookie()

        raw_cookie = 'hhuid=DrlybFQqzbbRklTLRSY27A--; ' \
                     'regions=1; ' \
                     '__gfp_64b=2_Zs.24hSBFvVDWb.brHgjdmpsTCVKFjy2M_zyBcBiX.Q7; ' \
                     '_xsrf=4c983fe0c9f384e18e610be0fedb468b; ' \
                     '_xsrf=4c983fe0c9f384e18e610be0fedb468b; ' \
                     'hhrole=anonymous; ' \
                     'GMT=3; ' \
                     '_ym_visorc_156828=b; ' \
                     '_ym_visorc_26843553=w; ' \
                     '__utma=1.670099261.1429860149.1429860149.1429860149.1; ' \
                     '__utmb=1.6.10.1429860149; ' \
                     '__utmc=1; ' \
                     '__utmz=1.1429860149.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)'

        cookie_parser.load(raw_cookie)

        self.assertEqual(cookie_parser.get('hhuid').value, 'DrlybFQqzbbRklTLRSY27A--')
        self.assertEqual(cookie_parser.get('regions').value, '1')
        self.assertEqual(cookie_parser.get('__gfp_64b').value, '2_Zs.24hSBFvVDWb.brHgjdmpsTCVKFjy2M_zyBcBiX.Q7')
        self.assertEqual(cookie_parser.get('_xsrf').value, '4c983fe0c9f384e18e610be0fedb468b')
        self.assertEqual(cookie_parser.get('hhrole').value, 'anonymous')
        self.assertEqual(cookie_parser.get('GMT').value, '3')
        self.assertEqual(cookie_parser.get('_ym_visorc_156828').value, 'b')
        self.assertEqual(cookie_parser.get('_ym_visorc_26843553').value, 'w')
        self.assertEqual(cookie_parser.get('__utma').value, '1.670099261.1429860149.1429860149.1429860149.1')
        self.assertEqual(cookie_parser.get('__utmb').value, '1.6.10.1429860149')
        self.assertEqual(cookie_parser.get('__utmc').value, '1')
        self.assertEqual(cookie_parser.get('__utmz').value, '1.1429860149.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)')

    def test_wrong_cookie(self):
        cookie_parser = PatchedSimpleCookie()

        raw_cookie = '__utma=1.1863264058.1397028550.1428533487.1428615011.6; ' \
                     '__utmz=1.1428615011.6.3.utmcsr=trud|utmccn=Trud|utmcmd=meta|utmctr=\x1c0AB5@%20?>%20=0@0I820=8N%20@5A=8F-418924211|utmcct=Trud; ' \
                     '__gfp_64b=DAXHRNVZPsisC84Q8AE71j4W_85Pzx.3GaL7BMyUwY3.Z7; ' \
                     '__utma=1.1863264058.1397028550.1428531706.1428533487.5; ' \
                     '__utmz=1.1428533487.5.2.utmcsr=trud|utmccn=Trud|utmcmd=meta|utmctr=\x1c0AB5@%20?>%20=0@0I820=8N%20@5A=8F-418924211|utmcct=moskva; ' \
                     '_xsrf=230aa988ca008e947738b9d899fe03b4; ' \
                     '_ym_visorc_156828=b; ' \
                     '_ym_visorc_2646964=b; ' \
                     '_ym_visorc_26843553=w; ' \
                     'ab_nomobile=1; ' \
                     'crypted_id=CC0AA817F12E4363A06A4B0589459688A5471C6F722104504734B32F0D03E9F8; ' \
                     'hhtoken=6SbL80ejmKBXU55S!d6P1WdWt3qf; ' \
                     'hhuid=1PmBTdwOybHfnlNEvIBKaw--; ' \
                     'lt-vc=2; ' \
                     'regions=1; ' \
                     'vishnu1.userid=CC0AA817F12E4363A06A4B0589459688A5471C6F722104504734B32F0D03E9F8'

        cookie_parser.load(raw_cookie)

        self.assertEqual(cookie_parser.get('__gfp_64b').value, 'DAXHRNVZPsisC84Q8AE71j4W_85Pzx.3GaL7BMyUwY3.Z7')
        self.assertEqual(cookie_parser.get('__utma').value, '1.1863264058.1397028550.1428531706.1428533487.5')
        self.assertEqual(cookie_parser.get('_xsrf').value, '230aa988ca008e947738b9d899fe03b4')
        self.assertEqual(cookie_parser.get('_ym_visorc_156828').value, 'b')
        self.assertEqual(cookie_parser.get('_ym_visorc_2646964').value, 'b')
        self.assertEqual(cookie_parser.get('_ym_visorc_26843553').value, 'w')
        self.assertEqual(cookie_parser.get('ab_nomobile').value, '1')
        self.assertEqual(cookie_parser.get('crypted_id').value, 'CC0AA817F12E4363A06A4B0589459688A5471C6F722104504734B32F0D03E9F8')
        self.assertEqual(cookie_parser.get('hhtoken').value, '6SbL80ejmKBXU55S!d6P1WdWt3qf')
        self.assertEqual(cookie_parser.get('hhuid').value, '1PmBTdwOybHfnlNEvIBKaw--')
        self.assertEqual(cookie_parser.get('lt-vc').value, '2')
        self.assertEqual(cookie_parser.get('regions').value, '1')
        self.assertEqual(cookie_parser.get('vishnu1.userid').value,'CC0AA817F12E4363A06A4B0589459688A5471C6F722104504734B32F0D03E9F8')
        # wrong cookie because of \x1c char
        self.assertEqual(cookie_parser.get('__utmz').value, '1.1428533487.5.2.utmcsr=trud|utmccn=Trud|utmcmd=meta|utmctr=')
