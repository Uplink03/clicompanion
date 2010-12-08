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

CONFIGFILE = os.path.expanduser("~/.config/clicompanion/config")

class Config(object):

    ''' 
    create configuration file
    '''

    

    def create_config(self):
        config = ConfigParser.ConfigParser()
        # set a number of parameters
        config.add_section("terminal")
        config.set("terminal", "scrollb", 500)
        config.set("terminal", "colorf", '#FFFFFF')
        config.set("terminal", "colorb", '#000000')
        config.set("terminal", "encoding", 'utf-8')
        
        

    
        # Writing our configuration file
        with open(CONFIGFILE, 'wb') as f:
            config.write(f)
      
    '''        
    def load_config(self):
        """Load configuration data"""
        if self.loaded is True:
            pass
        else:
            configfile = open(CONFIGFILE, 'wb')
            self.loaded = True
    '''



