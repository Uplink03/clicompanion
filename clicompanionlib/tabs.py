#!/usr/bin/env python
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
#

import os
import pygtk
pygtk.require('2.0')
import gtk
import vte
import clicompanionlib.config as cc_config

from clicompanionlib.utils import get_user_shell, dbg
import clicompanionlib.controller
import clicompanionlib.utils as utils
import view


class Tabs(object):
    '''
    add a new terminal in a tab above the current terminal
    '''
    def __init__(self):
        #definition nop - (no of pages) reflects no of terminal tabs left (some may be closed by the user)
        self.nop = 0
        #definition gcp - how many pages is visible
        self.gcp = 0

    def add_tab(self, notebook):
        dbg('Adding a new tab')
        _vte = vte.Terminal()
        if view.NETBOOKMODE == 1:
            _vte.set_size_request(700, 120)
        else:
		    _vte.set_size_request(700, 220) 
       
        _vte.connect("child-exited", lambda term: gtk.main_quit())
        _vte.fork_command(get_user_shell()) # Get the user's default shell
        
        self.update_term_config(_vte)

        vte_tab = gtk.ScrolledWindow()
        vte_tab.add(_vte)
        #notebook.set_show_tabs(True)
        #notebook.set_show_border(True)
        
        self.nop += 1
        self.gcp += 1
        pagenum = ('Tab %d') % self.gcp
        if self.nop > 1:
            dbg('More than one tab, showing them.')
            view.MainWindow.notebook.set_show_tabs(True)
        box = gtk.HBox()
        label = gtk.Label(pagenum)
        box.pack_start(label, True, True)
        
        
        ## x image for tab close button
        close_image = gtk.image_new_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_MENU)
        ## close button
        closebtn = gtk.Button()
        closebtn.set_relief(gtk.RELIEF_NONE)
        closebtn.set_focus_on_click(True)

        closebtn.add(close_image)
        ## put button in a box and show box
        box.pack_end(closebtn, False, False)
        box.show_all()

        view.MainWindow.notebook.prepend_page(vte_tab, box) # add tab
        view.MainWindow.notebook.set_scrollable(True)
        actions = clicompanionlib.controller.Actions()
        _vte.connect("button_press_event", actions.copy_paste, None)
        vte_tab.grab_focus()
        # signal handler for tab
        closebtn.connect("clicked", lambda *x: self.close_tab(vte_tab, notebook))
                
        vte_tab.show_all()

        return vte_tab


    ## Remove a page from the notebook
    def close_tab(self, vte_tab, notebook):
        ## get the page number of the tab we wanted to close
        pagenum = view.MainWindow.notebook.page_num(vte_tab)
        ## and close it
        view.MainWindow.notebook.remove_page(pagenum)
        self.nop -= 1
        if self.nop <= 1:
            view.MainWindow.notebook.set_show_tabs(False)
        
        # check if the focus does not go to the last page (ie with only a + sign)
        if view.MainWindow.notebook.get_current_page() == self.nop:
            view.MainWindow.notebook.prev_page()
        
    def update_all_term_config(self, config=None):
        for pagenum in range(view.MainWindow.notebook.get_n_pages()):
            page = view.MainWindow.notebook.get_nth_page(pagenum)
            dbg(page)
            if isinstance(page, gtk.ScrolledWindow):
                for grandson in page.get_children():
                    dbg(grandson)
                    if isinstance(grandson,vte.Terminal):
                        self.update_term_config(grandson, config)
        
    def update_term_config(self, _vte, config=None):
        ##set terminal preferences from conig file data
        if not config:
            config = cc_config.get_config()
        try:
            config_scrollback = config.getint('terminal', 'scrollb')
        except ValueError:
            print _("WARNING: Invalid value for property 'terminal', int expected:"
                    " got '%s', using default '%s'")%(
                        config.get('terminal', 'scrollb'),
                        config.get('DEFAULT', 'scrollb'))
            config.set('terminal','scrollb',config.get('DEFAULT', 'scrollb'))
            config_scrollback = config.getint('DEFAULT', 'scrollb')
        _vte.set_scrollback_lines(config_scrollback)
        
        color = '#2e3436:#cc0000:#4e9a06:#c4a000:#3465a4:#75507b:#06989a:#d3d7cf:#555753:#ef2929:#8ae234:#fce94f:#729fcf:#ad7fa8:#34e2e2:#eeeeec'
        colors = color.split(':')
        palette = []
        for color in colors:
            if color:
                palette.append(gtk.gdk.color_parse(color))
        
        try:
            config_color_fore = gtk.gdk.color_parse(config.get('terminal', 'colorf'))
        except ValueError, e:
            print _("WARNING: Invalid value for property '%s':"
                    " got '%s', using default '%s'.")%(
                        'colorf',
                        config.get('terminal', 'colorf'),
                        config.get('DEFAULT', 'colorf'))
            config.set('terminal','colorf',config.get('DEFAULT', 'colorf'))
            config_color_fore = gtk.gdk.color_parse(config.get('DEFAULT', 'colorf'))

        try:
            config_color_back = gtk.gdk.color_parse(config.get('terminal', 'colorb'))
        except ValueError, e:
            print _("WARNING: Invalid value for property '%s':"
                    " got '%s', using default '%s'.")%(
                        'colorb',
                        config.get('terminal', 'colorb'),
                        config.get('DEFAULT', 'colorb'))
            config.set('terminal','colorb',config.get('DEFAULT', 'colorb'))
            config_color_back = gtk.gdk.color_parse(config.get('DEFAULT', 'colorb'))
        _vte.set_colors(config_color_fore, config_color_back, palette)
        
        config_encoding = config.get('terminal', 'encoding')
        if config_encoding.upper() not in [ enc.upper() for enc, desc in utils.encodings]:
            print _("WARNING: Invalid value for property '%s':"
                    " got '%s', using default '%s'")%(
                        'encoding',
                        config_encoding,
                        config.get('DEFAULT', 'encoding'))
            config.set('terminal','encoding',config.get('DEFAULT', 'encoding'))
            config_encoding = config.get('DEFAULT', 'encoding')
        _vte.set_encoding(config_encoding)


        
