#!/usr/bin/env python
#


# IMPORTANT need to move the .cheatsheet file to your $HOME

import pygtk
pygtk.require('2.0')
import gtk
import vte
import os
import gobject

states = []
x = ''
text=""
cheatsheet = os.path.expanduser("~/.clicompanion")


class Companion:
    with open(cheatsheet, "r") as cheatfile:
        bugdata=cheatfile.read()
        cheatfile.close()
    

    # create the terminal
    v = vte.Terminal()
    v.set_size_request(400, 150)
    # fork_command() will run a command, in this case it shows a prompt
    v.fork_command('bash')



    # close the window and quit
    def delete_event(self, widget, event, data=None):
        gtk.main_quit()
        return False
        
        
    # if a command needs more info this gets user input like a file path
    def get_info(self, widget, data=None):
        global x
        p = int(x[0][0])

        # Create Dialog object
        dialog = gtk.MessageDialog(
            None,
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            gtk.MESSAGE_QUESTION,
            gtk.BUTTONS_OK,
            None)
        
        # ask for input. Use column 2 for what is required
        dialog.set_markup("This command requires more information")

        #create the text input field
        entry = gtk.Entry()
        #allow the user to press enter to do ok
        entry.connect("activate", self.responseToDialog, dialog, gtk.RESPONSE_OK)


        #create a horizontal box to pack the entry and a label
        hbox = gtk.HBox()
        hbox.pack_start(gtk.Label(self.liststore[p][1]+":"), False, 5, 5)
        hbox.pack_end(entry)
        #some secondary text
        dialog.format_secondary_markup("Please provide a "+self.liststore[p][1])
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

    def run_command(self, widget, data=None):
        global x
        text = ""
        p = int(x[0][0])
        
        a = states[p]
        if not self.liststore[p][1] == " ":
            print "user input"
            text = Companion.get_info(self, text)
            print text
            Companion.v.feed_child(a+" "+text+"\n")
            Companion.v.show()
        else:
            Companion.v.feed_child(a+"\n")
            Companion.v.show()
        
    def __init__(self):
        # Create a new window
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)

        self.window.set_title("CLI Companion")
                
        # Sets the border width of the window.
        self.window.set_border_width(10)

        self.window.set_size_request(650, 450)

        self.window.connect("delete_event", self.delete_event)

        # create a liststore with one string column to use as the model
        self.liststore = gtk.ListStore(str, str, str)
        
        #this was for the search
        self.modelfilter = self.liststore.filter_new()

        # create the TreeView
        self.treeview = gtk.TreeView()

        # create the TreeViewColumns to display the data
        self.treeview.columns = [None]*3
        self.treeview.columns[0] = gtk.TreeViewColumn('Command')
        self.treeview.columns[1] = gtk.TreeViewColumn('User Argument')
        self.treeview.columns[2] = gtk.TreeViewColumn('Description')
        

        global states
        # add bug data
        self.states = []
        for line in self.bugdata.splitlines():
            l = line.split(':',2)
            states.append(l[0])
            self.liststore.append([l[0],l[1],l[2]])
        

        '''
        self.liststore.append([l[0],l[1],[]])
        treeiter = self.liststore.get_iter(path)
        print treeiter
        model.set(iter, COLUMN_TEXT, unicode("Hey", 'iso-8859-1'),   COLUMN_OBJECT, theObject)

        
        if not l[1] in self.states:
           self.states.append(l[1])
       
        self.show_states = self.states[:]'''

        ## is this the right model. This was for the search
        self.treeview.set_model(self.modelfilter)

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
  
  
        self.treeview.get_selection().set_mode(gtk.SELECTION_SINGLE)

        def mark_selected(treeselection):
            (model,pathlist)=treeselection.get_selected_rows()
            global x
            x = pathlist
            print pathlist

        self.treeview.get_selection().connect('changed',lambda s: mark_selected(s))


        # make ui layout
        self.vbox = gtk.VBox()
        # create window with scrollbar
        self.scrolledwindow = gtk.ScrolledWindow()
        self.scrolledwindow.set_size_request(400, 250)
        

        
        ## create run command button ##
        button = gtk.Button("Run Command")
        button.connect("clicked", self.run_command)

        self.vbox.pack_start(self.scrolledwindow)
        self.vbox.pack_start(self.v, True, True, 0)
        self.vbox.pack_start(button, True, True, 0)

        self.scrolledwindow.add(self.treeview)
        self.window.add(self.vbox)

        self.window.show_all()
        return


def main():
    gtk.main()

if __name__ == "__main__":
    companion = Companion()
    main()

