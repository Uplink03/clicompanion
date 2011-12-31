#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# clicompanion - commandline tool.
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

from clicompanionlib.utils import get_user_shell

import clicompanionlib.tabs
import view

import pygtk
pygtk.require('2.0')
import re
import webbrowser
import ConfigParser
import os
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
    


CHEATSHEET = os.path.expanduser("~/.clicompanion2")
CONFIG_ORIG = "/etc/clicompanion.d/clicompanion2.config"
CONFIGFILE = os.path.expanduser("~/.config/clicompanion/config")

class Actions(object):
    #make instances of the Classes we are going to use
    #main_window = view.MainWindow
    ## Info Dialog Box
    ## if a command needs more info EX: a package name, a path
    def get_info(self, widget, liststore):

        if not view.ROW:
            return
        row_int = int(view.ROW[0][0])

        ## Create Dialog object
        dialog = gtk.MessageDialog(
            None,
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            gtk.MESSAGE_QUESTION,
            gtk.BUTTONS_OK,
            None)

        # Primary text
        dialog.set_markup(_("This command requires more information."))

        ## create the text input field
        entry = gtk.Entry()
        ## allow the user to press enter to do ok
        entry.connect("activate", self.responseToDialog, dialog, gtk.RESPONSE_OK)

        ## create a horizontal box to pack the entry and a label
        hbox = gtk.HBox()
        hbox.pack_start(gtk.Label(liststore[row_int][1]+":"), False, 5, 5)
        hbox.pack_end(entry)
        ## some secondary text
        dialog.format_secondary_markup(_("Please provide a "+liststore[row_int][1]))
        ## add it and show it
        dialog.vbox.pack_end(hbox, True, True, 0)
        dialog.show_all()

        ## Show the dialog
        dialog.run()

        ## user text assigned to a variable
        text = entry.get_text()
        user_input = text.split(' ')

        ## The destroy method must be called otherwise the 'Close' button will
        ## not work.
        dialog.destroy()
        return user_input

    def responseToDialog(self, text, dialog, response):
        dialog.response(response)

    ## Add command dialog box
    def add_command(self, widget, liststore):

        ## Create Dialog object
        dialog = gtk.MessageDialog(
            None,
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            gtk.MESSAGE_QUESTION,
            gtk.BUTTONS_OK,
            None)

        ## primaary text
        dialog.set_markup(_("Add a command to your command list"))

        #create the text input field
        entry1 = gtk.Entry()
        entry2 = gtk.Entry()
        entry3 = gtk.Entry()
        ## allow the user to press enter to do ok
        entry1.connect("activate", self.responseToDialog, dialog, gtk.RESPONSE_OK)
        entry2.connect("activate", self.responseToDialog, dialog, gtk.RESPONSE_OK)
        entry3.connect("activate", self.responseToDialog, dialog, gtk.RESPONSE_OK)

        ## create three labels
        hbox1 = gtk.HBox()
        hbox1.pack_start(gtk.Label(_("Command")), False, 5, 5)
        hbox1.pack_start(entry1, False, 5, 5)

        hbox1.pack_start(gtk.Label(_("User Input")), False, 5, 5)
        hbox1.pack_start(entry2, False, 5, 5)

        hbox2 = gtk.HBox()
        hbox2.pack_start(gtk.Label(_("Description")), False, 5, 5)
        hbox2.pack_start(entry3, True, 5, 5)

        ## cancel button
        dialog.add_button('Cancel', gtk.RESPONSE_DELETE_EVENT)
        ## some secondary text
        dialog.format_secondary_markup(_('When entering a command use question '
                'marks(?) as placeholders if user input is required when the '
                'command runs. Example: ls /any/directory would be entered as, '
                'ls ? .For each question mark(?) in your command, if any, use '
                'the User Input field to provide a hint for each variable. '
                'Using our example ls ? you could put directory as the User '
                'Input. Lastly provide a brief Description.'))

        ## add it and show it
        dialog.vbox.pack_end(hbox2, True, True, 0)
        dialog.vbox.pack_end(hbox1, True, True, 0)
        dialog.show_all()
        ## Show the dialog
        result = dialog.run()

        if result == gtk.RESPONSE_OK:
            ## user text assigned to a variable
            text1 = entry1.get_text()
            text2 = entry2.get_text()
            text3 = entry3.get_text()
            '''open flat file, add the new command, update CMNDS variable
            ## update commands in liststore (on screen) '''
            if text1 != "":
                with open(CHEATSHEET, "r") as cheatfile:
                    cheatlines = cheatfile.readlines()
                    cheatlines.append(text1+"\t"+text2+"\t"+text3+'\n')
                    cheatfile.close()
                with open(CHEATSHEET, "w") as cheatfile2:
                    cheatfile2.writelines(cheatlines)
                    cheatfile2.close()
                    l = str(text1+"\t"+text2+"\t"+text3)
                    #ls = l.split(':',2)
                    ## update view.CMNDS variable
                    filteredcommandplus = text1, text2, text3
                    view.CMNDS.append(filteredcommandplus)
                    ## update the command list on screen
                    liststore.append([text1,text2,text3])


        ## The destroy method must be called otherwise the 'Close' button will
        ## not work.
        dialog.destroy()
        #return text

    ## This the edit function
    def edit_command(self, widget , liststore):

        if not view.ROW:
            return
        row_int_x = int(view.ROW[0][0])
        row_int = 0
		## TODO: Not implemented with filted yet
        if view.FILTER == 1:
            with open(CHEATSHEET, "r") as cheatfile:
                cheatlines = cheatfile.readlines()
                for i in range(len(cheatlines)):
			    	if view.CMNDS[row_int_x][0] in cheatlines[i] and view.CMNDS[row_int_x][1] in cheatlines[i] :
				    	row_int = i 
                cheatfile.close()
        else:
			row_int = row_int_x

         
        row_obj1 = view.MainWindow.liststore[row_int][0]
        text1 = "".join(row_obj1)

        row_obj2 = view.MainWindow.liststore[row_int][1]
        text2 = "".join(row_obj2)

        row_obj3 = view.MainWindow.liststore[row_int][2]
        text3 = "".join(row_obj3)

        ## Create Dialog object
        dialog = gtk.MessageDialog(
            None,
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            gtk.MESSAGE_QUESTION,
            gtk.BUTTONS_OK,
            None)

        # primary text
        dialog.set_markup(_("Edit a command in your command list"))

        ## create the text input fields
        entry1 = gtk.Entry()
        entry1.set_text(text1)
        entry2 = gtk.Entry()
        entry2.set_text(text2)
        entry3 = gtk.Entry()
        entry3.set_text(text3)
        ## allow the user to press enter to do ok
        entry1.connect("activate", self.responseToDialog, dialog, gtk.RESPONSE_OK)

        ## create three labels
        hbox1 = gtk.HBox()
        hbox1.pack_start(gtk.Label(_("Command")), False, 5, 5)
        hbox1.pack_start(entry1, False, 5, 5)

        hbox1.pack_start(gtk.Label(_("User Input")), False, 5, 5)
        hbox1.pack_start(entry2, False, 5, 5)

        hbox2 = gtk.HBox()
        hbox2.pack_start(gtk.Label(_("Description")), False, 5, 5)
        hbox2.pack_start(entry3, True, 5, 5)

        ## cancel button
        dialog.add_button('Cancel', gtk.RESPONSE_DELETE_EVENT)
        ## some secondary text
        dialog.format_secondary_markup(_("Please provide a command, description, and what type of user variable, if any, is required."))

        ## add it and show it
        dialog.vbox.pack_end(hbox2, True, True, 0)
        dialog.vbox.pack_end(hbox1, True, True, 0)
        dialog.show_all()
        ## Show the dialog
        result = dialog.run()

        if result == gtk.RESPONSE_OK:
            ## user text assigned to a variable
            text1 = entry1.get_text()
            text2 = entry2.get_text()
            text3 = entry3.get_text()

            if text1 != "":
                self.remove_command(widget, liststore)
                '''open flat file, add the new command, update CMNDS variable
                ## update commands in liststore (on screen) '''
                
                with open(CHEATSHEET, "r") as cheatfile:
                    cheatlines = cheatfile.readlines()
                    cheatlines.append(text1+":"+text2+":"+text3+'\n')
                    cheatfile.close()
                with open(CHEATSHEET, "w") as cheatfile2:
                    cheatfile2.writelines(cheatlines)
                    cheatfile2.close()
                    l = str(text1+":"+text2+":"+text3)
                    #ls = l.split(':',2)
                    ## update view.CMNDS variable
                    filteredcommandplus = text1, text2, text3
                    view.CMNDS.append(filteredcommandplus)
                    ## update the command list on screen
                    liststore.append([text1,text2,text3])
                
        ## The destroy method must be called otherwise the 'Close' button will
        ## not work.
        dialog.destroy()


    ## Remove command from command file and GUI
    def remove_command(self, widget, liststore):
		
        if not view.ROW:
            return
        row_int_x = int(view.ROW[0][0])
        row_int = 0
		## TODO: Not implemented with filted yet
        if view.FILTER == 1:
            with open(CHEATSHEET, "r") as cheatfile:
                cheatlines = cheatfile.readlines()
                for i in range(len(cheatlines)):
			    	if view.CMNDS[row_int_x][0] in cheatlines[i] and view.CMNDS[row_int_x][1] in cheatlines[i]:
				    	row_int = i 
                cheatfile.close()
        else:
			row_int = row_int_x

        del view.CMNDS[row_int_x]
        del liststore[row_int]

        ## open command file and delete line so the change is persistent
        with open(CHEATSHEET, "r") as cheatfile:
            cheatlines = cheatfile.readlines()
            del cheatlines[row_int]
            cheatfile.close()
        with open(CHEATSHEET, "w") as cheatfile2:
            cheatfile2.writelines(cheatlines)
            cheatfile2.close()


    def _filter_commands(self, widget, liststore, treeview):
        """
        Show commands matching a given search term.
        The user should enter a term in the search box and the treeview should
        only display the rows which contain the search term.
        Pretty straight-forward.
        """
        search_term = widget.get_text().lower()
        if search_term == "":
		    view.FILTER = 0
        else:
		    view.FILTER = 1
        
        ## Create a TreeModelFilter object which provides auxiliary functions for
        ## filtering data.
        ## http://www.pygtk.org/pygtk2tutorial/sec-TreeModelSortAndTreeModelFilter.html
        modelfilter = liststore.filter_new()
        def search(modelfilter, iter, search_term):
            try:
                ## Iterate through every column and row and check if the search
                ## term is there:
                if search_term in modelfilter.get_value(iter, 0).lower() or \
                   search_term in modelfilter.get_value(iter, 1).lower() or \
                   search_term in modelfilter.get_value(iter, 2).lower() :
                        return True
                                         
            except TypeError:
                ## Python raises a TypeError if row data doesn't exist. Catch
                ## that and fail silently.
                pass
            except AttributeError:
                ## Python raises a AttributeError if row data was modified . Catch
                ## that and fail silently.
                pass


        modelfilter.set_visible_func(search, search_term)
        treeview.set_model(modelfilter)
        

        #clear CMNDS list then populate it with the filteredlist of commands
        view.CMNDS = []
        for line in modelfilter:
            filteredcommandplus = tuple(line[0:2])
            view.CMNDS.append(filteredcommandplus)



    ## send the command to the terminal
    def run_command(self, widget, notebook, liststore):

        ## if called without selecting a command from the list return
        if not view.ROW:
            return
        text = ""
        row_int = int(view.ROW[0][0]) ## removes everything but number from [5,]

        ## get the current notebook page so the function knows which terminal to run the command in.
        pagenum = notebook.get_current_page()
        widget = notebook.get_nth_page(pagenum)
        page_widget = widget.get_child()

        ## view.CMNDS is where commands are stored
        cmnd = view.CMNDS[row_int][0]
            
        ## find how many ?(user arguments) are in command
        match = re.findall('\?', cmnd) 
        '''
        Make sure user arguments were found. Replace ? with something
        .format can read. This is done so the user can just enter ?, when
        adding a command where arguments are needed, instead
        of {0[1]}, {0[1]}, {0[2]}
        '''    
        if match == False:
            pass
        else:
            num = len(match)
            ran = 0
            new_cmnd = self.replace(cmnd, num, ran)


        if not view.CMNDS[row_int][1] == "": # command with user input
            c = ""
            try:
                text = self.get_info(self, liststore)
                c = new_cmnd.format(text)
            except: 
                error = gtk.MessageDialog (None, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                    _("You need to enter full input. Click on [x] to continue."))
                error.run()
            page_widget.feed_child(c+"\n") #send command w/ input
            page_widget.show()
            page_widget.grab_focus()
        else: ## command that has no user input
            page_widget.feed_child(cmnd+"\n") #send command
            page_widget.show()
            page_widget.grab_focus()
            
    ## replace ? with {0[n]}
    def replace(self, cmnd, num, ran):
        replace_cmnd=re.sub('\?', '{0['+str(ran)+']}', cmnd, count=1)
        cmnd = replace_cmnd
        ran += 1
        if ran < num:
            return self.replace(cmnd, num, ran)    
        else:
            pass
        return cmnd
        
    ## open the man page for selected command
    def man_page(self, widget, notebook):
        try:
            row_int = int(view.ROW[0][0]) # removes everything but number from EX: [5,]
        except IndexError:  
            ## When user not choose row, when is in filter mode
            dialog = gtk.MessageDialog(
                None,
                gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                gtk.MESSAGE_QUESTION,
                gtk.BUTTONS_OK,
                None)
            dialog.set_markup('You must choose row to view help')
            dialog.show_all()
            dialog.run()
            dialog.destroy()     
            return 
        cmnd = view.CMNDS[row_int][0] #CMNDS is where commands are store
        splitcommand = self._filter_sudo_from(cmnd.split(" "))
        ## get current notebook tab to use in function
        pagenum = notebook.get_current_page()
        widget = notebook.get_nth_page(pagenum)
        page_widget = widget.get_child()
        #send command to Terminal
        page_widget.feed_child("man "+splitcommand[0]+"| most \n") 
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



    #TODO: Move to menus_buttons
    def copy_paste(self, vte, event, data=None):
        if event.button == 3:

            time = event.time
            ## right-click popup menu Copy
            popupMenu = gtk.Menu()
            menuPopup1 = gtk.ImageMenuItem (gtk.STOCK_COPY)
            popupMenu.add(menuPopup1)
            menuPopup1.connect('activate', lambda x: vte.copy_clipboard())
            ## right-click popup menu Paste
            menuPopup2 = gtk.ImageMenuItem (gtk.STOCK_PASTE)
            popupMenu.add(menuPopup2)
            menuPopup2.connect('activate', lambda x: vte.paste_clipboard())

            ## Show popup menu
            popupMenu.show_all()
            popupMenu.popup( None, None, None, event.button, time)
            return True
        else:
            pass
            
    ## close the window and quit
    def delete_event(self, widget,  data=None):
        gtk.main_quit()
        return False
    
    ## Help --> About and Help --> Help menus
    def about_event(self, widget, data=None):
        # Create AboutDialog object
        dialog = gtk.AboutDialog()

        # Add the application name to the dialog
        dialog.set_name('CLI Companion ')

        # Set the application version
        dialog.set_version('1.1')

        # Pass a list of authors.  This is then connected to the 'Credits'
        # button.  When clicked the buttons opens a new window showing
        # each author on their own line.
        dialog.set_authors(['Duane Hinnen', 'Kenny Meyer', 'Marcos Vanettai', 'Marek Bardoński'])

        # Add a short comment about the application, this appears below the application
        # name in the dialog
        dialog.set_comments('This is a CLI Companion program.')

        # Add license information, this is connected to the 'License' button
        # and is displayed in a new window.
        dialog.set_license('Distributed under the GNU license. You can see it at <http://www.gnu.org/licenses/>.')

        # Show the dialog
        dialog.run()

        # The destroy method must be called otherwise the 'Close' button will
        # not work.
        dialog.destroy()
    def help_event(self, widget, data=None):
        webbrowser.open("http://okiebuntu.homelinux.com/okwiki/clicompanion")
        
    def usage_event(self, widget, data=None):
        mw = view.MainWindow
        dialog = gtk.Dialog("Usage",
            None,
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            (gtk.STOCK_CANCEL, gtk.RESPONSE_CLOSE))
            
        hbox1 = gtk.HBox()
        hbox2 = gtk.HBox()
        hbox21 = gtk.HBox()
        hbox3 = gtk.HBox()
        hbox4 = gtk.HBox()
        hbox5 = gtk.HBox()
        hbox6 = gtk.HBox()

        hbox1.pack_start(gtk.Label(_("To maximize window, press F11")), False, 5, 5)
        hbox2.pack_start(gtk.Label(_("To hide UI, press F12")), False, 5, 5)
        hbox21.pack_start(gtk.Label(_("--------------------")), False, 5, 5)
        hbox3.pack_start(gtk.Label(_("Run command - F4")), False, 5, 5) 
        hbox4.pack_start(gtk.Label(_("Add command - F5")), False, 5, 5)        
        hbox5.pack_start(gtk.Label(_("Remove command - F6")), False, 5, 5) 
        hbox6.pack_start(gtk.Label(_("Add tab - F7")), False, 5, 5)        
        
        dialog.vbox.pack_end(hbox1, True, True, 0)
        dialog.vbox.pack_end(hbox2, True, True, 0)
        dialog.vbox.pack_end(hbox21, True, True, 0)
        dialog.vbox.pack_end(hbox3, True, True, 0)
        dialog.vbox.pack_end(hbox4, True, True, 0)
        dialog.vbox.pack_end(hbox5, True, True, 0)
        dialog.vbox.pack_end(hbox6, True, True, 0)
        
        dialog.show_all()
        
        result = dialog.run()
        ## The destroy method must be called otherwise the 'Close' button will
        ## not work.
        dialog.destroy()
        
        
    ## File --> Preferences    
    def changed_cb(self, combobox, config):
        config.read(CONFIGFILE)
        model = combobox.get_model()
        index = combobox.get_active()
        if index:
            text_e = model[index][0]
            config.set("terminal", "encoding", text_e)
            # Writing our configuration file
            with open(CONFIGFILE, 'wb') as f:
                config.write(f)

        
    def color_set_fg_cb(self, colorbutton_fg, config):
        config.read(CONFIGFILE)
        #colorf16 = colorbutton_fg.get_color()
        colorf = self.color2hex(colorbutton_fg)
        config.set("terminal", "colorf", str(colorf))          
        # Writing our configuration file
        with open(CONFIGFILE, 'wb') as f:
            config.write(f)



    def color_set_bg_cb(self, colorbutton_bg, config):
        config.read(CONFIGFILE)
        #colorb16 = colorbutton_bg.get_color()
        colorb = self.color2hex(colorbutton_bg)
        config.set("terminal", "colorb", str(colorb))
        # Writing our configuration file
        with open(CONFIGFILE, 'wb') as f:
            config.write(f)

        
        
    def color2hex(self, widget):
        """Pull the colour values out of a Gtk ColorPicker widget and return them
        as 8bit hex values, sinces its default behaviour is to give 16bit values"""
        widcol = widget.get_color()
        print widcol
        return('#%02x%02x%02x' % (widcol.red>>8, widcol.green>>8, widcol.blue>>8))
        
    def preferences(self, widget, data=None):
        '''
        Preferences window
        '''
        mw = view.MainWindow
        dialog = gtk.Dialog("User Preferences",
            None,
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            (gtk.STOCK_CANCEL, gtk.RESPONSE_CLOSE,
            gtk.STOCK_OK, gtk.RESPONSE_OK))
            
        config = ConfigParser.RawConfigParser()
        config.read(CONFIGFILE)
            
        ##create the text input fields
        entry1 = gtk.Entry()
        entry1.set_text(config.get('terminal', 'scrollb'))

        
        ##combobox for selecting encoding
        combobox = gtk.combo_box_new_text()
        combobox.append_text('Select encoding:')
        combobox.append_text('UTF-8')
        combobox.append_text('ISO-8859-1')
        combobox.append_text('ISO-8859-15')

        combobox.connect('changed', self.changed_cb, config)
        combobox.set_active(0)
        
        ##colorbox for selecting text and background color
        colorbutton_fg = gtk.ColorButton(gtk.gdk.color_parse('white'))
        colorbutton_bg = gtk.ColorButton(gtk.gdk.color_parse('black'))

        colorbutton_fg.connect('color-set', self.color_set_fg_cb, config)
        colorbutton_bg.connect('color-set', self.color_set_bg_cb, config)

        #dialog.show_all()
        
        ## allow the user to press enter to do ok
        entry1.connect("activate", self.responseToDialog, dialog, gtk.RESPONSE_OK)



        ## create three labels
        hbox1 = gtk.HBox()
        hbox1.pack_start(gtk.Label(_("Scrollback")), False, 5, 5)
        hbox1.pack_start(entry1, False, 5, 5)

        hbox1.pack_start(gtk.Label(_("encoding")), False, 5, 5)
        hbox1.pack_start(combobox, False, 5, 5)


        hbox2 = gtk.HBox()
        hbox2.pack_start(gtk.Label(_("font color")), False, 5, 5)
        hbox2.pack_start(colorbutton_fg, True, 5, 5)
        
        hbox2.pack_start(gtk.Label(_("background color")), False, 5, 5)
        hbox2.pack_start(colorbutton_bg, True, 5, 5)
        
        
        ## add it and show it
        dialog.vbox.pack_end(hbox2, True, True, 0)
        dialog.vbox.pack_end(hbox1, True, True, 0)
        dialog.show_all()
        
        result = dialog.run()

        if result == gtk.RESPONSE_OK:

            ## user text assigned to a variable
            text_sb = entry1.get_text()
            
            config.read(CONFIGFILE)
            config.set("terminal", "scrollb", text_sb)



            # Writing our configuration file
            with open(CONFIGFILE, 'wb') as f:
                config.write(f)
   

            ## instantiate tabs
            tabs = clicompanionlib.tabs.Tabs()
            tabs.update_term_config

        ## The destroy method must be called otherwise the 'Close' button will
        ## not work.
        dialog.destroy()

    def save_cmnds(self):
        with open(CHEATSHEET, "w") as cheatfile:
            for command in  view.CMNDS:
                cheatfile.write('\t'.join(command)+'\n')
       
        
