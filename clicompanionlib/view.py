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
from clicompanionlib.utils import get_user_shell , Borg
import clicompanionlib.tabs
from clicompanionlib.config import Config


CONFIGFILE = os.path.expanduser("~/.config/clicompanion/config")
CHEATSHEET = os.path.expanduser("~/.clicompanion2")
CONFIG_ORIG = "/etc/clicompanion.d/clicompanion2.config"

## Changed two->three columns
CMNDS = [] ## will hold the commands. Actually the first three columns
ROW = '1' ## holds the currently selected row
TARGETS = [
    ('MY_TREE_MODEL_ROW', gtk.TARGET_SAME_WIDGET, 0),
    ('text/plain', 0, 1),
    ('TEXT', 0, 2),
    ('STRING', 0, 3),
    ]

FILTER = 0
NETBOOKMODE = 0
HIDEUI = 0
FULLSCREEN = 0


menu_search_hbox = ''
button_box = ''


class MainWindow(Borg):
    window = gtk.Window(gtk.WINDOW_TOPLEVEL) 
    #color = gtk.gdk.Color(60000, 65533, 60000)
    #window.modify_bg(gtk.STATE_NORMAL, color)
    liststore = gtk.ListStore(str, str, str)	
    treeview = gtk.TreeView()
    expander = gtk.Expander()
    scrolledwindow = gtk.ScrolledWindow()
    notebook = gtk.Notebook()


    screen = gtk.gdk.display_get_default().get_default_screen()
    screen_size = screen.get_monitor_geometry(0)
    height =  screen.get_height() ## screen height ##
    global NETBOOKMODE
    if height < 750:
		NETBOOKMODE = 1
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
            self.update(self.liststore)

        ## add bug data from .clicompanion --> bugdata --> to the liststore
        for line in bugdata.splitlines():
            l = line.split(':',2)
            commandplus = l[0], l[1], l[2]
            CMNDS.append(commandplus)
            self.liststore.append([l[0],l[1],l[2]])

          
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
    def expanded_cb(self, expander, params, window, search_box):
        if expander.get_expanded():

            # Activate the search box when expanded
            search_box.set_sensitive(True)
        else:
            # De-activate the search box when not expanded
            self.search_box.set_sensitive(False)
            expander.set_expanded(False)
            #expander.remove(expander.child)
            ##reset the size of the window to its original one
            window.resize(1, 1)
        return  
        

    # close the window and quit
    def delete_event(self, widget,  data=None):
        gtk.main_quit()
        return False
        
    def key_clicked(self, widget, event):
        actions = clicompanionlib.controller.Actions()
        tabs = clicompanionlib.tabs.Tabs()
        global HIDEUI
        global FULLSCREEN
        global menu_search_hbox
        global button_box
        keyname = gtk.gdk.keyval_name(event.keyval).upper()
        #print keyname ##debug
        if keyname == "F12":
            HIDEUI = 1 - HIDEUI
        if HIDEUI == 1:
            self.treeview.hide_all()
            self.expander.hide_all()
            self.scrolledwindow.hide_all()
            menu_search_hbox.hide_all()
            button_box.hide_all()
        else:
            self.treeview.show_all()
            self.expander.show_all()
            self.scrolledwindow.show_all()
            menu_search_hbox.show_all()
            button_box.show_all()
        if keyname == "F11":
            FULLSCREEN = 1 - FULLSCREEN
        if FULLSCREEN == 1:
            pwin = button_box.get_window()
            pwin.fullscreen()
        else: 
            pwin = button_box.get_window()
            pwin.unfullscreen()
        if keyname == "F4":
			actions.run_command(self, self.notebook, self.liststore)
        if keyname == "F5":
			actions.add_command(self, self.liststore)
        if keyname == "F6":
			actions.remove_command(self, self.liststore)
        if keyname == "F7":
			tabs.add_tab(self, self.notebook)
  
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
        
        
        ## style to reduce padding around tabs
        ## TODO: Find a better place for this? 
    	gtk.rc_parse_string ("style \"tab-close-button-style\"\n"
		     "{\n"
		       "GtkWidget::focus-padding = 0\n"
		       "GtkWidget::focus-line-width = 0\n"
		       "xthickness = 0\n"
		       "ythickness = 0\n"
		     "}\n"
		     "widget \"*.tab-close-button\" style \"tab-close-button-style\"");
        
        ## Create UI widgets

        self.notebook.set_show_tabs(0)

        ##attach the style to the widget
        self.notebook.set_name ("tab-close-button")


        ## set sizes and borders
        global NETBOOKMODE
        if NETBOOKMODE == 1:
            self.scrolledwindow.set_size_request(700, 200)
            self.window.set_default_size(700, 500)
        else:
            self.scrolledwindow.set_size_request(700, 220)
            self.window.set_default_size(700, 625)
        self.window.set_border_width(10)
        ## Sets the position of the window relative to the screen
        self.window.set_position(gtk.WIN_POS_CENTER_ALWAYS)
        ## Allow user to resize window
        self.window.set_resizable(True)
        
        
        ## set Window title and icon
        self.window.set_title("CLI Companion")
        icon = gtk.gdk.pixbuf_new_from_file("/usr/share/pixmaps/clicompanion.16.png")
        self.window.set_icon(icon)
        
        
	   
        # get commands and put in liststore
        self.update(self.liststore) 
        
        ## set renderer and colors

        #color2 = gtk.gdk.Color(5000,5000,65000)
        renderer = gtk.CellRendererText()
        #renderer.set_property("cell-background-gdk", color)
        #renderer.set_property("foreground-gdk", color2)
        
        ## create the TreeViewColumns to display the data
        self.treeview.columns = [None]*3
        self.treeview.columns[0] = gtk.TreeViewColumn(_('Command'), renderer)
        self.treeview.columns[1] = gtk.TreeViewColumn(_('User Input'), renderer)
        self.treeview.columns[2] = gtk.TreeViewColumn(_('Description'), renderer)     
        
        for n in range(3):
            ## add columns to treeview
            self.treeview.append_column(self.treeview.columns[n])
            ## create a CellRenderers to render the data
            self.treeview.columns[n].cell = gtk.CellRendererText()
            #self.treeview.columns[n].cell.set_property("cell-background-gdk", color)
            #self.treeview.columns[n].cell.set_property("foreground-gdk", color2)
            ## add the cells to the columns
            self.treeview.columns[n].pack_start(self.treeview.columns[n].cell,
                                                True)
            ## set the cell attributes to the appropriate liststore column
            self.treeview.columns[n].set_attributes(
            self.treeview.columns[n].cell, text=n)   
            self.treeview.columns[n].set_resizable(True)  
        
        ''' set treeview model and put treeview in the scrolled window
        and the scrolled window in the expander. '''
        self.treeview.set_model(self.liststore)
        self.treeview.set_reorderable(True)
        self.scrolledwindow.add(self.treeview)
        
        self.expander.add(self.scrolledwindow)
        #self.window.show_all()

        ## instantiate tabs
        tabs = clicompanionlib.tabs.Tabs()
        ## instantiate controller.Actions, where all the button actions are
        actions = clicompanionlib.controller.Actions()
        ## instantiate 'File' and 'Help' Drop Down Menu [menus_buttons.py]
        bar = clicompanionlib.menus_buttons.FileMenu()
        menu_bar = bar.the_menu(actions, self.notebook, self.liststore)
        

        ## get row of a selection
        def mark_selected(self, treeselection):
            global ROW
            (model, pathlist)=treeselection.get_selected_rows()
            ROW = pathlist
            
            
        ## double click to run a command    
        def treeview_clicked(widget, event):
            if event.button == 1 and event.type == gtk.gdk._2BUTTON_PRESS:
                actions.run_command(self, self.notebook, self.liststore)

        ## press enter to run a command                   
        def treeview_button(widget, event):
            keyname = gtk.gdk.keyval_name(event.keyval).upper()
            #print keyname ##debug
            if event.type == gtk.gdk.KEY_PRESS:
                if keyname == 'RETURN':
                    actions.run_command(self, self.notebook, self.liststore)
                    
                    

        selection = self.treeview.get_selection()
        #selection.set_mode(gtk.SELECTION_SINGLE)
        ## open with top command selected
        selection.select_path(0) 
        selection.connect("changed", mark_selected, selection)
        ## double-click
        self.treeview.connect("button-press-event", treeview_clicked)
        #press enter to run command
        self.treeview.connect("key-press-event", treeview_button)
                
        global menu_search_hbox
        
        ## The search section
        search_label = gtk.Label(_("Search:"))
        search_label.set_alignment(xalign=-1, yalign=0)
        self.search_box = gtk.Entry()
        self.search_box.connect("changed", actions._filter_commands, self.liststore, self.treeview)
        ## search box tooltip
        self.search_box.set_tooltip_text(_("Search your list of commands"))
        ## Set the search box sensitive OFF at program start, because
        ## expander is not unfolded by default
        self.search_box.set_sensitive(False)
        ## hbox for menu and search Entry
        menu_search_hbox = gtk.HBox(False)
        menu_search_hbox.pack_end(self.search_box, True)
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
        self.expander.set_label_widget(expander_hbox)

        ## Add the first tab with the Terminal
        tabs.add_tab(self, self.notebook)
        self.notebook.set_tab_pos(2)

        ## The "Add Tab" tab
        add_tab_button = gtk.Button("+")
        ## tooltip for "Add Tab" tab
        add_tab_button.set_tooltip_text(_("Click to add another tab"))
        ## create first tab
        self.notebook.append_page(gtk.Label(""), add_tab_button)
        
        global button_box
        ## buttons at bottom of main window [menus_buttons.py]
        button_box = bar.buttons(actions, 10, gtk.BUTTONBOX_END, self.notebook, self.liststore)

        ## vbox for search, notebook, buttonbar
        vbox = gtk.VBox()
        self.window.add(vbox)
        ## pack everytyhing in the vbox
        #self.vbox.pack_start(menu_bar, False, False,  0) ##menuBar
        vbox.pack_start(menu_search_hbox, False, False, 5)
        vbox.pack_start(self.expander, False, False, 5)
        vbox.pack_start(self.notebook, True, True, 5)
        vbox.pack_start(button_box, False, False, 5)
        
        ## signals
        self.expander.connect('notify::expanded', self.expanded_cb, self.window, self.search_box)
        self.window.connect("delete_event", self.delete_event)
        self.window.connect("key-press-event", self.key_clicked)
        add_tab_button.connect("clicked", tabs.add_tab, self.notebook)
        ## right click menu event capture
        self.treeview.connect ("button_press_event", bar.right_click, actions, self.treeview, self.notebook, self.liststore)


        #self.vte.grab_focus()
        self.window.show_all()
        return

    def main(self):
        try:
            gtk.main()
        except KeyboardInterrupt:
            pass
        
def run():
    
    main_window = MainWindow()
    main_window.main()
