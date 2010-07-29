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
# IMPORTANT: you need to move the .cheatsheet file to your $HOME
#
import os
import gtk
import pygtk
import vte

pygtk.require('2.0')

STATES = []
ROW = ''
#text=""
CHEATSHEET = os.path.expanduser("~/.clicompanion")
CONFIG_ORIG = "/etc/clicompanion.d/clicompanion.config"


class Companion:

    # create the terminal and set its size
    vte = vte.Terminal()
    vte.set_size_request(700, 350)
    # fork_command() will run a command, in this case it shows a prompt
    vte.fork_command('bash')
    
    #copy config file to user $HOME if does not exist
    def setup(self):
    	if not os.path.isfile (CHEATSHEET):
            os.system ("cp %s %s" % (CONFIG_ORIG, CHEATSHEET))
            
    # close the window and quit
    def delete_event(self, widget,  data=None):
        gtk.main_quit()
        return False
        
    # Info Dialog Box    
    # if a command needs more info EX: a package name
    def get_info(self, widget, data=None):
        global ROW
        row_int = int(ROW[0][0])

        # Create Dialog object
        dialog = gtk.MessageDialog(
            None,
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            gtk.MESSAGE_QUESTION,
            gtk.BUTTONS_OK,
            None)
        
        # Primary text
        dialog.set_markup("This command requires more information")

        #create the text input field
        entry = gtk.Entry()
        #allow the user to press enter to do ok
        entry.connect("activate", self.responseToDialog, dialog, gtk.RESPONSE_OK)

        #create a horizontal box to pack the entry and a label
        hbox = gtk.HBox()
        hbox.pack_start(gtk.Label(self.liststore[row_int][1]+":"), False, 5, 5)
        hbox.pack_end(entry)
        #some secondary text
        dialog.format_secondary_markup("Please provide a "+self.liststore[row_int][1])
        #add it and show it
        dialog.vbox.pack_end(hbox, True, True, 0)
        dialog.show_all()

        # Show the dialog
        dialog.run()
        
        #user text assigned to a variable
        text = entry.get_text()
        # The destroy method must be called otherwise the 'Close' button will
        # not work.
        dialog.destroy()
        return text

    def responseToDialog(self, text, dialog, response):
	    dialog.response(response)
	
    # Add command dialog box
    def add_command(self, widget, data=None):

        # Create Dialog object
        dialog = gtk.MessageDialog(
            None,
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            gtk.MESSAGE_QUESTION,
            gtk.BUTTONS_OK,
            None)


        # primaary text
        dialog.set_markup("Add a command to your clicompanion dictionary")

        #create the text input field
        entry1 = gtk.Entry()
        entry2 = gtk.Entry()
        entry3 = gtk.Entry()
        #allow the user to press enter to do ok
        entry1.connect("activate", self.responseToDialog, dialog, gtk.RESPONSE_OK)

        #create the three labels
        hbox1 = gtk.HBox()
        hbox1.pack_start(gtk.Label("Command"), False, 5, 5)
        hbox1.pack_start(entry1, False, 5, 5)
        
        hbox1.pack_start(gtk.Label("User Input"), False, 5, 5)
        hbox1.pack_start(entry2, False, 5, 5)
        
        hbox2 = gtk.HBox()
        hbox2.pack_start(gtk.Label("Description"), False, 5, 5)
        hbox2.pack_start(entry3, True, 5, 5)

        # cancel button        
        dialog.add_button('Cancel', gtk.RESPONSE_DELETE_EVENT)
        #some secondary text
        dialog.format_secondary_markup("Please provide a command, description, and what type of user variable if any is required.")
        
        #add it and show it
        dialog.vbox.pack_end(hbox2, True, True, 0)
        dialog.vbox.pack_end(hbox1, True, True, 0)
        dialog.show_all()
        # Show the dialog
        result = dialog.run()
        
        text1 = ""
        text2 = ""
        text3 = ""
        if result == gtk.RESPONSE_OK:
            #user text assigned to a variable
            text1 = entry1.get_text()
            text2 = entry2.get_text()
            text3 = entry3.get_text()
        
        # open flat file that contains the commands and add the new command
        with open(CHEATSHEET, "a") as cheatfile:
            if text1 != "":
                cheatfile.write(text1+" :"+text2+" : "+text3+'\n')
                cheatfile.close()
                l = str(text1+" :"+text2+" : "+text3)
                ls = l.split(':',2)
                STATES.append(ls[0])
                self.liststore.append([ls[0],ls[1],ls[2]])
            #self.update()
          
        # The destroy method must be called otherwise the 'Close' button will
        # not work.
        dialog.destroy()
        #return text
        
	# Remove command from command file and GUI 
    def remove_command(self, widget, data=None):
        row_int = int(ROW[0][0]) #convert pathlist into something usable    
        del self.liststore[row_int] #remove line from list
        
        # open command file and delete line so the change is persistent
        with open(CHEATSHEET, "r") as cheatfile:
            cheatlines = cheatfile.readlines()
            del cheatlines[row_int]
            cheatfile.close()
        with open(CHEATSHEET, "w") as cheatfile2:           
            cheatfile2.writelines(cheatlines)
            cheatfile2.close()

    def _filter_commands(self, widget, data=None):
        """Show commands matching a given search term.
        
        The user should enter a term in the search box and the treeview should
        only display the rows which contain the search term.
        Pretty straight-forward.
        """
        search_term = self.search_box.get_text()
        # Duane's better solution: 
        # Create a TreeModelFilter object which provides auxiliary functions for
        # filtering data. 
        # http://www.pygtk.org/pygtk2tutorial/sec-TreeModelSortAndTreeModelFilter.html
        modelfilter = self.liststore.filter_new()
        def func(modelfilter, iter, search_term):
            try:
                # Iterate through every column and row and check if the search
                # term is there:
                if search_term in modelfilter.get_value(iter, 0) or \
                   search_term in modelfilter.get_value(iter, 1) or \
                   search_term in modelfilter.get_value(iter, 2):
                    return True
            except TypeError:
                # Python raises a TypeError if row data doesn't exist. Catch
                # that and fail silently.
                pass
        
        modelfilter.set_visible_func(func, search_term) 
        self.treeview.set_model(modelfilter)
            
    #send the command to the terminal
    def run_command(self, widget, data=None):
        global ROW
        text = ""
        row_int = int(ROW[0][0]) # removes everything but number from EX: [5,]
        
        cmnd = STATES[row_int] #STATES is where commands are stored
        if not self.liststore[row_int][1] == " ": # command with user input
            text = Companion.get_info(self, text)
            #print text #debug
            Companion.vte.feed_child(cmnd+" "+text+"\n") #send command w/ input
            Companion.vte.show()
        else: # command that has no user input
            Companion.vte.feed_child(cmnd+"\n") #send command
            Companion.vte.show()
            Companion.vte.grab_focus()
     
     #open the man page for selected command
    def man_page(self, widget, data=None):
        row_int = int(ROW[0][0]) # removes everything but number from EX: [5,]
        cmnd = STATES[row_int] #STATES is where commands are store
        splitcommand=cmnd.split(" ")
        Companion.vte.feed_child("man "+splitcommand[0]+"| most \n") #send command
        Companion.vte.show()
    
    # open file containing command dictionary and put it in a variable
    def update(self):
        try:
            with open(CHEATSHEET, "r") as cheatfile:
                bugdata=cheatfile.read()
                cheatfile.close()
        except IOError:
            # CHEATSHEET is not there. Oh, no!
            # So, run self.setup() again.
            self.setup() 
            # Then, run me again.
            self.update()
    
        global STATES
        # add bug data from .clicompanion to the liststore
        STATES = []
        for line in sorted(bugdata.splitlines()):
            l = line.split(':',2)
            STATES.append(l[0])
            self.liststore.append([l[0],l[1],l[2]])
            
    def __init__(self):
        
        self.setup()
        # Create a new window
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title("CLI Companion")
        # Sets the border width of the window.
        self.window.set_border_width(10)
        #set the size of the window
        self.window.set_default_size(700, 600)
        #Sets the position of the window relative to the screen
        self.window.set_position(gtk.WIN_POS_CENTER)
        #Allow user to resize window
        self.window.set_resizable(True)

        self.window.connect("delete_event", self.delete_event)

        # create a liststore with three string columns
        self.liststore = gtk.ListStore(str, str, str)        
        self.update()
        
        # The search section
        self.search_label = gtk.Label("Search:")
        self.search_label.set_alignment(xalign=-1, yalign=0) 
        self.search_box = gtk.Entry()
        self.search_box.connect("changed", self._filter_commands)

        search_hbox = gtk.HBox(False)
        search_hbox.pack_start(self.search_label, False, False, 10)
        search_hbox.pack_end(self.search_box, expand=True)

        # create the TreeView
        self.treeview = gtk.TreeView()

        # create the TreeViewColumns to display the data
        self.treeview.columns = [None]*3
        self.treeview.columns[0] = gtk.TreeViewColumn('Command')
        self.treeview.columns[1] = gtk.TreeViewColumn('User Argument')
        self.treeview.columns[2] = gtk.TreeViewColumn('Description')
        
        # The set_model() method sets the "model" property for the treeview to the value of model. model : the new tree model to use with the treeview
        self.treeview.set_model(self.liststore)
        #self.treeview.set_search_entry(entry=None)
        #self.treeview.set_enable_search(enable_search)

        for n in range(3):
            # add columns to treeview
            self.treeview.append_column(self.treeview.columns[n])
            # create a CellRenderers to render the data
            self.treeview.columns[n].cell = gtk.CellRendererText()
            # add the cells to the columns
            self.treeview.columns[n].pack_start(self.treeview.columns[n].cell,
                                                True)
            # set the cell attributes to the appropriate liststore column
            self.treeview.columns[n].set_attributes(
                self.treeview.columns[n].cell, text=n)   
            self.treeview.columns[n].set_resizable(True)          

        self.treeview.get_selection().set_mode(gtk.SELECTION_SINGLE)
        self.treeview.get_selection().connect('changed',lambda s: mark_selected(s)) 
        
        
        def mark_selected(treeselection):
            (model,pathlist)=treeselection.get_selected_rows()
            global ROW
            ROW = pathlist
            #print pathlist #debug

        # make ui layout
        self.vbox = gtk.VBox()
        # create window with scrollbar
        self.scrolledwindow = gtk.ScrolledWindow()
        self.scrolledwindow.set_size_request(700, 220)
        
        def button_box(self, spacing, layout):
            #button box at bottom of main window
            frame = gtk.Frame()
            bbox = gtk.HButtonBox()
            bbox.set_border_width(5)
            frame.add(bbox)

            # Set the appearance of the Button Box
            bbox.set_layout(layout)
            bbox.set_spacing(spacing)
            # OK button
            buttonRun = gtk.Button("Run")
            bbox.add(buttonRun)
            buttonRun.connect("clicked", self.run_command)
            # Add button
            buttonAdd = gtk.Button(stock=gtk.STOCK_ADD)
            bbox.add(buttonAdd)
            buttonAdd.connect("clicked", self.add_command)
            # Delete button
            buttonDelete = gtk.Button(stock=gtk.STOCK_REMOVE)
            bbox.add(buttonDelete)
            buttonDelete.connect("clicked", self.remove_command)
            #Help Button
            buttonHelp = gtk.Button(stock=gtk.STOCK_HELP)
            bbox.add(buttonHelp)
            buttonHelp.connect("clicked", self.man_page)
            # Cancel button
            buttonCancel = gtk.Button(stock=gtk.STOCK_QUIT)
            bbox.add(buttonCancel)
            buttonCancel.connect("clicked", self.delete_event)

            
            return frame


        self.vbox.pack_start(self.scrolledwindow, True, True, 5)
        self.vbox.pack_start(search_hbox, True, True, 5)
        self.vbox.pack_start(self.vte, True, True, 10)
        self.vbox.pack_start(button_box( self, 10, gtk.BUTTONBOX_END), True, True, 5)

        self.scrolledwindow.add(self.treeview)
        self.window.add(self.vbox)
        self.vte.grab_focus()
        self.window.show_all()
        return

def main():
    gtk.main()

if __name__ == "__main__":       
    companion = Companion()
    main()


