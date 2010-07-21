#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# clicompanion.py - commandline tool.
#
# Copyright 2010 Duane Hinnen
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
import webbrowser

import gtk
import pygtk
import vte

pygtk.require('2.0')

states = []
row = ''
#text=""
cheatsheet = os.path.expanduser("~/.clicompanion")


class Companion:

    # create the terminal
    vte = vte.Terminal()
    vte.set_size_request(700, 350)
    # fork_command() will run a command, in this case it shows a prompt
    vte.fork_command('bash')

    # close the window and quit
    def delete_event(self, widget,  data=None):
        gtk.main_quit()
        return False
        
    # Info Dialog Box    
    # if a command needs more info EX: a package name
    def get_info(self, widget, data=None):
        global row
        row_int = int(row[0][0])

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

        # ask for input. Use column 2 for what is required
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
    
        #some secondary text
        dialog.format_secondary_markup("Please provide a command, description, and what type of user variable if any is required.")
        
        #add it and show it
        dialog.vbox.pack_end(hbox2, True, True, 0)
        dialog.vbox.pack_end(hbox1, True, True, 0)

        dialog.show_all()

        # Show the dialog
        dialog.run()
        
        #user text assigned to a variable
        text1 = entry1.get_text()
        text2 = entry2.get_text()
        text3 = entry3.get_text()
        # open flat file that contains the command dictionary
        with open(cheatsheet, "a") as cheatfile:
            cheatfile.write(text1+" :"+text2+" : "+text3+'\n')
            cheatfile.close()
            self.update()
            
        # The destroy method must be called otherwise the 'Close' button will
        # not work.
        dialog.destroy()
        #return text
        
	# Remove command method 
    def remove_command(self, widget, data=None):
        row_int = int(row[0][0]) #convert pathlist into something usable    
        del self.liststore[row_int] #remove line from list
        
        # open command file and delete line so the change is persistent
        with open(cheatsheet, "r") as cheatfile:
            cheatlines = cheatfile.readlines()
            del cheatlines[row_int]
            cheatfile.close()
        with open(cheatsheet, "w") as cheatfile2:           
            cheatfile2.writelines(cheatlines)
            cheatfile2.close()


        
    #send the command to the terminal
    def run_command(self, widget, data=None):
        #global row
        text = ""
        row_int = int(row[0][0]) # removes everything but number from EX: [5,]
        
        cmnd = states[row_int] #states is where commands are stored
        if not self.liststore[row_int][1] == " ": # command with user input
            text = Companion.get_info(self, text)
            #print text #debug
            Companion.vte.feed_child(cmnd+" "+text+"\n") #send command w/ input
            Companion.vte.show()
        else: # command that has no user input
            Companion.vte.feed_child(cmnd+"\n") #send command
            Companion.vte.show()
            Companion.vte.grab_focus()
     
     #open the website that is the help file
    def open_site(self, widget, data=None):
        '''
        siteOpen = webbrowser.open("http://okiebuntu.homelinux.com")
        return siteOpen
        '''
        row_int = int(row[0][0]) # removes everything but number from EX: [5,]
        cmnd = states[row_int] #states is where commands are store
        splitcommand=cmnd.split(" ")
        Companion.vte.feed_child("man "+splitcommand[0]+"\n") #send command
        Companion.vte.show()

        
    # open file containing command dictionary and put it in a variable
    def update(self):
        with open(cheatsheet, "r") as cheatfile:
            bugdata=cheatfile.read()
            cheatfile.close()
    
        #global states
        # add bug data from .clicompanion to the liststore
        self.states = []
        for line in sorted(bugdata.splitlines()):
            l = line.split(':',2)
            states.append(l[0])
            self.liststore.append([l[0],l[1],l[2]])
  
        
            
    def __init__(self):
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
        
        #this was for the search
        #self.modelfilter = self.liststore.filter_new()

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
            global row
            row = pathlist
            #print pathlist #debug

        # make ui layout
        self.vbox = gtk.VBox()
        # create window with scrollbar
        self.scrolledwindow = gtk.ScrolledWindow()
        self.scrolledwindow.set_size_request(700, 220)
        
        def buttonBox(self, spacing, layout):
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
            # Cancel button
            buttonCancel = gtk.Button(stock=gtk.STOCK_QUIT)
            bbox.add(buttonCancel)
            buttonCancel.connect("clicked", self.delete_event)
            #Help Button
            buttonHelp = gtk.Button(stock=gtk.STOCK_HELP)
            bbox.add(buttonHelp)
            buttonHelp.connect("clicked", self.open_site)
            
            return frame

        
        self.vbox.pack_start(self.scrolledwindow)
        self.vbox.pack_start(self.vte, True, True, 0)
        self.vbox.pack_start(buttonBox( self, 10, gtk.BUTTONBOX_END), True, True, 5)

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

