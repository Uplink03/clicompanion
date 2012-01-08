#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# helpers.py - Helper dialogs for clicompanion
#                                                                                                             
# Copyright 2012 Duane Hinnen, Kenny Meyer, Marcos Vanetta, Marek Bardoński,
#                David Caro
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
####
## This file keeps some popups that are shown across the program execution,
## that aren't directly related with a class, like the edit comand popup or the
## about popup, but are too small to be kept in a separate file

import os
import re
import pygtk
pygtk.require('2.0')
import gtk
import subprocess as sp
import shlex
from clicompanionlib.utils import dbg


class ManPage(gtk.Dialog):
    def __init__(self, cmd):
        if not cmd:
            choose_row_error()
            return
        self.cmd = cmd
        gtk.Dialog.__init__(self)
        notebook = gtk.Notebook()
        notebook.set_scrollable(True)
        notebook.popup_enable()
        notebook.set_properties(group_id=0, tab_vborder=0,
                                tab_hborder=1, tab_pos=gtk.POS_TOP)
        ## create a tab for each command
        for command in self.get_commands():
            scrolled_page = gtk.ScrolledWindow()
            scrolled_page.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
            tab = gtk.HBox()
            tab_label = gtk.Label(command)
            tab_label.show()
            tab.pack_start(tab_label)
            page = gtk.TextView()
            page.set_wrap_mode(gtk.WRAP_WORD)
            page.set_editable(False)
            page.set_cursor_visible(False)
            try:
                manpage = sp.check_output(["man", command])
            except sp.CalledProcessError, e:
                manpage = _('Failed to get manpage for command '
                            '"%s"\nReason:\n%s') % (command, e)
            textbuffer = page.get_buffer()
            textbuffer.set_text(manpage)
            scrolled_page.add(page)
            notebook.append_page(scrolled_page, tab)
        self.set_title(_("Man page for %s") % cmd)
        self.vbox.pack_start(notebook, True, True, 0)
        button = gtk.Button("close")
        button.connect_object("clicked", lambda *x: self.destroy(), self)
        button.set_flags(gtk.CAN_DEFAULT)
        self.action_area.pack_start(button, True, True, 0)
        button.grab_default()
        self.set_default_size(500, 600)
        self.show_all()

    def get_commands(self):
        commands = []
        next_part = True
        found_sudo = False
        try:
            for part in shlex.split(self.cmd):
                if next_part:
                    if part == 'sudo' and not found_sudo:
                        found_sudo = True
                        commands.append('sudo')
                    else:
                        if part not in commands:
                            commands.append(part)
                        next_part = False
                else:
                    if part in ['||', '&&', '&', '|']:
                        next_part = True
        except Exception, e:
            return [self.cmd]
        return commands


def show_about():
    dialog = gtk.AboutDialog()
    dialog.set_name('CLI Companion')
    dialog.set_version('1.1')
    dialog.set_authors([u'Duane Hinnen', u'Kenny Meyer', u'Marcos Vanettai',
                        u'Marek Bardoński', u'David Caro'])
    dialog.set_comments(_('This is a CLI Companion program.'))
    dialog.set_license(_('Distributed under the GNU license. You can see it at'
                         '<http://www.gnu.org/licenses/>.'))
    dialog.run()
    dialog.destroy()

