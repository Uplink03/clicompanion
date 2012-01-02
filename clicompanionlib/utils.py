#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# clicompanion.py - commandline tool.
#
# Copyright 2010 Duane Hinnen, Kenny Meyer, Marcos Vanetta
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

"""
A collection of useful functions.
"""

import getpass
import os
import sys 
import gtk 
import pwd 
import inspect


## set to True if you want to see more logs
DEBUG = False
DEBUGFILES = False
DEBUGCLASSES = []
DEBUGMETHODS = []

## list gotten from terminator (https://launchpad.net/terminator)
encodings = [
    ["ISO-8859-1", _("Western")],
    ["ISO-8859-2", _("Central European")],
    ["ISO-8859-3", _("South European") ],
    ["ISO-8859-4", _("Baltic") ],
    ["ISO-8859-5", _("Cyrillic") ],
    ["ISO-8859-6", _("Arabic") ],
    ["ISO-8859-7", _("Greek") ],
    ["ISO-8859-8", _("Hebrew Visual") ],
    ["ISO-8859-8-I", _("Hebrew") ],
    ["ISO-8859-9", _("Turkish") ],
    ["ISO-8859-10", _("Nordic") ],
    ["ISO-8859-13", _("Baltic") ],
    ["ISO-8859-14", _("Celtic") ],
    ["ISO-8859-15", _("Western") ],
    ["ISO-8859-16", _("Romanian") ],
    #    ["UTF-7", _("Unicode") ],
    ["UTF-8", _("Unicode") ],
    #    ["UTF-16", _("Unicode") ],
    #    ["UCS-2", _("Unicode") ],
    #    ["UCS-4", _("Unicode") ],
    ["ARMSCII-8", _("Armenian") ],
    ["BIG5", _("Chinese Traditional") ],
    ["BIG5-HKSCS", _("Chinese Traditional") ],
    ["CP866", _("Cyrillic/Russian") ],
    ["EUC-JP", _("Japanese") ],
    ["EUC-KR", _("Korean") ],
    ["EUC-TW", _("Chinese Traditional") ],
    ["GB18030", _("Chinese Simplified") ],
    ["GB2312", _("Chinese Simplified") ],
    ["GBK", _("Chinese Simplified") ],
    ["GEORGIAN-PS", _("Georgian") ],
    ["HZ", _("Chinese Simplified") ],
    ["IBM850", _("Western") ],
    ["IBM852", _("Central European") ],
    ["IBM855", _("Cyrillic") ],
    ["IBM857", _("Turkish") ],
    ["IBM862", _("Hebrew") ],
    ["IBM864", _("Arabic") ],
    ["ISO-2022-JP", _("Japanese") ],
    ["ISO-2022-KR", _("Korean") ],
    ["EUC-TW", _("Chinese Traditional") ],
    ["GB18030", _("Chinese Simplified") ],
    ["GB2312", _("Chinese Simplified") ],
    ["GBK", _("Chinese Simplified") ],
    ["GEORGIAN-PS", _("Georgian") ],
    ["HZ", _("Chinese Simplified") ],
    ["IBM850", _("Western") ],
    ["IBM852", _("Central European") ],
    ["IBM855", _("Cyrillic") ],
    ["IBM857", _("Turkish") ],
    ["IBM862", _("Hebrew") ],
    ["IBM864", _("Arabic") ],
    ["ISO-2022-JP", _("Japanese") ],
    ["ISO-2022-KR", _("Korean") ],
    ["ISO-IR-111", _("Cyrillic") ],
    #    ["JOHAB", _("Korean") ],
    ["KOI8-R", _("Cyrillic") ],
    ["KOI8-U", _("Cyrillic/Ukrainian") ],
    ["MAC_ARABIC", _("Arabic") ],
    ["MAC_CE", _("Central European") ],
    ["MAC_CROATIAN", _("Croatian") ],
    ["MAC-CYRILLIC", _("Cyrillic") ],
    ["MAC_DEVANAGARI", _("Hindi") ],
    ["MAC_FARSI", _("Persian") ],
    ["MAC_GREEK", _("Greek") ],
    ["MAC_GUJARATI", _("Gujarati") ],
    ["MAC_GURMUKHI", _("Gurmukhi") ],
    ["MAC_HEBREW", _("Hebrew") ],
    ["MAC_ICELANDIC", _("Icelandic") ],
    ["MAC_ROMAN", _("Western") ],
    ["MAC_ROMANIAN", _("Romanian") ],
    ["MAC_TURKISH", _("Turkish") ],
    ["MAC_UKRAINIAN", _("Cyrillic/Ukrainian") ],
    ["SHIFT-JIS", _("Japanese") ],
    ["TCVN", _("Vietnamese") ],
    ["TIS-620", _("Thai") ],
    ["UHC", _("Korean") ],
    ["VISCII", _("Vietnamese") ],
    ["WINDOWS-1250", _("Central European") ],
    ["WINDOWS-1251", _("Cyrillic") ],
    ["WINDOWS-1252", _("Western") ],
    ["WINDOWS-1253", _("Greek") ],
    ["WINDOWS-1254", _("Turkish") ],
    ["WINDOWS-1255", _("Hebrew") ],
    ["WINDOWS-1256", _("Arabic") ],
    ["WINDOWS-1257", _("Baltic") ],
    ["WINDOWS-1258", _("Vietnamese") ]
    ]


def dbg(log):
    if DEBUG:
        stack = inspect.stack()
        method = None
        for stackitem in stack:
            parent_frame = stackitem[0]
            names, varargs, keywords, local_vars = inspect.getargvalues(parent_frame)
            ## little trick to get the second stackline method, in case we do 
            ## not find self
            if not method and method != None:
                method = stackitem[3]
            elif not method:
                method = ''
            try:
                self_name = names[0]
                if self_name != 'self':
                    continue
                classname = local_vars[self_name].__class__.__name__
            except IndexError:
                classname = "noclass"
            ## in case self is found, get the method
            method = stackitem[3]
            break
        if DEBUGFILES:
            line = stackitem[2]
            filename = parent_frame.f_code.co_filename
            extra = " (%s:%s)" % (filename, line)
        else:
            extra = ""
        if DEBUGCLASSES != [] and classname not in DEBUGCLASSES:
            return
        if DEBUGMETHODS != [] and method not in DEBUGMETHODS:
            return
        try:
            print >> sys.stderr, "%s::%s: %s%s" % (classname, method, log, extra)
        except IOError:
            pass
    

#TODO: Move this to controller.py
def get_user_shell():
    """Get the user's shell defined in /etc/passwd ."""
    data = None
    try:
        # Read out the data in /etc/passwd
        with open('/etc/passwd') as f:
            data = f.readlines()
    except e:
        print "Something unexpected happened!"
        raise e

    for i in data:
        tmp = i.split(":")
        # Check for the entry of the currently logged in user
        if tmp[0] == getpass.getuser(): 
            # Columns are separated by colons, so split each column.
            # Sample /etc/passwd entry for a user:
            # 
            #  jorge:x:1001:1002:,,,:/home/jorge:/bin/bash
            #
            # The last column is relevant for us.
            # Don't forget to strip the newline at the end of the string!
            return i.split(":")[-1:][0].strip('\n')

class Borg:
    __shared_state = {}
    def __init__(self):
        self.__dict__ = self.__shared_state
