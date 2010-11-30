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

import pygtk
pygtk.require('2.0')
import gtk
import vte

from clicompanionlib.utils import get_user_shell
import clicompanionlib.controller

class Tabs(object):
      
        
        
    ## add a new terminal in a tab above the current terminal
    def add_tab(self,widget, notebook):

        _vte = vte.Terminal()
        _vte.set_size_request(700, 220)
        _vte.connect ("child-exited", lambda term: gtk.main_quit())
        _vte.fork_command(get_user_shell()) # Get the user's default shell

        vte_tab = gtk.ScrolledWindow()
        vte_tab.add(_vte)
        #notebook.set_show_tabs(True)
        #notebook.set_show_border(True)

        gcp = notebook.get_current_page() +1
        pagenum = ('Tab %d') % gcp

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

        notebook.prepend_page(vte_tab, box) # add tab
        notebook.set_scrollable(True)
        actions = clicompanionlib.controller.Actions()
        _vte.connect ("button_press_event", actions.copy_paste, None)
        vte_tab.grab_focus()
        # signal handler for tab
        closebtn.connect("clicked", self.close_tab, vte_tab, notebook) 
        vte_tab.show_all()

        return vte_tab


    ## Remove a page from the notebook
    def close_tab(self, sender, widget, notebook):
        ## get the page number of the tab we wanted to close
        pagenum = notebook.page_num(widget)
        ## and close it
        notebook.remove_page(pagenum) 
