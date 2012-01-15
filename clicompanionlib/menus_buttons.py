#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# menus_buttons.py - Menus and Buttons for the clicompanion
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
# This file contains the upper menus (class FileMenu), and the lower buttons
# (class Buttons) used in the CLI Companion main window

import gtk
import gobject
import webbrowser
import clicompanionlib.helpers as cc_helpers


class FileMenu(gtk.MenuBar):
    __gsignals__ = {
         'run_command': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                             ()),
         'cancel_command': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                             ()),
         'add_command': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                             ()),
         'remove_command': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                             ()),
         'edit_command': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                             ()),
         'add_tab': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                             ()),
         'close_tab': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                             ()),
         'preferences': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                             ()),
         'quit': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                             ()),
         }

    def __init__(self, config):
        gtk.MenuBar.__init__(self)
        menu = gtk.Menu()
        #color = gtk.gdk.Color(65555, 62000, 65555)
        #menu.modify_bg(gtk.STATE_NORMAL, color)
        root_menu = gtk.MenuItem(_("File"))
        root_menu.set_submenu(menu)

        menu2 = gtk.Menu()
        #color = gtk.gdk.Color(65555, 62000, 60000)
        #menu2.modify_bg(gtk.STATE_NORMAL, color)
        root_menu2 = gtk.MenuItem(_("Help"))
        root_menu2.set_submenu(menu2)

        ##FILE MENU ##
        ## Make 'Run' menu entry
        menu_item1 = gtk.MenuItem(_("Run Command"))
        menu.append(menu_item1)
        menu_item1.connect("activate", lambda *x: self.emit('run_command'))
        menu_item1.show()

        ## Make 'Cancel' menu entry
        menu_item_cancel = gtk.MenuItem(_("Cancel Command"))
        menu.append(menu_item_cancel)
        menu_item_cancel.connect("activate", lambda *x: self.emit('cancel_command'))
        menu_item_cancel.show()

        ## Make 'Add' file menu entry
        menu_item2 = gtk.MenuItem(_("Add Command"))
        menu.append(menu_item2)
        menu_item2.connect("activate", lambda *x: self.emit('add_command'))
        menu_item2.show()

        ## Make 'Remove' file menu entry
        menu_item3 = gtk.MenuItem(_("Remove Command"))
        menu.append(menu_item3)
        menu_item3.connect("activate", lambda *x: self.emit('remove_command'))
        menu_item3.show()

        ## Make 'Add Tab' file menu entry
        menu_item4 = gtk.MenuItem(_("Add Tab"))
        menu.append(menu_item4)
        menu_item4.connect("activate", lambda *x: self.emit('add_tab'))
        menu_item4.show()

        ## Make 'Close Tab' file menu entry
        menu_item4 = gtk.MenuItem(_("Close Tab"))
        menu.append(menu_item4)
        menu_item4.connect("activate", lambda *x: self.emit('close_tab'))
        menu_item4.show()

        ## Make 'User Preferences' file menu entry
        menu_item5 = gtk.MenuItem(_("Preferences"))
        menu.append(menu_item5)
        menu_item5.connect("activate", lambda *x: self.emit('preferences'))
        menu_item5.show()

        ## Make 'Quit' file menu entry
        menu_item6 = gtk.MenuItem(_("Quit"))
        menu.append(menu_item6)
        menu_item6.connect("activate", lambda *x: self.emit('quit'))
        menu_item6.show()

        ## HELP MENU ##
        ## Make 'About' file menu entry
        menu_item11 = gtk.MenuItem(_("About"))
        menu2.append(menu_item11)
        menu_item11.connect("activate", lambda *x: cc_helpers.show_about())
        menu_item11.show()

        ## Make 'Help' file menu entry
        menu_item22 = gtk.MenuItem(_("Help-online"))
        menu2.append(menu_item22)
        menu_item22.connect("activate", lambda *x: webbrowser.open(
                                        "http://launchpad.net/clicompanion"))
        menu_item22.show()

        self.append(root_menu)  # Menu bar(file)
        self.append(root_menu2)  # Menu bar(help)
        self.show_all()


class Buttons(gtk.Frame):
    __gsignals__ = {
         'run_command': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                             ()),
         'cancel_command': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                             ()),
         'add_command': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                             ()),
         'remove_command': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                             ()),
         'edit_command': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                             ()),
         'add_tab': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                             ()),
         'show_man': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                             ()),
         'quit': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                             ()),
         }

    #button box at bottom of main window
    def __init__(self, spacing, layout):
        gtk.Frame.__init__(self)
        bbox = gtk.HButtonBox()
        bbox.set_border_width(5)
        self.add(bbox)

        # Set the appearance of the Button Box
        bbox.set_layout(layout)
        bbox.set_spacing(spacing)
        # Run button
        buttonRun = gtk.Button(stock=gtk.STOCK_EXECUTE)
        bbox.add(buttonRun)
        buttonRun.connect("clicked", lambda *x: self.emit('run_command'))
        buttonRun.set_tooltip_text(_("Click to run a highlighted command"))

        # Cancel button
        buttonCancel = gtk.Button(stock=gtk.STOCK_CANCEL)
        bbox.add(buttonCancel)
        buttonCancel.connect("clicked", lambda *x: self.emit('cancel_command'))
        buttonCancel.set_tooltip_text(_("Click to cancel the running command"))
        
        # Add button
        buttonAdd = gtk.Button(stock=gtk.STOCK_ADD)
        bbox.add(buttonAdd)
        buttonAdd.connect("clicked", lambda *x: self.emit('add_command'))
        buttonAdd.set_tooltip_text(_("Click to add a command to your"
                                     "command list"))
        # Edit button
        buttonEdit = gtk.Button(stock=gtk.STOCK_EDIT)
        bbox.add(buttonEdit)
        buttonEdit.connect("clicked", lambda *x: self.emit('edit_command'))
        buttonEdit.set_tooltip_text(_("Click to edit a command in your "
                                      "command list"))
        # Delete button
        buttonDelete = gtk.Button(stock=gtk.STOCK_DELETE)
        bbox.add(buttonDelete)
        buttonDelete.connect("clicked", lambda *x: self.emit('remove_command'))
        buttonDelete.set_tooltip_text(_("Click to delete a command in your "
                                        "command list"))
        #Help Button
        buttonHelp = gtk.Button(stock=gtk.STOCK_HELP)
        bbox.add(buttonHelp)
        buttonHelp.connect("clicked", lambda *x: self.emit('show_man'))
        buttonHelp.set_tooltip_text(_("Click to get help with a command in "
                                      "your command list"))
        #AddTab Button
        button_addtab = gtk.Button(stock=gtk.STOCK_NEW)
        bbox.add(button_addtab)
        # Very ugly and nasty hack...
        box = button_addtab.get_children()[0].get_children()[0]
        lbl = box.get_children()[1]
        lbl.set_text(_('Add tab'))
        button_addtab.connect("clicked", lambda *x: self.emit('add_tab'))
        button_addtab.set_tooltip_text(_("Click to add a terminal tab"))
        # Cancel button
        buttonCancel = gtk.Button(stock=gtk.STOCK_QUIT)
        bbox.add(buttonCancel)
        buttonCancel.connect("clicked", lambda *x: self.emit('quit'))
        buttonCancel.set_tooltip_text(_("Click to quit CLI Companion"))
        self.show_all()
