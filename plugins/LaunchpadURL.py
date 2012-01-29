#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# LaunchpadURL.py - URL plugin for launchpad bugs, repos and code
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


import pygtk
pygtk.require('2.0')
import gobject
import webbrowser

try:
    import gtk
except:
    ## do not use gtk, just print
    print _("You need to install the python gtk bindings package"
            "'python-gtk2'")
    sys.exit(1)

from clicompanionlib.utils import dbg
import clicompanionlib.plugins as plugins


class LaunchpadURL(plugins.URLPlugin):
    '''
    Match launchpad urls and open them on the browser
    '''
    __authors__ = 'David Caro <david.caro.estevez@gmail.com>'
    __info__ = ('This plugins enables launchpad urls to be matched.')
    __title__ = 'Launchpad URLS'

    def __init__(self, config):
        plugins.URLPlugin.__init__(self, config)
        self.matches = ['lp:[0-9]+',
                        'lp:.*']

    def callback(self, url, matchnum):
        dbg('Openeing launchpad url ' + url)
        if matchnum == 0:
            url = 'http://bugs.launchpad.net/bugs/' + url[3:]
        else:
            url = 'http://code.launchpad.net/+branch/' + url[3:]
        self.open_url(url)
