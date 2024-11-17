#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# clfu.py - CommandlineFU API librearies for python
#
# Copyright 2012 David Caro <david.caro.estevez@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#
# Inspired by the commandlinefu module by Olivier Hervieu
# <olivier.hervieu@gmail.com>, https://github.com/ohe/commandlinefu

from base64 import b64encode as encodestring
from json import loads
from http.client import HTTPSConnection
from re import search


CLFU_API_HOST = 'www.commandlinefu.com'
CLFU_API_URL = '/commands'

CLFU_API_SORTS = {'date': '',
                   'votes': '/sort-by-votes'}

CLFU_API_RANGES = {'anytime': '',
                    'last day': '/last-day',
                    'last week': '/last-week',
                    'last month': '/last-month'}

## Not sure hot to use tags, needs the tad-id, but there's no easy way to get
## it, so not implemented
CLFU_API_COMMANDS = {'browse': '/browse',
                      'search': '/matching',
                      'tag': '/tagged',
                      'using': '/using'}

CLFU_API_FORMATS = {'json': '/json',
                     'plain': '/plaintext',
                     'rss': '/rss'}

EMPTY = {'json': [],
         'plain': '',
         'rss': ''}

DEBUG = False


def dbg(string):
    if DEBUG:
        print(string)


class CLFu:
    def __init__(self):
        self.conn = HTTPSConnection(CLFU_API_HOST)
        self.tags = {}
        self.page = 0

    def _send_request(self, command, string='', sort='date',
                    form='json', timerange='anytime', page=0):

        import socket
        if string != '' and command == 'search':
            string = '/%s/%s' % (string, encodestring(string)[:-1])
        elif command == 'tag':
            tagid = self.get_tag_id(string)
            if not tagid:
                raise Exception('Tag %s not found.' % string)
            string = '/%s/%s' % (tagid, string)

        if command == 'get_tags':
            request = '/commands/browse'
        else:
            request = CLFU_API_URL \
                 + CLFU_API_COMMANDS[command] \
                 + string \
                 + CLFU_API_SORTS[sort] \
                 + CLFU_API_RANGES[timerange] \
                 + CLFU_API_FORMATS[form] \
                 + '/%s' % (page * 25)

        response = False
        ## try to connect 3 times, closing and opening again if failed
        for i in range(3):
            try:
                if not response:
                    self.conn.close()
                    self.conn.connect()
                dbg('Sending request number %d to: ' % i
                    + CLFU_API_HOST + request)
                self.conn.request('GET', request)
                response = self.conn.getresponse().read()
                return response
            except socket.gaierror as e:
                dbg('Connection failed: %s\nRetrying...' % e)
        return response or EMPTY[form]

    def _send(self, command, string='', sort='date',
              form='json', timerange='anytime', page=0):
        response = self._send_request(command, string, sort, form,
                                    timerange, page)
        if response:
            if form == 'json':
                try:
                    response = loads(response)
                except ValueError as e:
                    raise ValueError(
                        "Error parsing response from Commandlinefu web: "
                        "%s\nResponse:%s" % (e, response))
                except TypeError as e:
                    raise TypeError(
                        "Error parsing response from Commandlinefu"
                        "web: %s\nResponse:%s" % (e, response))
        return response

    def _send_iter(self, command, sort='date', string='',
                   form='json', timerange='anytime', page=0):
        page = 0
        response = 'do not match first time'
        oldresponse = ''
        ## whe check if the response is the same twice, if it is, we stop, to
        ## avoid infinite loops
        while not self._endpage(response, form) and oldresponse != response:
            response = self._send_request(command, string, sort,
                                          form, timerange, page)
            oldresponse == response
            if not response:
                break
            if form == 'json' and response:
                try:
                    for cmd in loads(response):
                        yield cmd
                except ValueError as e:
                    raise ValueError(
                        "Error parsing response from Commandlinefu web: "
                        "%s\nResponse:%s" % (e, response))
                except TypeError as e:
                    raise TypeError(
                        "Error parsing response from Commandlinefu web: "
                        "%s\nResponse:%s" % (e, response))
            elif not self._endpage(response, form) and response != oldresponse:
                yield response
            page = page + 1

    def _endpage(self, page, form):
        if page == 'do not match first time':
            return False
        if form == 'json':
            return [] == loads(page)
        elif form == 'rss':
            endpage = True
            channel = False
            for line in page.split('\n'):
                if line.strip().startswith('<item'):
                    endpage = False
                    break
            return endpage
        elif form == 'plain':
            ## Note: This may change... use the oldresponse failsafe also
            return page == '# commandlinefu.com by David Winterbottom\n\n'

    def browse(self, sort='date', form='json', timerange='anytime', page=0):
        return self._send('browse', sort=sort, form=form,
                          timerange=timerange, page=page)

    def browse_all(self, sort='date', form='json',
                    timerange='anytime', page=0):
        for response in self._send_iter('browse', sort=sort, form=form,
                                        timerange=timerange, page=page):
            yield response

    def search(self, string, sort='date', form='json',
                timerange='anytime', page=0):
        return self._send('search', string, sort, form, timerange, page)

    def search_all(self, string, sort='date', form='json',
                    timerange='anytime', page=0):
        for response in self._send_iter('search', string, sort,
                                        form, timerange, page):
            yield response

    def using(self, string, sort='date', form='json',
                timerange='anytime', page=0):
        return self._send('using', string, sort, form, timerange, page)

    def using_all(self, string, sort='date', form='json',
                    timerange='anytime', page=0):
        for response in self._send_iter('using', string, sort, form,
                                        timerange, page):
            yield response

    def tag(self, tag, sort='date', form='json', timerange='anytime', page=0):
        return self._send('tag', tag, sort, form, timerange, page)

    def tag_iter(self, tag, sort='date', form='json',
                    timerange='anytime', page=0):
        for response in self._send_iter('tag', tag, sort, form,
                                        timerange, page):
            yield response

    def get_tags(self):
        response = str(self._send('get_tags', form='plain'))
        tags_cloud = False
        self.tags = {}
        for line in response.split('\n'):
            if search('<div id="cloud"', line):
                tags_cloud = True
            if tags_cloud and line.strip():
                match = search('/(?P<tagid>\\d+)/(?P<tagname>[^"]+)', line)
                if match:
                    newtag = match.groupdict()
                    self.tags[newtag['tagname']] = newtag['tagid']
                elif search('</div', line):
                    tags_cloud = False
        return self.tags.items()

    def get_tag_id(self, tag):
        if not self.tags:
            dbg('No tags loaded, trying to load them from the web.')
            self.get_tags()
        if tag in self.tags:
            return self.tags[tag]
        else:
            return None

    def get_timeranges(self):
        return sorted(CLFU_API_RANGES.keys())
