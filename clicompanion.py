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
#

import sys
import pygtk
pygtk.require('2.0')

import os
# import gtk or print error
try:
    import gtk
except:
    print >> sys.stderr, "You need to install the python gtk bindings"
    sys.exit(1)
    
# TODO: these handle the exception different. Which do we like?
# import vte or display message dialog
try:
    import vte
except:
    error = gtk.MessageDialog (None, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
        'You need to install python bindings for libvte')
    error.run()
    sys.exit (1)

import menus_buttons


#TODO: Get rid of global commands CMNDS and ROW
CMNDS = []
ROW = ''
CHEATSHEET = os.path.expanduser("~/.clicompanion")
CONFIG_ORIG = "/etc/clicompanion.d/clicompanion.config"


class Companion(object):
    '''
    # create the terminal and set its size
    vte = vte.Terminal()
    vte.set_size_request(700, 350)
    vte.connect ("child-exited", lambda term: gtk.main_quit())
    vte.fork_command('bash')
    '''
    #copy config file to user $HOME if does not exist
    def setup(self):
        """Create an initial cheatsheet."""
        if not os.path.exists(CHEATSHEET):
            if os.path.exists(CONFIG_ORIG):
                os.system ("cp %s %s" % (CONFIG_ORIG, CHEATSHEET))
            else:
                # Oops! Looks like there's no cheatsheet in CHEATSHEET.
                # Then, create an empty cheatsheet.
                open(CHEATSHEET, 'w').close()
            
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
    def add_command(self, widget, text1 = "", text2 = "", text3 = ""):
        print text1, text2, text3
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
        entry1.set_text(text1)
        entry2 = gtk.Entry()
        entry2.set_text(text2)
        entry3 = gtk.Entry()
        entry3.set_text(text3)        
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
                    CMNDS.append(ls[0])
                    self.liststore.append([ls[0],ls[1],ls[2]])
                #self.update()
          
        # The destroy method must be called otherwise the 'Close' button will
        # not work.
        dialog.destroy()
        #return text
        
    # This the edit function
    def edit_command(self, widget , data=None):

        global ROW
        row_int = int(ROW[0][0])
        #print row_int
        #print text1, text2, text3

        row_obj1 = self.liststore[row_int][0]
        text1 = "".join(row_obj1)
        

        row_obj2 = self.liststore[row_int][1]
        text2 = "".join(row_obj2)
        

        row_obj3 = self.liststore[row_int][2]
        text3 = "".join(row_obj3)
        
        '''
        row_obj = self.liststore[row_int]
        row_str = "".join(row_obj)
        print row_str
        row_edit = row_str.split(':',2)
        print row_edit
        text1 = str(row_edit[1])
        text2 = str(row_edit[2])
        text3 = str(row_edit[3])
        '''
        print text1, text2, text3
        self.add_command(text1, text2, text3)


    # Remove command from command file and GUI 
    def remove_command(self, widget, data=None):
        row_int = int(ROW[0][0]) #convert pathlist into something usable    
        del self.liststore[row_int]
        
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

        # Create a TreeModelFilter object which provides auxiliary functions for
        # filtering data. 
        # http://www.pygtk.org/pygtk2tutorial/sec-TreeModelSortAndTreeModelFilter.html
        modelfilter = self.liststore.filter_new()
        def search(modelfilter, iter, search_term):
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
        
        modelfilter.set_visible_func(search, search_term) 
        self.treeview.set_model(modelfilter)
            
    #send the command to the terminal
    def run_command(self, widget, data=None):
        global ROW
        text = ""
        row_int = int(ROW[0][0]) # removes everything but number from EX: [5,]
        
        #get the current notebook page so the function knows which terminal to run the command in.
        pagenum = self.notebook.get_current_page()
        page_widget = self.notebook.get_nth_page(pagenum)
        
        cmnd = CMNDS[row_int] #CMNDS is where commands are stored
        if not self.liststore[row_int][1] == " ": # command with user input
            text = Companion.get_info(self, text)
            #print text #debug
            page_widget.feed_child(cmnd+" "+text+"\n") #send command w/ input
            page_widget.show()
        else: # command that has no user input
            page_widget.feed_child(cmnd+"\n") #send command
            page_widget.show()
            page_widget.grab_focus()
     
     #open the man page for selected command
    def man_page(self, widget, data=None):
        row_int = int(ROW[0][0]) # removes everything but number from EX: [5,]
        cmnd = CMNDS[row_int] #CMNDS is where commands are store
        splitcommand = self._filter_sudo_from(cmnd.split(" "))
        # get current notebook tab to use in function
        pagenum = self.notebook.get_current_page()
        page_widget = self.notebook.get_nth_page(pagenum)
        
        page_widget.feed_child("man "+splitcommand[0]+"| most \n") #send command
        page_widget.grab_focus()
        page_widget.show()
        
        
    @staticmethod
    def _filter_sudo_from(command):
        """Filter the sudo from `command`, where `command` is a list.
        Return the command list with the "sudo" filtered out.
        """
        if command[0].startswith("sudo"):
            del command[0]
            return command
        return command
        
    
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
    
        global CMNDS
        # add bug data from .clicompanion to the liststore
        CMNDS = []
        for line in sorted(bugdata.splitlines()):
            l = line.split(':',2)
            CMNDS.append(l[0])
            self.liststore.append([l[0],l[1],l[2]])
            

    #right-click popup menu for the Liststore(command list)
    def right_click_callback(self, treeview, event, data=None):
        if event.button == 3:
            x = int(event.x)
            y = int(event.y)
            time = event.time
            pthinfo = treeview.get_path_at_pos(x, y)
            if pthinfo is not None:
                path, col, cellx, celly = pthinfo
                treeview.grab_focus()
                treeview.set_cursor( path, col, 0)
                
                # right-click popup menu Apply(run)
                popupMenu = gtk.Menu()
                menuPopup1 = gtk.ImageMenuItem (gtk.STOCK_APPLY)
                popupMenu.add(menuPopup1)
                menuPopup1.connect("activate", self.run_command)
                # right-click popup menu Edit        
                menuPopup2 = gtk.ImageMenuItem (gtk.STOCK_EDIT)
                popupMenu.add(menuPopup2)
                menuPopup2.connect("activate", self.edit_command)
                # right-click popup menu Delete                 
                menuPopup3 = gtk.ImageMenuItem (gtk.STOCK_DELETE)
                popupMenu.add(menuPopup3)
                menuPopup3.connect("activate", self.remove_command)
                # right-click popup menu Help                
                menuPopup4 = gtk.ImageMenuItem (gtk.STOCK_HELP)
                popupMenu.add(menuPopup4)
                menuPopup4.connect("activate", self.man_page)
                # Show popup menu
                popupMenu.show_all()
                popupMenu.popup( None, None, None, event.button, time)
            return True
            
    # add a new terminal in a tab above the current terminal        
    def add_tab(self,   data=None):
        
        vte_tab = vte.Terminal()
        vte_tab.set_size_request(700, 220)
        vte_tab.connect ("child-exited", lambda term: gtk.main_quit())
        vte_tab.fork_command('bash')
        
        #self.notebook.set_show_tabs(True)
        #self.notebook.set_show_border(True)
        
        gcp = self.notebook.get_current_page() +1
        print gcp
        pagenum = ('Tab %d') % gcp

        box = gtk.HBox()
        label = gtk.Label(pagenum)
        #icon = gtk.Image()
        box.pack_start(label, True, True)
        
        # x image for tab close button
        close_image = gtk.image_new_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_MENU)
        # close button
        closebtn = gtk.Button()
        closebtn.set_relief(gtk.RELIEF_NONE)
        closebtn.set_focus_on_click(True)

        closebtn.add(close_image)
        # put button in a box and show box
        box.pack_end(closebtn, False, False)
        box.show_all()
                
        #widget = gtk.Label(label)
        self.notebook.prepend_page(vte_tab, box) # add tab
        vte_tab.connect ("button_press_event", self.copy_paste, None)
        vte_tab.grab_focus()
        
        closebtn.connect("clicked", self.close_tab, vte_tab) # signal handler for tab
        self.window.show_all()


        return vte_tab

    # Remove a page from the notebook
    def close_tab(self, sender, widget):
        #get the page number of the tab we wanted to close
        pagenum = self.notebook.page_num(widget)
        #and close it
        self.notebook.remove_page(pagenum)


    def copy_paste(self, vte, event, data=None):        
        if event.button == 3:

            time = event.time
            # right-click popup menu Copy
            popupMenu = gtk.Menu()
            menuPopup1 = gtk.ImageMenuItem (gtk.STOCK_COPY)
            popupMenu.add(menuPopup1)
            menuPopup1.connect('activate', lambda x: vte.copy_clipboard())
            #item.set_sensitive(terminal.vte.get_has_selection())
            # right-click popup menu Paste       
            menuPopup2 = gtk.ImageMenuItem (gtk.STOCK_PASTE)
            popupMenu.add(menuPopup2)
            menuPopup2.connect('activate', lambda x: vte.paste_clipboard())
           
            # Show popup menu
            popupMenu.show_all()
            popupMenu.popup( None, None, None, event.button, time)
            return True
        else:
            pass
            
    def about_event(self):
        pass
    def help_event(self):
        pass
            
    def __init__(self):
        
        self.setup()
        #TODO: do we want to do this? Or just keep the height under 600.
        ##Get user screen size## 
        #screen = gtk.gdk.display_get_default().get_default_screen()
        #screen_size = screen.get_monitor_geometry(0)
        #height =  screen.get_height() ## screen height ##
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
        

        ## 'File' and 'Help' Drop Down Menu [menus_buttons.py]
        bar = menus_buttons.FileMenu()
        menu_bar = bar.the_menu(self)


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
        
        ## right click menu event capture
        self.treeview.connect ("button_press_event", self.right_click_callback, None)
        
        # The set_model() method sets the "model" property for the treeview to the value of model. model : the new tree model to use with the treeview
        self.treeview.set_model(self.liststore)


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

        # buttons at bottom of main window [menu.py]
        button_box = bar.buttons(self, 10, gtk.BUTTONBOX_END)
        
        # make ui layout
        self.vbox = gtk.VBox()
        # create window with scrollbar
        self.scrolledwindow = gtk.ScrolledWindow()
        self.scrolledwindow.set_size_request(700, 220)
        
        self.notebook = gtk.Notebook()
        
        #self.notebook.add(self.vte)
        self.add_tab()
        self.notebook.set_tab_pos(1)
        #gcp = self.notebook.get_current_page()
        #pagenum = ('Tab %d') % gcp
        #vte_tab.connect ("button_press_event", self.copy_paste, None)
        
        # The "Add Tab" tab
        add_tab_button = gtk.Button("+")
        add_tab_button.connect("clicked", self.add_tab)
        self.notebook.append_page(gtk.Label(""), add_tab_button)


        self.window.add(self.vbox)
        self.vbox.pack_start(menu_bar, False, False,  0) ##menuBar
        self.vbox.pack_start(self.scrolledwindow, True, True, 5)
        self.vbox.pack_start(search_hbox, True, True, 5)
        self.vbox.pack_start(self.notebook, True, True, 10)
        self.vbox.pack_start(button_box, True, True, 5)

        self.scrolledwindow.add(self.treeview)
        #self.window.add(self.vbox)
        #self.vte.grab_focus()
        self.window.show_all()
        return

def main():
    try:
        gtk.main()
    except KeyboardInterrupt:
        pass
             
if __name__ == "__main__":       
    companion = Companion()
    main()


