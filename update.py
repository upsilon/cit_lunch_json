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

import sys
import os
import urllib2
import json
import urlparse
import re
import datetime

class CitLunchJson:
    def __init__(self, base_dir):
        self._base_dir = base_dir
        self._public_dir = os.path.join(base_dir, 'public')
        self._cache_dir = os.path.join(base_dir, 'cache')

        self._fetcher = CitLunchFetcher(self._cache_dir)

    def update(self):
        for name in ['tsuda_dining', 'shiba_dining', 'shiba_kissa']:
            for date, url in self._fetcher.get_index(name + '.html'):
                menu = self._fetcher.get_menu(url)
                filename = '%s/%s/menu.json' % (name, date.strftime('%Y-%m-%d'))
                self._put_json(filename, list(menu))

    def _put_json(self, filename, data):
        fullpath = os.path.join(self._public_dir, filename)
        dirname = os.path.dirname(fullpath)
        if not os.path.exists(dirname):
          os.makedirs(dirname)

        fp = open(fullpath, 'w')
        json.dump(data, fp)
        fp.close()

class CitLunchFetcher:
    base_url = 'http://www.cit-s.com/mobile/'
    version = 'CitLunchFetcher/1.0 (https://udon.upsilo.net/citlunch/)'

    def __init__(self, cache_dir):
        self._cache_dir = cache_dir

    def get_index(self, url = 'tsuda_dining.html'):
        html = self._fetch(url)
        for m in re.finditer(ur'<a href="([^"]+)"[^>]*>(\d+)月(\d+)日', html, re.I):
            year = datetime.date.today().year
            date = datetime.date(year, int(m.group(2)), int(m.group(3)))
            yield (date, m.group(1))

    def get_menu(self, url):
        html = self._fetch(url)
        item = None
        for line in html.splitlines():
            m = re.match(ur'<span[^>]*>▼(.+)</span> \\(\d+).*', line, re.I)
            if m != None:
                if item != None:
                    yield item
                item = {
                    'name': m.group(1),
                    'price': int(m.group(2)),
                    'details': [],
                }
                continue

            m = re.match(ur'・(.+)<br>', line, re.I)
            if m != None:
                item['details'].append(m.group(1))
        yield item

    def _fetch(self, url):
        req = self._make_request(url)

        meta = self._load_cache(url + '.meta')
        if meta != None:
            req.add_header('If-None-Match', meta['etag'])

        try:
            fp = urllib2.urlopen(req)
            html = fp.read()
            etag = fp.info().getheader('ETag')
            fp.close()

            meta = {'etag': etag} if etag else None
            self._write_cache(url, html, meta)
        except urllib2.HTTPError, e:
            if e.code != 304: # Not Modified
                raise
            html = self._load_cache(url)

        return html.decode('shift_jis')

    def _make_request(self, url):
        fullurl = urlparse.urljoin(self.base_url, url)
        req = urllib2.Request(fullurl)
        req.add_header('User-Agent', self.version)
        return req

    def _write_cache(self, filename, contents, meta = None):
        fullpath = os.path.join(self._cache_dir, filename)
        dirname = os.path.dirname(fullpath)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

        contents_fp = open(fullpath, 'w')
        contents_fp.write(contents)
        contents_fp.close()

        if meta != None:
            meta_fp = open(fullpath + '.meta', 'w')
            json.dump(meta, meta_fp)
            meta_fp.close()

    def _load_cache(self, filename):
        fullpath = os.path.join(self._cache_dir, filename)
        try:
            fp = open(fullpath, 'r')
            if filename.endswith('.meta'):
                data = json.load(fp)
            else:
                data = fp.read()
            fp.close()
            return data
        except:
            return None

if __name__ == '__main__':
    lunch = CitLunchJson(os.path.dirname(sys.argv[0]))
    lunch.update()
