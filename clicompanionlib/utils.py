#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# utils.py - Some helpful functions for clicompanion
#
# Copyright 2010 Duane Hinnen, Kenny Meyer, Marcos Vanetta, David Caro
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
# In this file are implemented some functions that do not need any clicompanion
# class and can somehow be useful in more than one module.

import os
import sys
import gtk
import pwd
import inspect
import re
try:
    import gconf
except ImportError:
    gconf = False



## set to True if you want to see more logs
DEBUG = False
DEBUGFILES = False
DEBUGCLASSES = []
DEBUGMETHODS = []

gconf_cli = None

## list gotten from terminator (https://launchpad.net/terminator)
encodings = [
    ["ISO-8859-1", _("Western")],
    ["ISO-8859-2", _("Central European")],
    ["ISO-8859-3", _("South European")],
    ["ISO-8859-4", _("Baltic")],
    ["ISO-8859-5", _("Cyrillic")],
    ["ISO-8859-6", _("Arabic")],
    ["ISO-8859-7", _("Greek")],
    ["ISO-8859-8", _("Hebrew Visual")],
    ["ISO-8859-8-I", _("Hebrew")],
    ["ISO-8859-9", _("Turkish")],
    ["ISO-8859-10", _("Nordic")],
    ["ISO-8859-13", _("Baltic")],
    ["ISO-8859-14", _("Celtic")],
    ["ISO-8859-15", _("Western")],
    ["ISO-8859-16", _("Romanian")],
    #    ["UTF-7", _("Unicode")],
    ["UTF-8", _("Unicode")],
    #    ["UTF-16", _("Unicode")],
    #    ["UCS-2", _("Unicode")],
    #    ["UCS-4", _("Unicode")],
    ["ARMSCII-8", _("Armenian")],
    ["BIG5", _("Chinese Traditional")],
    ["BIG5-HKSCS", _("Chinese Traditional")],
    ["CP866", _("Cyrillic/Russian")],
    ["EUC-JP", _("Japanese")],
    ["EUC-KR", _("Korean")],
    ["EUC-TW", _("Chinese Traditional")],
    ["GB18030", _("Chinese Simplified")],
    ["GB2312", _("Chinese Simplified")],
    ["GBK", _("Chinese Simplified")],
    ["GEORGIAN-PS", _("Georgian")],
    ["HZ", _("Chinese Simplified")],
    ["IBM850", _("Western")],
    ["IBM852", _("Central European")],
    ["IBM855", _("Cyrillic")],
    ["IBM857", _("Turkish")],
    ["IBM862", _("Hebrew")],
    ["IBM864", _("Arabic")],
    ["ISO-2022-JP", _("Japanese")],
    ["ISO-2022-KR", _("Korean")],
    ["EUC-TW", _("Chinese Traditional")],
    ["GB18030", _("Chinese Simplified")],
    ["GB2312", _("Chinese Simplified")],
    ["GBK", _("Chinese Simplified")],
    ["GEORGIAN-PS", _("Georgian")],
    ["HZ", _("Chinese Simplified")],
    ["IBM850", _("Western")],
    ["IBM852", _("Central European")],
    ["IBM855", _("Cyrillic")],
    ["IBM857", _("Turkish")],
    ["IBM862", _("Hebrew")],
    ["IBM864", _("Arabic")],
    ["ISO-2022-JP", _("Japanese")],
    ["ISO-2022-KR", _("Korean")],
    ["ISO-IR-111", _("Cyrillic")],
    #    ["JOHAB", _("Korean")],
    ["KOI8-R", _("Cyrillic")],
    ["KOI8-U", _("Cyrillic/Ukrainian")],
    ["MAC_ARABIC", _("Arabic")],
    ["MAC_CE", _("Central European")],
    ["MAC_CROATIAN", _("Croatian")],
    ["MAC-CYRILLIC", _("Cyrillic")],
    ["MAC_DEVANAGARI", _("Hindi")],
    ["MAC_FARSI", _("Persian")],
    ["MAC_GREEK", _("Greek")],
    ["MAC_GUJARATI", _("Gujarati")],
    ["MAC_GURMUKHI", _("Gurmukhi")],
    ["MAC_HEBREW", _("Hebrew")],
    ["MAC_ICELANDIC", _("Icelandic")],
    ["MAC_ROMAN", _("Western")],
    ["MAC_ROMANIAN", _("Romanian")],
    ["MAC_TURKISH", _("Turkish")],
    ["MAC_UKRAINIAN", _("Cyrillic/Ukrainian")],
    ["SHIFT-JIS", _("Japanese")],
    ["TCVN", _("Vietnamese")],
    ["TIS-620", _("Thai")],
    ["UHC", _("Korean")],
    ["VISCII", _("Vietnamese")],
    ["WINDOWS-1250", _("Central European")],
    ["WINDOWS-1251", _("Cyrillic")],
    ["WINDOWS-1252", _("Western")],
    ["WINDOWS-1253", _("Greek")],
    ["WINDOWS-1254", _("Turkish")],
    ["WINDOWS-1255", _("Hebrew")],
    ["WINDOWS-1256", _("Arabic")],
    ["WINDOWS-1257", _("Baltic")],
    ["WINDOWS-1258", _("Vietnamese")]
    ]


def dbg(log):
    if DEBUG:
        stack = inspect.stack()
        method = None
        for stackitem in stack:
            parent_frame = stackitem[0]
            names, varargs, keywords, local_vars = \
                        inspect.getargvalues(parent_frame)
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
            print >> sys.stderr, "%s::%s: %s%s" % (classname, method,
                                                    log, extra)
        except IOError:
            pass


def shell_lookup():
    """Find an appropriate shell for the user
    Function copied from the terminator project source code
    www.launchpad.net/terminator"""
    try:
        usershell = pwd.getpwuid(os.getuid())[6]
    except KeyError:
        usershell = None
    shells = [os.getenv('SHELL'), usershell, 'bash',
            'zsh', 'tcsh', 'ksh', 'csh', 'sh']

    for shell in shells:
        if shell is None:
            continue
        elif os.path.isfile(shell):
            dbg('Found shell %s' % (shell))
            return shell
        else:
            rshell = path_lookup(shell)
            if rshell is not None:
                dbg('Found shell %s at %s' % (shell, rshell))
                return rshell
    dbg('Unable to locate a shell')


## replace ? with {0[n]}
def replace(cmnd, num, ran):
    while ran < num:
        replace_cmnd = re.sub('\?', '{0[' + str(ran) + ']}', cmnd, count=1)
        cmnd = replace_cmnd
        ran += 1
    return cmnd


def get_system_font(callback=None):
    """Look up the system font"""
    global gconf_cli
    if not gconf:
        return 'Monospace 10'
    else:
        if not gconf_cli:
            gconf_cli = gconf.client_get_default()
        value = gconf_cli.get(
                    '/desktop/gnome/interface/monospace_font_name')
        if not value:
            return 'Monospace 10'
        system_font = value.get_string()
        if callback:
            gconf_cli.notify_add(
                        '/desktop/gnome/interface/monospace_font_name',
                        callback)
        return system_font


## WARNING: the altgr key is detected as a normal key
def get_keycomb(event):
    keyname = gtk.gdk.keyval_name(event.keyval)
    if event.state & gtk.gdk.CONTROL_MASK:
        keyname = 'ctrl+' + keyname
    if event.state & gtk.gdk.MOD1_MASK:
        keyname = 'alt+' + keyname
    if event.state & gtk.gdk.SHIFT_MASK:
        keyname = 'shift+' + keyname
    return keyname


## WARNING: the altgr key is detected as shift
def only_modifier(event):
    key = gtk.gdk.keyval_name(event.keyval)
    return 'shift' in key.lower() \
        or 'control' in key.lower() \
        or 'super' in key.lower() \
        or 'alt' in key.lower()


### Singleton implementation (kind of)
class Borg:
    __shared_state = {}

    def __init__(self):
        self.__dict__ = self.__shared_state


def get_pid_cwd(pid):
    """Extract the cwd of a PID from proc, given the PID and the /proc path to
    insert it into, e.g. /proc/%s/cwd"""
    try:
        cwd = os.path.realpath('/proc/%s/cwd' % pid)
    except Exception, ex:
        dbg('Unable to get cwd for PID %s: %s' % (pid, ex))
        cwd = '/'
    return cwd
