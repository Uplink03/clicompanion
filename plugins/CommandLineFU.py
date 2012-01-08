#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# CommandLineFu.py - CommandlineFU commands plugin for CLI Comapnion
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


import os
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
import clfu as cc_clf
import clicompanionlib.plugins as plugins


class CommandLineFU(plugins.TabPlugin):
    '''
    Tab with all the commandlinefu commands and search options
    '''
    __authors__ = 'David Caro <david.caro.estevez@gmail.com>'
    __info__ = ('This plugin crates a tab on the commands list that allows you'
        ' to search commands on the CommandlineFU website '
        '(www.commandlinefu.com).')
    __title__ = 'CommandlineFU Commands'

    def __init__(self, config):
        plugins.TabPlugin.__init__(self)
        self.config = config
        self.clfu = cc_clf.CLFu()
        self.pages = []
        ## las_search will store the params of the last search
        self.lastsearch = []

        ## box for commands tags and timerange comboboxes, and refresh
        hbox = gtk.HBox()
        self.pack_start(hbox, False, False, 0)

        ## combobox for selecting command tag
        self.tags_box = gtk.combo_box_new_text()
        self.tags_box.append_text('Update')
        self.tags_box.append_text('None')
        self.tags_box.set_active(1)
        self.tags_box.connect('changed', lambda *x: self.populate_tags())
        hbox.pack_start(gtk.Label(_('Tag:')), False, False, 0)
        hbox.pack_start(self.tags_box, False, False, 0)

        ## time range combobox
        self.trange_box = gtk.combo_box_new_text()
        ## populate time ranges, no http call needed
        for timerange in self.clfu.get_timeranges():
            self.trange_box.append_text(timerange)
        self.trange_box.set_active(0)
        hbox.pack_start(gtk.Label(_('From:')), False, False, 0)
        hbox.pack_start(self.trange_box, False, False, 0)

        ## refresh button
        refresh_btn = gtk.Button("Search")
        refresh_btn.connect("clicked", lambda *x: self.populate())
        hbox.pack_start(refresh_btn, False, False, 0)

        ## add the commands list
        sw = gtk.ScrolledWindow()
        self.liststore = gtk.ListStore(gtk.gdk.Pixbuf, gtk.gdk.Pixbuf,
                                str, str, int, str)
        self.treeview = gtk.TreeView(gtk.TreeModelSort(self.liststore))
        sw.add(self.treeview)
        #self.treeview.set_reorderable(True)
        self.treeview.connect('row-activated', self.clicked)
        self.treeview.connect("button_press_event", self.right_click)
        self.init_cols()
        self.pack_start(sw, True, True, 0)

        ## Get more button
        self.more_btn = gtk.Button("Get more!")
        self.more_btn.connect("clicked",
                lambda *x: self.populate(next_page=True))
        hbox.pack_start(self.more_btn, False, False, 0)
        self.more_btn.set_sensitive(False)

        ## Show everything
        self.show_all()

    def add_pixbuf_col(self, colname, n=0):
        col = gtk.TreeViewColumn()
        col.set_title(colname)
        render_pixbuf = gtk.CellRendererPixbuf()
        col.pack_start(render_pixbuf, expand=True)
        col.add_attribute(render_pixbuf, 'pixbuf', n)
        col.set_resizable(True)
        self.treeview.append_column(col)

    def add_text_col(self, colname, n=0):
        col = gtk.TreeViewColumn()
        col.set_title(_(colname))
        render = gtk.CellRendererText()
        col.pack_start(render, expand=True)
        col.add_attribute(render, 'text', n)
        col.set_resizable(True)
        col.set_sort_column_id(n)
        self.treeview.append_column(col)

    def init_cols(self):
        self.add_pixbuf_col('', 0)
        self.add_pixbuf_col('', 1)
        self.add_text_col('Command', 2)
        self.add_text_col('Summary', 3)
        self.add_text_col('Votes', 4)

    def populate_tags(self):
        dbg('Poulating clf tags')
        tag = self.tags_box.get_active_text()
        if tag == "Update":
            self.tags_box.set_model(gtk.ListStore(str))
            self.tags_box.append_text('Update')
            self.tags_box.append_text('None')
            ## populate commands tags
            for tag, tagid in self.clfu.get_tags():
                self.tags_box.append_text(tag)
            self.tags_box.set_active(1)

    def populate(self, next_page=False, filter_str=''):
        '''
        populate the widgets with the info from the commandlinefu website
        '''
        ## get the filter params, the saved ones if it's a next page request or
        ## the new ones if it's  anew search
        self.liststore.clear()
        if next_page:
            tag, timerange, filter_str = self.lastsearch
            page = len(self.pages)
        else:
            tag = self.tags_box.get_active_text()
            timerange = self.trange_box.get_active_text()
            self.lastsearch = tag, timerange, filter_str
            page = 0
            self.pages = []
        ## get new commands page
        if tag != 'None':
            commands = self.clfu.tag(tag=tag, timerange=timerange, page=page)
        elif filter_str != '':
            commands = self.clfu.search(filter_str, timerange=timerange,
                                page=page)
        else:
            commands = self.clfu.browse(timerange=timerange, page=page)
        ## if there were no results, do avoid requesting more pages, show the
        ## user that there are no more pages
        self.more_btn.set_sensitive(True)
        if not commands or len(commands) < 25:
            self.more_btn.set_sensitive(False)
        ## append it to the revious pages if any
        self.pages.append(commands)
        ## filter and show all the commands
        for page in self.pages:
            for command in page:
                if filter_str != '':
                    if filter_str not in command['command'] \
                    and filter_str not in command['summary']:
                        continue
                add_btn = self.treeview.render_icon(stock_id=gtk.STOCK_ADD,
                                 size=gtk.ICON_SIZE_SMALL_TOOLBAR)
                link_btn = self.treeview.render_icon(stock_id=gtk.STOCK_INFO,
                                 size=gtk.ICON_SIZE_SMALL_TOOLBAR)
                self.liststore.append((add_btn, link_btn,
                        command['command'], command['summary'],
                        int(command['votes']), command['url']))

    def filter(self, search_term):
        """
        Show commands matching a given search term.
        The user should enter a term in the search box and the treeview should
        only display the rows which contain the search term.
        No reordering allowed when filtering.
        """
        ## If the search term is empty, and we change filtering state
        ## restore the liststore, else do nothing
        if search_term == "":
            if self.filtering:
                dbg("Uniltering...")
                self.filtering = False
                self.treeview.set_model(gtk.TreeModelSort(self.liststore))
            return
        dbg("Filtering...")
        self.filtering = True
        modelfilter = self.liststore.filter_new()

        def search(model, iter, search_term):
            cmd, desc = model.get(iter, 2, 3)
            if search_term in ('%s %s' % (cmd, desc)).lower():
                    return True
        modelfilter.set_visible_func(search, search_term)
        self.treeview.set_model(gtk.TreeModelSort(modelfilter))

    def clicked(self, treeview, path, column):
        treeselection = treeview.get_selection()
        model, iter = treeselection.get_selected()
        data = model.get(iter, 2, 3, 4, 5)
        if column == treeview.get_column(0):
            dbg('Adding command %s, %s, %s' % (data[0], '', data[1]))
            self.emit('add_command', data[0], '', data[1])
        elif column == treeview.get_column(1):
            webbrowser.open(data[3])
        else:
            self.emit('run_command', data[0], '', data[1])

    def get_command(self, withurl=False):
        treeselection = self.treeview.get_selection()
        model, iter = treeselection.get_selected()
        if not iter:
            return None, None, None
        cmd, desc, url = model.get(iter, 2, 3, 5)
        if not withurl:
            return cmd, '', desc
        return cmd, '', desc, url


    #right-click popup menu for the Liststore(command list)
    def right_click(self, widget, event):
        if event.button == 3:
            x = int(event.x)
            y = int(event.y)
            time = event.time
            row = self.treeview.get_path_at_pos(x, y)
            if row:
                path, col, x, y = row
            if row:
                popupMenu = gtk.Menu()
                self.treeview.grab_focus()
                self.treeview.set_cursor(path, col, 0)
                data = self.get_command(withurl=True)
                if data[0] == None:
                    return
                # right-click popup menu Apply(run)
                menuPopup1 = gtk.ImageMenuItem(gtk.STOCK_APPLY)
                popupMenu.add(menuPopup1)
                menuPopup1.connect("activate",
                    lambda *x: self.emit('run_command', *data[:-1]))
                # right-click popup menu AddToLocal
                menuPopup2 = gtk.ImageMenuItem(gtk.STOCK_ADD)
                popupMenu.add(menuPopup2)
                menuPopup2.connect("activate",
                    lambda *x: self.emit('add_command', *data[:-1]))
                # right-click popup menu Help
                menuPopup4 = gtk.ImageMenuItem(gtk.STOCK_HELP)
                popupMenu.add(menuPopup4)
                menuPopup4.connect("activate",
                    lambda *x: self.emit('show_man', data[0]))
                # right-click popup menu Online Help
                menuPopup4 = gtk.ImageMenuItem(gtk.STOCK_INFO)
                box = menuPopup4.get_children()[0]
                box.set_label(_('Show online info'))
                popupMenu.add(menuPopup4)
                menuPopup4.connect("activate",
                    lambda wg, url: webbrowser.open(url), data[3])
                # Show popup menu
                popupMenu.show_all()
                popupMenu.popup(None, None, None, event.button, time)
                return True
