#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# StandardURLs.py - URL plugin for common urls (http, ftp, etc.)
#
# Copyright 2012 David Caro <david.caro.estevez@gmail.com>
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 3, as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.
#
import sys

import gi

gi.require_version("Gtk", "3.0")

try:
    from gi.repository import Gtk as gtk
except:
    ## do not use gtk, just print
    print(_("You need to install the python gtk bindings package"
            "'python-gtk2'"))
    sys.exit(1)

from clicompanionlib.utils import dbg
import clicompanionlib.plugins as plugins


class StandardURLs(plugins.URLPlugin):
    '''
    Match launchpad urls and open them on the browser
    '''
    __authors__ = 'David Caro <david.caro.estevez@gmail.com>'
    __plugin_info__ = ('This plugins enables some common urls to be matched.')
    __title__ = 'Standard URLS'

    def __init__(self, config):
        plugins.URLPlugin.__init__(self, config)
        self.matches = []

        userchars = "-A-Za-z0-9"
        passchars = "-A-Za-z0-9,?;.:/!%$^*&~\"#'"
        hostchars = "-A-Za-z0-9"
        pathchars = "-A-Za-z0-9_$.+!*(),;:@&=?/~#%'\""
        schemes = ("(news:|telnet:|nntp:|https?:|ftps?:|webcal:)//")
        user = "([" + userchars + "]+(:[" + passchars + "]+)?)?"
        urlpath = "/[" + pathchars + "]*[^]'.}>) \t\r\n,\\\"]"
        email = ("[a-zA-Z0-9][a-zA-Z0-9.+-]*@[a-zA-Z0-9][a-zA-Z0-9-]*"
                "\\.[a-zA-Z0-9][a-zA-Z0-9-]+[.a-zA-Z0-9-]*")

        lboundry = "\\<"
        rboundry = "\\>"

        ## http/https/ftp/ftps/webcal/nntp/telnet urls
        self.matches.append(schemes + user + "[" + hostchars + "]*\\.["
                            + hostchars + ".]+(:[0-9]+)?(" + urlpath + ")?")
        ## file
        self.matches.append('file:///[' + pathchars + "]*")
        ## SIP
        self.matches.append('(callto:|h323:|sip:)'
                + "[" + userchars + "+]["
                + userchars + ".]*(:[0-9]+)?@?["
                + pathchars + "]+"
                + rboundry)
        ## mail
        self.matches.append("(mailto:)?" + email)
        ## news
        self.matches.append('news:[-A-Z\\^_a-z{|}~!"#$%&\'()*+'
                        + ',./0-9;:=?`]+@' + "[-A-Za-z0-9.]+(:[0-9]+)?")
        ## General url (www.host.com or ftp.host.com)
        self.matches.append("(www|ftp)[" + hostchars + "]*\\.["
                + hostchars + ".]+(:[0-9]+)?(" + urlpath + ")?/?")

    def callback(self, url, matchnum):
        dbg('Opening common url ' + url)
        if matchnum == 5:
            if url[:3] == 'www':
                url = 'http://' + url
            else:
                url = 'ftp://' + url
        self.open_url(url)
