#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# clicompanion.py - commandline tool.
#
# Copyright 2010 Duane Hinnen, Kenny Meyer
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


import pygtk
pygtk.require('2.0')
import os
import ConfigParser

# import vte and gtk or print error
try:
    import gtk
except:
    error = gtk.MessageDialog (None, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
        _("You need to install the python gtk bindings package 'python-gtk2'"))
    error.run()
    sys.exit (1)
    
try:
    import vte
except:
    error = gtk.MessageDialog (None, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
        _("You need to install 'python-vte' the python bindings for libvte."))
    error.run()
    sys.exit (1)
    
import clicompanionlib.menus_buttons
import clicompanionlib.controller
from clicompanionlib.utils import get_user_shell 
import clicompanionlib.tabs
from clicompanionlib.config import Config


CONFIGFILE = os.path.expanduser("~/.config/clicompanion/config")
CHEATSHEET = os.path.expanduser("~/.clicompanion2")
CONFIG_ORIG = "/etc/clicompanion.d/clicompanion2.config"
CMNDS = [] ## will hold the commands. Actually the first two columns
ROW = '1' ## holds the currently selected row



class MainWindow():

    ## open file containing command list and put it in a variable
    def update(self, liststore):
        try:
            with open(CHEATSHEET, "r") as cheatfile:
                bugdata=cheatfile.read()
                cheatfile.close()
        except IOError:
            ## CHEATSHEET is not there. Oh, no!
            ## So, run self.setup() again.
            self.setup()
            ## Then, run me again.
            self.update(liststore)

        ## add bug data from .clicompanion --> bugdata --> to the liststore
        for line in bugdata.splitlines():
            l = line.split(':',2)
            commandplus = l[0], l[1]
            CMNDS.append(commandplus)
            liststore.append([l[0],l[1],l[2]])

          
    #copy config file to user $HOME if does not exist
    def setup(self):
        """
        Check if ~/.clicompanion2 exists. If not check for original
        installed in /etc/clicompanion.d/. If origianl exists copy to $HOME.
        if not create a new, blank ~/.clicompanion2 so program will not crash
        """

        if not os.path.exists(CHEATSHEET):
            if os.path.exists(CONFIG_ORIG):
                os.system ("cp %s %s" % (CONFIG_ORIG, CHEATSHEET))
            else:
                # Oops! Looks like there's no cheatsheet in CHEATSHEET.
                # Then, create an empty cheatsheet.
                open(CHEATSHEET, 'w').close()
    
    
    #liststore in a scrolled window in an expander
    def expanded_cb(self, expander, params, notebook, treeview, liststore):
        if expander.get_expanded():


            # Activate the search box when expanded
            self.search_box.set_sensitive(True)
        else:
            # De-activate the search box when not expanded
            self.search_box.set_sensitive(False)
            expander.set_expanded(False)
            #expander.remove(expander.child)
            ##reset the size of the window to its original one
            self.window.resize(1, 1)
        return  
        

    # close the window and quit
    def delete_event(self, widget,  data=None):
        gtk.main_quit()
        return False
  
    def __init__(self):
        #import pdb  ##debug
        #pdb.set_trace() ##debug
        
        ##For now TERM is hardcoded to xterm because of a change
        ##in libvte in Ubuntu Maverick
        os.putenv('TERM', 'xterm')

        ## copy command list to user $HOME if does not exist
        self.setup()

        ##create the config file
        conf_mod = Config()
        conf_mod.create_config()

        
        #TODO: do we want to do this? Or just keep the height under 600.
        ##Get user screen size##
        #screen = gtk.gdk.display_get_default().get_default_screen()
        #screen_size = screen.get_monitor_geometry(0)
        #height =  screen.get_height() ## screen height ##
        
        ## Create UI widgets
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        liststore = gtk.ListStore(str, str, str)
        treeview = gtk.TreeView()
        expander = gtk.Expander()
        scrolledwindow = gtk.ScrolledWindow()
        notebook = gtk.Notebook()

        ## set sizes and borders
        scrolledwindow.set_size_request(700, 220)
        window.set_default_size(700, 625)
        window.set_border_width(10)
        ## Sets the position of the window relative to the screen
        window.set_position(gtk.WIN_POS_CENTER_ALWAYS)
        ## Allow user to resize window
        window.set_resizable(True)
        
        
        ## set Window title and icon
        window.set_title("CLI Companion")
        icon = gtk.gdk.pixbuf_new_from_file("/usr/share/pixmaps/clicompanion.16.png")
        window.set_icon(icon)
        
        # get commands and put in liststore
        self.update(liststore) 
        ## create the TreeViewColumns to display the data
        treeview.columns = [None]*3
        treeview.columns[0] = gtk.TreeViewColumn(_('Command'))
        treeview.columns[1] = gtk.TreeViewColumn(_('User Input'))
        treeview.columns[2] = gtk.TreeViewColumn(_('Description'))
        
        for n in range(3):
            ## add columns to treeview
            treeview.append_column(treeview.columns[n])
            ## create a CellRenderers to render the data
            treeview.columns[n].cell = gtk.CellRendererText()
            ## add the cells to the columns
            treeview.columns[n].pack_start(treeview.columns[n].cell,
                                                True)
            ## set the cell attributes to the appropriate liststore column
            treeview.columns[n].set_attributes(
            treeview.columns[n].cell, text=n)   
            treeview.columns[n].set_resizable(True) 
        
        ''' set treeview model and put treeview in the scrolled window
        and the scrolled window in the expander. '''
        treeview.set_model(liststore)
        scrolledwindow.add(treeview)
        expander.add(scrolledwindow)
        #self.window.show_all()

        ## instantiate tabs
        tabs = clicompanionlib.tabs.Tabs()
        ## instantiate controller.Actions, where all the button actions are
        actions = clicompanionlib.controller.Actions()
        ## instantiate 'File' and 'Help' Drop Down Menu [menus_buttons.py]
        bar = clicompanionlib.menus_buttons.FileMenu()
        menu_bar = bar.the_menu(actions, notebook, liststore)
        

        ## get row of a selection
        def mark_selected(self, treeselection):
            global ROW
            (model, pathlist)=treeselection.get_selected_rows()
            ROW = pathlist
            
        ## double click to run a command    
        def treeview_clicked(widget, event):
            if event.button == 1 and event.type == gtk.gdk._2BUTTON_PRESS:
                actions.run_command(self, notebook, liststore)

        ## press enter to run a command                   
        def treeview_button(widget, event):
            keyname = gtk.gdk.keyval_name(event.keyval).upper()
            #print keyname ##debug
            if event.type == gtk.gdk.KEY_PRESS:
                if keyname == 'RETURN':
                    actions.run_command(self, notebook, liststore)
                    

        selection = treeview.get_selection()
        #selection.set_mode(gtk.SELECTION_SINGLE)
        ## open with top command selected
        selection.select_path(0) 
        selection.connect("changed", mark_selected, selection)
        ## double-click
        treeview.connect("button-press-event", treeview_clicked)
        #press enter to run command
        treeview.connect("key-press-event", treeview_button)
        
        
        ## The search section
        search_label = gtk.Label(_("Search:"))
        search_label.set_alignment(xalign=-1, yalign=0)
        search_box = gtk.Entry()
        search_box.connect("changed", actions._filter_commands, liststore, treeview)
        ## search box tooltip
        search_box.set_tooltip_text(_("Search your list of commands"))
        ## Set the search box sensitive OFF at program start, because
        ## expander is not unfolded by default
        search_box.set_sensitive(False)
        ## hbox for menu and search Entry
        menu_search_hbox = gtk.HBox(False)
        menu_search_hbox.pack_end(search_box, True)
        menu_search_hbox.pack_end(search_label, False, False, 10)
        menu_search_hbox.pack_start(menu_bar, True)

        ## expander title
        expander_hbox = gtk.HBox()
        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_INDEX, gtk.ICON_SIZE_BUTTON)
        label = gtk.Label(_('Command List'))
        ## tooltip for the label of the expander
        expander_hbox.set_tooltip_text(_("Click to show/hide command list"))
        
        ## add expander widget to hbox
        expander_hbox.pack_start(image, False, False)
        expander_hbox.pack_start(label, True, False)
        expander.set_label_widget(expander_hbox)

        ## Add the first tab with the Terminal
        tabs.add_tab(self, notebook)
        notebook.set_tab_pos(2)

        ## The "Add Tab" tab
        add_tab_button = gtk.Button("+")
        ## tooltip for "Add Tab" tab
        add_tab_button.set_tooltip_text(_("Click to add another tab"))
        ## create first tab
        notebook.append_page(gtk.Label(""), add_tab_button)
        
        ## buttons at bottom of main window [menus_buttons.py]
        button_box = bar.buttons(actions, 10, gtk.BUTTONBOX_END, notebook, liststore)

        ## vbox for search, notebook, buttonbar
        vbox = gtk.VBox()
        window.add(vbox)
        ## pack everytyhing in the vbox
        #self.vbox.pack_start(menu_bar, False, False,  0) ##menuBar
        vbox.pack_start(menu_search_hbox, False, False, 5)
        vbox.pack_start(expander, False, False, 5)
        vbox.pack_start(notebook, True, True, 5)
        vbox.pack_start(button_box, False, False, 5)
        
        ## signals
        expander.connect('notify::expanded', self.expanded_cb, notebook, treeview, liststore)
        window.connect("delete_event", self.delete_event)
        add_tab_button.connect("clicked", tabs.add_tab, notebook)
        ## right click menu event capture
        treeview.connect ("button_press_event", bar.right_click, actions, treeview, notebook, liststore)


        #self.vte.grab_focus()
        window.show_all()
        return

    def main(self):
        try:
            gtk.main()
        except KeyboardInterrupt:
            pass
        
def run():
    
    main_window = MainWindow()
    main_window.main()
