#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# clicompanion.py - commandline tool.
#
# Copyright 2010 Duane Hinnen
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
#
import os
import ConfigParser

CONFIGDIR = os.path.expanduser("~/.config/clicompanion/")
CONFIGFILE = os.path.expanduser("~/.config/clicompanion/config")
DEFAULTS = { "scrollb": '500',
             "colorf": '#FFFFFF',
             "colorb": '#000000',
             "encoding": 'UTF-8'}

def create_config(conffile=CONFIGFILE):
    configdir = conffile.rsplit(os.sep,1)[0]
    if not os.path.exists(configdir):
        try:
            os.makedirs(configdir)
        except Exception, e:
            print 'Unable to create config at dir %s (%s)'%(configdir,e)
            return False
     # set a number of parameters
    config = ConfigParser.SafeConfigParser()
    config.add_section("terminal")
    for option, value in DEFAULTS.items():
        config.set("terminal", option, value)
    # Writing our configuration file
    with open(CONFIGFILE, 'wb') as f:
       config.write(f)
    print "INFO: Created config file at %s."%conffile
    return config
        

def get_config(conffile=CONFIGFILE, confdir=CONFIGDIR):
    config = None
    if not os.path.isfile(conffile):
        config = create_config(conffile)
    if not config:
        config = ConfigParser.SafeConfigParser(DEFAULTS)
        config.add_section("terminal")
        config.read([conffile])
    return config



