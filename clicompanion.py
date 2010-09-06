#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# clicompanion.py - commandline tool.
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

import sys
import pygtk
pygtk.require('2.0')

import os
import os.path

# Starting with the i18n
import locale
import gettext

BASEDIR = os.curdir

def get_language():
    """Return the language to be used by the system.

    If it finds the system language in the translated files, it
    returns it, otherwise it just returns None.
    """
    loc = locale.setlocale(locale.LC_ALL, "")
    loc = loc[:2]
    traducidos = os.listdir(locale_dir)
    if loc in traducidos:
        return loc
    return

locale_dir = os.path.join(BASEDIR, "locale")
gettext.install('clicompanion', locale_dir, unicode=True)
idioma = get_language()
if idioma is not None:
    mo = os.path.join(locale_dir, '%s/LC_MESSAGES/clicompanion.mo' % idioma)
    if not os.access(mo, os.F_OK):
        raise IOError("The l10n directory (for language %r) exists but "
                      "not the clicompanion.mo file" % idioma)
    trans = gettext.translation('clicompanion', locale_dir, languages=[idioma])
    trans.install(unicode=True)

# End with i18n


# import gtk or print error
try:
    import gtk
except:
    print >> sys.stderr, _("You need to install the python gtk bindings")
    sys.exit(1)

# TODO: these handle the exception different. Which do we like?
#
# import vte or display message dialog
try:
    import vte
except:
    error = gtk.MessageDialog (None, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
        _('You need to install python bindings for libvte'))
    error.run()
    sys.exit (1)

#import clicompanion.menus_buttons # packaged verrsion
import menus_buttons #######################################local version

#TODO: Get rid of global commands CMNDS and ROW
CMNDS = []
ROW = ''
CHEATSHEET = os.path.expanduser("~/.clicompanion")
CONFIG_ORIG = "/etc/clicompanion.d/clicompanion.config"


class Companion(object):
    '''
    All the actions the program can do.
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
    # if a command needs more info EX: a package name, a path
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
        dialog.set_markup(_("This command requires more information"))

        #create the text input field
        entry = gtk.Entry()
        #allow the user to press enter to do ok
        entry.connect("activate", self.responseToDialog, dialog, gtk.RESPONSE_OK)

        #create a horizontal box to pack the entry and a label
        hbox = gtk.HBox()
        hbox.pack_start(gtk.Label(self.liststore[row_int][1]+":"), False, 5, 5)
        hbox.pack_end(entry)
        #some secondary text
        dialog.format_secondary_markup(_("Please provide a "+self.liststore[row_int][1]))
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
    def add_command(self, widget):

        # Create Dialog object
        dialog = gtk.MessageDialog(
            None,
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            gtk.MESSAGE_QUESTION,
            gtk.BUTTONS_OK,
            None)


        # primaary text
        dialog.set_markup(_("Add a command to your clicompanion dictionary"))

        #create the text input field
        entry1 = gtk.Entry()
        entry2 = gtk.Entry()
        entry3 = gtk.Entry()
        #allow the user to press enter to do ok
        entry1.connect("activate", self.responseToDialog, dialog, gtk.RESPONSE_OK)

        #create the three labels
        hbox1 = gtk.HBox()
        hbox1.pack_start(gtk.Label(_("Command")), False, 5, 5)
        hbox1.pack_start(entry1, False, 5, 5)

        hbox1.pack_start(gtk.Label(_("User Input")), False, 5, 5)
        hbox1.pack_start(entry2, False, 5, 5)

        hbox2 = gtk.HBox()
        hbox2.pack_start(gtk.Label(_("Description")), False, 5, 5)
        hbox2.pack_start(entry3, True, 5, 5)

        # cancel button
        dialog.add_button('Cancel', gtk.RESPONSE_DELETE_EVENT)
        #some secondary text
        dialog.format_secondary_markup(_("Please provide a command, description, and what type of user variable, if any, is required."))

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


        row_obj1 = self.liststore[row_int][0]
        text1 = "".join(row_obj1)

        row_obj2 = self.liststore[row_int][1]
        text2 = "".join(row_obj2)

        row_obj3 = self.liststore[row_int][2]
        text3 = "".join(row_obj3)

        # Create Dialog object
        dialog = gtk.MessageDialog(
            None,
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            gtk.MESSAGE_QUESTION,
            gtk.BUTTONS_OK,
            None)

        # primary text
        dialog.set_markup(_("Edit the command in your clicompanion dictionary"))

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
        hbox1.pack_start(gtk.Label(_("Command")), False, 5, 5)
        hbox1.pack_start(entry1, False, 5, 5)

        hbox1.pack_start(gtk.Label(_("User Input")), False, 5, 5)
        hbox1.pack_start(entry2, False, 5, 5)

        hbox2 = gtk.HBox()
        hbox2.pack_start(gtk.Label(_("Description")), False, 5, 5)
        hbox2.pack_start(entry3, True, 5, 5)

        # cancel button
        dialog.add_button('Cancel', gtk.RESPONSE_DELETE_EVENT)
        #some secondary text
        dialog.format_secondary_markup(_("Please provide a command, description, and what type of user variable, if any, is required."))

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

            if text1 != "":
                self.remove_command(widget)
                # open flat file, add the new command
                with open(CHEATSHEET, "a") as cheatfile:
                        cheatfile.write(text1+":"+text2+":"+text3+'\n')
                        cheatfile.close()
                        l = str(text1+":"+text2+":"+text3)
                        ls = l.split(':',2)
                        CMNDS.append(ls[0])
                        self.liststore.append([ls[0],ls[1],ls[2]])


        # The destroy method must be called otherwise the 'Close' button will
        # not work.
        dialog.destroy()



    # Remove command from command file and GUI
    def remove_command(self, widget, data=None):
        global ROW
        row_int = int(ROW[0][0]) #convert pathlist into something usable

        del CMNDS[row_int]
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
        row_int = int(ROW[0][0]) # removes everything but number from [5,]

        #get the current notebook page so the function knows which terminal to run the command in.
        pagenum = self.notebook.get_current_page()
        widget = self.notebook.get_nth_page(pagenum)
        page_widget = widget.get_child()

        cmnd = CMNDS[row_int] #CMNDS is where commands are stored
        if not self.liststore[row_int][1] == " ": # command with user input
            text = Companion.get_info(self, text)
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
        widget = self.notebook.get_nth_page(pagenum)
        page_widget = widget.get_child()

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
        for line in bugdata.splitlines():
            l = line.split(':',2)
            CMNDS.append(l[0])
            self.liststore.append([l[0],l[1],l[2]])



    # add a new terminal in a tab above the current terminal
    def add_tab(self,   data=None):

        _vte = vte.Terminal()
        _vte.set_size_request(700, 220)
        _vte.connect ("child-exited", lambda term: gtk.main_quit())
        _vte.fork_command('bash')

        vte_tab = gtk.ScrolledWindow()
        vte_tab.add(_vte)
        #self.notebook.set_show_tabs(True)
        #self.notebook.set_show_border(True)

        gcp = self.notebook.get_current_page() +1
        pagenum = ('Tab %d') % gcp

        box = gtk.HBox()
        label = gtk.Label(pagenum)
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

        self.notebook.prepend_page(vte_tab, box) # add tab
        self.notebook.set_scrollable(True)
        _vte.connect ("button_press_event", self.copy_paste, None)
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
        
    #the expanded Expander with the liststore in a scrolled window in an expander
    def expanded_cb(self, expander, params):
        if expander.get_expanded():
            # create a liststore with three string columns
            self.liststore = gtk.ListStore(str, str, str)        
            self.update()
            # create the TreeView
            self.treeview = gtk.TreeView()
            # create window with scrollbar
            self.scrolledwindow = gtk.ScrolledWindow()
            self.scrolledwindow.set_size_request(700, 220)

            # create the TreeViewColumns to display the data
            self.treeview.columns = [None]*3
            self.treeview.columns[0] = gtk.TreeViewColumn(_('Command'))
            self.treeview.columns[1] = gtk.TreeViewColumn(_('User Argument'))
            self.treeview.columns[2] = gtk.TreeViewColumn(_('Description'))
            
            ## right click menu event capture
            bar = menus_buttons.FileMenu()
            self.treeview.connect ("button_press_event", bar.right_click, None)
            
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

            # The set_model() method sets the "model" property for the treeview to the value of model. model : the new tree model to use with the treeview
            self.treeview.set_model(self.liststore)
            self.scrolledwindow.add(self.treeview)
            expander.add(self.scrolledwindow)
            
            self.window.show_all()

            self.treeview.get_selection().set_mode(gtk.SELECTION_SINGLE)
            self.treeview.get_selection().connect('changed',lambda s: mark_selected(s))

            def mark_selected(treeselection):
                (model,pathlist)=treeselection.get_selected_rows()
                global ROW
                ROW = pathlist    
                    

        else:
            expander.remove(expander.child)
            ##reset the size of the window to its original one
            self.window.resize(1, 1)
        return        
        
        
    def __init__(self):
        #For now TERM is hardcoded to xterm because of a change in libvte in Maverick
        os.putenv('TERM', 'xterm')

        self.setup()
        #TODO: do we want to do this? Or just keep the height under 600.
        ##Get user screen size##
        #screen = gtk.gdk.display_get_default().get_default_screen()
        #screen_size = screen.get_monitor_geometry(0)
        #height =  screen.get_height() ## screen height ##
        # Create a new window
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        #Create an expander
        expander = gtk.Expander(None)
        #Create Notebook
        self.notebook = gtk.Notebook()
        #set Window title
        self.window.set_title("CLI Companion")
        # Adding icon
        icon = gtk.gdk.pixbuf_new_from_file("images/CLIcompanion.16.png")
        self.window.set_icon(icon)
        # Sets the border width of the window.
        self.window.set_border_width(10)
        #set the size of the window
        self.window.set_default_size(700, 400)
        #Sets the position of the window relative to the screen
        self.window.set_position(gtk.WIN_POS_CENTER)
        #Allow user to resize window
        self.window.set_resizable(True)
        
        #expander title
        expander_hbox = gtk.HBox()
        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_INDEX, gtk.ICON_SIZE_BUTTON)
        label = gtk.Label(' Command List')

        expander_hbox.pack_start(image, False, False)
        expander_hbox.pack_start(label, False, False)
        expander.set_label_widget(expander_hbox)

        self.window.connect("delete_event", self.delete_event)


        ## 'File' and 'Help' Drop Down Menu [menus_buttons.py]
        #bar = clicompanion.menus_buttons.FileMenu() #packaged version
        bar = menus_buttons.FileMenu() #########################local version
        menu_bar = bar.the_menu(self)
        
        #right-click menu[menus_buttons.py]
        #right_click_callback = bar.right_click(self)
        
        #expander signal
        expander.connect('notify::expanded', self.expanded_cb)
        
        # The search section
        self.search_label = gtk.Label(_("Search:"))
        self.search_label.set_alignment(xalign=-1, yalign=0)
        self.search_box = gtk.Entry()
        self.search_box.connect("changed", self._filter_commands)
        #Hbox for search Entry
        search_hbox = gtk.HBox(False)
        search_hbox.pack_start(self.search_label, False, False, 10)
        search_hbox.pack_end(self.search_box, True)


    
        #Add the first tab with the Terminal
        self.add_tab()
        self.notebook.set_tab_pos(1)


        # The "Add Tab" tab
        add_tab_button = gtk.Button("+")
        add_tab_button.connect("clicked", self.add_tab)
        self.notebook.append_page(gtk.Label(""), add_tab_button)
        
        # buttons at bottom of main window [menus_buttons.py]
        button_box = bar.buttons(self, 10, gtk.BUTTONBOX_END)

        # vbox for search, notebook, buttonbar
        self.vbox = gtk.VBox()
        self.window.add(self.vbox)
        #pack everytyhing in the vbox
        self.vbox.pack_start(menu_bar, False, False,  0) ##menuBar
        self.vbox.pack_start(expander, False, False, 5)
        self.vbox.pack_start(search_hbox, False, False, 5)
        self.vbox.pack_start(self.notebook, True, True, 10)
        self.vbox.pack_start(button_box, False, False, 5)


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

