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
        gtk.Dialog.__init__(self)
        if not cmd:
            choose_row_error()
            self.cmd = None
            return
        self.cmd = cmd
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

    def run(self):
        if not self.cmd:
            return
        gtk.Dialog.run(self)

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


## Some hlper popus like edit command and so
class CommandInfoWindow(gtk.MessageDialog):
    def __init__(self, cmd, ui, desc):
        self.cmd, self.ui, self.desc = cmd, ui, desc
        gtk.MessageDialog.__init__(self,
            None,
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            gtk.MESSAGE_QUESTION,
            gtk.BUTTONS_OK_CANCEL,
            None)
        self.set_markup(_("This command requires more information."))
        ## create the text input field
        self.entry = gtk.Entry()
        ## allow the user to press enter to do ok
        self.entry.connect("activate", lambda *x: self.response(
                                                    gtk.RESPONSE_OK))
        ## create a horizontal box to pack the entry and a label
        hbox = gtk.HBox()
        hbox.pack_start(gtk.Label(self.ui + ":"), False, 5, 5)
        hbox.pack_end(self.entry)
        ## some secondary text
        self.format_secondary_markup(_("Please provide a " + self.ui))
        ## add it and show it
        self.vbox.pack_end(hbox, True, True, 0)
        self.show_all()
        ## The destroy method must be called otherwise the 'Close' button will
        ## not work.

    def run(self):
        result = False
        while not result:
            result = gtk.MessageDialog.run(self)
            if result == gtk.RESPONSE_OK:
                ui = self.entry.get_text().strip()
                dbg('Got ui "%s"' % ui)
                if not ui:
                    self.show_error()
                    result = None
                try:
                    cmd = self.cmd.format(ui.split(' '))
                except:
                    result = None
            else:
                cmd = None
        self.destroy()
        return cmd

    def show_error(self):
        error = gtk.MessageDialog(None, gtk.DIALOG_MODAL, \
            gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
            _("You need to enter full input. Space separated."))
        error.connect('response', lambda *x: error.destroy())
        error.run()


def choose_row_error():
    dialog = gtk.MessageDialog(
            None,
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            gtk.MESSAGE_QUESTION,
            gtk.BUTTONS_OK,
            None)
    dialog.set_markup(_('You must choose a row to view the help'))
    dialog.show_all()
    dialog.run()
    dialog.destroy()
