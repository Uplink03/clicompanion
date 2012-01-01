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
import clicompanionlib.utils as utils
from clicompanionlib.utils import dbg

CHEATSHEET = os.path.expanduser("~/.clicompanion2")
CONFIGDIR = os.path.expanduser("~/.config/clicompanion/")
CONFIGFILE = os.path.expanduser("~/.config/clicompanion/config")
CONFIG_ORIG = "/etc/clicompanion.d/clicompanion2.config"
DEFAULTS = { "scrollb": '500',
             "colorf": '#FFFFFF',
             "colorb": '#000000',
             "encoding": 'UTF-8',
             "debug": 'False'}

## To avoid parsing the config file each time, we store the loaded config here
CONFIG = None

def create_config(conffile=CONFIGFILE):
    global CONFIG
    config = CONFIG
    configdir = conffile.rsplit(os.sep,1)[0]
    if not os.path.exists(configdir):
        try:
            os.makedirs(configdir)
        except Exception, e:
            print 'Unable to create config at dir %s (%s)'%(configdir,e)
            return False
    # reuse the config if able
    if not config:
        config = ConfigParser.SafeConfigParser(DEFAULTS)
        # set a number of parameters
        if os.path.isfile(conffile):
            config.read([conffile])
        else:
            config.add_section("terminal")
            for option, value in DEFAULTS.items():
                config.set("terminal", option, value)
        CONFIG = config
    # Writing our configuration file
    save_config(config, conffile)
    print "INFO: Created config file at %s."%conffile
    return config
        

def get_config(conffile=CONFIGFILE, confdir=CONFIGDIR):
    global CONFIG
    config = CONFIG
    if not config:
        dbg('Loading new config')
        if not os.path.isfile(conffile):
            config = create_config(conffile)
        config = ConfigParser.SafeConfigParser(DEFAULTS)
        config.add_section("terminal")
        config.read([conffile])
        CONFIG = config
    else:
        dbg('Reusing config')
    if config.get('terminal','debug') == 'True':
        utils.DEBUG = True
    return config


def save_config(config, conffile=CONFIGFILE):
    dbg('Saving conffile at %s'%conffile)
    with open(CONFIGFILE, 'wb') as f:
        config.write(f)

class Cheatsheet:
    '''
    comtainer class for the cheatsheet

    Example of usage:
    >>> c = config.Cheatsheet()
    >>> c.load('/home/cascara/.clicompanion2')
    >>> c[3]
    ['uname -a', '', 'What kernel am I running\n']
    >>> c.file
    '/home/cascara/.clicompanion2'
    >>> c[2]=[ 'mycmd', 'userui', 'desc' ]
    >>> c[2]
    ['mycmd', 'userui', 'desc']
    >>> del c[2]
    >>> c[2]
    ['ps aux | grep ?', 'search string', 'Search active processes for search string\n']
    >>> c.insert('cmd2','ui2','desc2',2)
    >>> c[2]
    ['cmd2', 'ui2', 'desc2']

    '''
    def __init__(self):
        self.file = CHEATSHEET
        self.commands = []

    def __repr__(self):
        return 'Config: %s - %s'%(self.file, self.commands)
    
    def load(self, cheatfile=None):
        if not cheatfile:
            self.file = CHEATSHEET
            if not os.path.exists(CHEATSHEET):
                if os.path.exists(CONFIG_ORIG):
                    os.system ("cp %s %s" % (CONFIG_ORIG, CHEATSHEET))
                else:
                    # Oops! Looks like there's no default cheatsheet.
                    # Then, create an empty cheatsheet.
                    open(CHEATSHEET, 'w').close()
        else:
            self.file = cheatfile
        try:
            dbg('Reading cheatsheet from file %s'%self.file)
            with open(self.file, 'r') as ch_fd:
                ## try to detect if the line is a old fashines config line
                ## (separated by ':'), when saved will rewrite it
                no_tabs = True
                some_colon = False
                for line in ch_fd:
                    line = line.strip()
                    if not line:
                        continue
                    cmd, ui, desc = line.split('\t',2) + ['',]*(3-len(line.split('\t',2)))
                    if ':' in cmd:
                        some_colon = True
                    if ui or desc:
                        no_tabs = False
                    if cmd and [ cmd, ui, desc ] not in self.commands:
                        self.commands.append([cmd, ui, desc])
                        dbg('Adding command %s'%[cmd, ui, desc])
                if no_tabs and some_colon:
                    ## None of the commands had tabs, and all had ':' in the 
                    ## cmd... most probably old config style
                    print "Detected old cheatsheet style at %s, parsing to new one."%self.file
                    for i in range(len(self.commands)):
                        cmd, ui, desc = self.commands[i]
                        cmd, ui, desc = cmd.split(':',2) + ['',]*(3-len(cmd.split(':',2)))
                        self.commands[i] = [cmd, ui, desc]
                    self.save()
        except IOError, e:
            print "Error loading cheatfile %s: %s"%(self.file, e)

    def save(self, cheatfile=None):
        '''
        Saves the current config to the file cheatfile, or the file that was 
        loaded.
        NOTE: It does not overwrite the value self.file, that points to the file 
        that was loaded
        '''
        if not cheatfile and self.file:
            cheatfile = self.file
        elif not cheatfile:
            return False
        try:
            with open(cheatfile, 'wb') as ch_fd:
                for command in self.commands:
                    ch_fd.write('\t'.join(command)+'\n')
        except IOError, e:
            print "Error writing cheatfile %s: %s"%(cheatfile, e)
            return False
        return True

    def __len__(self):
        return len(self.commands)

    def __getitem__(self, key):
        return self.commands[key]

    def __setitem__(self, key, value):
        try:
            self.insert(*value, pos=key)
        except ValueError, e:
            raise ValueError('Value must be a container with three items, but got %s'%value)

    def __iter__(self):
        for command in self.commands:
            yield command

    def insert(self, cmd, ui, desc, pos=None):
        if not [cmd, ui, desc] in self.commands:
            if not pos:
                self.commands.append([cmd, ui, desc])
            else:
                self.commands.insert(pos, [cmd, ui, desc])

    def append(self, cmd, ui, desc):
        self.insert(cmd, ui, desc)

    def index(self, cmd, ui, value):
        return self.commands.index([cmd, ui, desc])
                    
    def __delitem__(self, key):
        del self.commands[key]
    
    def pop(self, key):
        return self.commands.pop(key)

    def del_by_value(self, cmd, ui, desc):
        if [cmd, ui, desc] in self.commands:
            return self.commands.pop(self.commands.index([cmd, ui, desc]))

    def drag_n_drop(cmd1, cmd2, before=True):
        if cmd1 in self.commands:
            i1 = self.commands.index(cmd1)
            del self.commands[i1]
            if cmd2:
                i2 = self.commands.index(cmd2)
                if before and i1<=i2:
                    self.commands.insert(i2-1, cmd1)
                elif before and i1>i2 or i1<=i2:
                     self.commands.insert(i2, cmd1)
                else:
                     self.commands.insert(i2+1, cmd1)
            else:
                self.commands.append(cmd1)
        else:
            if before:
                self.commands.insert(i2, cmd1)
            else:
                self.commands.insert(i2+1, cmd1)
