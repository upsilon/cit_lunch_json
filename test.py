#!/usr/bin/env python
# -*- encoding: utf-8 -*-

# CitLunchJson - retrieve lunch menu of CIT cafeteria in JSON format
# Copyright (C) 2013 Kimura Youichi <kim.upsilon@bucyou.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import unittest
import os
import sys
import datetime
import update

class CitLunchFetcherTest(unittest.TestCase):
    class FakeCitLunchFetcher(update.CitLunchFetcher):
        html = ''
        def __init__(self, cache_dir):
            update.CitLunchFetcher.__init__(self, cache_dir)

        def _fetch(self, url):
            return self.html

    def setUp(self):
        cache_dir = os.path.join(os.path.dirname(sys.argv[0]), 'cache')
        self.fetcher = CitLunchFetcherTest.FakeCitLunchFetcher(cache_dir)

    def test_get_index(self):
        self.fetcher.html = ur'''
<SPAN style="color:#6666FF">▼日替ﾒﾆｭｰ</SPAN> <BR>
　<A href="tsuda_d/2-tue.html" accesskey="2">1月8日(火)</A><BR>
　<A href="tsuda_d/3-wed.html" accesskey="3">1月9日(水)</A><BR>
　<A href="tsuda_d/4-thu.html" accesskey="4">1月10日(木)</A><BR>
　<A href="tsuda_d/5-fri.html" accesskey="5">1月11日(金)</A><BR>
　<A href="tsuda_d/6-sat.html" accesskey="6">1月12日(土)</A><BR>
'''
        today = datetime.date.today()
        self.assertEqual(list(self.fetcher.get_index()), [
            (datetime.date(today.year, 1, 8), u'tsuda_d/2-tue.html'),
            (datetime.date(today.year, 1, 9), u'tsuda_d/3-wed.html'),
            (datetime.date(today.year, 1, 10), u'tsuda_d/4-thu.html'),
            (datetime.date(today.year, 1, 11), u'tsuda_d/5-fri.html'),
            (datetime.date(today.year, 1, 12), u'tsuda_d/6-sat.html'),
        ])

    def test_get_menu(self):
        self.fetcher.html = ur'''
<SPAN style="color:#6666FF">▼Aﾗﾝﾁ</SPAN> \300
<BR>
・やきとり丼<BR>
<BR>
<SPAN style="color:#6666FF">▼Bﾗﾝﾁ</SPAN> \300
<BR>
・とんかつ<BR>
<BR>
<SPAN style="color:#6666FF">▼Cﾗﾝﾁ</SPAN> \350
<BR>
・ﾁｰｽﾞｺｰﾝのせﾊﾝﾊﾞｰｸﾞ<BR>
・ﾎﾟﾃﾄﾌﾗｲ<BR>
<BR>
'''
        self.assertEqual(list(self.fetcher.get_menu('hoge.html')), [
          { 'name': u'Aﾗﾝﾁ', 'price': 300, 'details': [u'やきとり丼'] },
          { 'name': u'Bﾗﾝﾁ', 'price': 300, 'details': [u'とんかつ'] },
          { 'name': u'Cﾗﾝﾁ', 'price': 350, 'details': [u'ﾁｰｽﾞｺｰﾝのせﾊﾝﾊﾞｰｸﾞ', u'ﾎﾟﾃﾄﾌﾗｲ'] },
        ])

if __name__ == '__main__':
    unittest.main()
