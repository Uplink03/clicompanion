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

import os
import pygtk
pygtk.require('2.0')
import re
import webbrowser
import view
import copy
import clicompanionlib.tabs
import clicompanionlib.config as cc_config
import clicompanionlib.utils  as utils
from clicompanionlib.utils import get_user_shell, dbg

#if cc_config.get_config().get('terminal','debug') == 'True':
#    utils.DEBUG = True

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
    


class Actions(object):
    ## Info Dialog Box
    ## if a command needs more info EX: a package name, a path
    def get_info(self, cmd, ui, desc):
        dbg('Got command with user input')
        ## Create Dialog object
        dialog = gtk.MessageDialog(
            None,
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            gtk.MESSAGE_QUESTION,
            gtk.BUTTONS_OK_CANCEL,
            None)

        # Primary text
        dialog.set_markup(_("This command requires more information."))

        ## create the text input field
        entry = gtk.Entry()
        ## allow the user to press enter to do ok
        entry.connect("activate", self.responseToDialog, dialog, gtk.RESPONSE_OK)

        ## create a horizontal box to pack the entry and a label
        hbox = gtk.HBox()
        hbox.pack_start(gtk.Label(ui+":"), False, 5, 5)
        hbox.pack_end(entry)
        ## some secondary text
        dialog.format_secondary_markup(_("Please provide a "+ui))
        ## add it and show it
        dialog.vbox.pack_end(hbox, True, True, 0)
        dialog.show_all()

        ## Show the dialog
        response = dialog.run()

        ## user text assigned to a variable
        text = entry.get_text()
        user_input = text.split(' ')

        ## The destroy method must be called otherwise the 'Close' button will
        ## not work.
        dialog.destroy()
        if response != gtk.RESPONSE_OK:
            user_input = None
        return user_input

    def responseToDialog(self, text, dialog, response):
        dialog.response(response)

    ## Add command dialog box
    def add_command(self, mw):

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
        dialog.add_button(_('Cancel'), gtk.RESPONSE_DELETE_EVENT)
        ## some secondary text
        dialog.format_secondary_markup(
            _("When entering a command use question marks(?) as placeholders if"
              " user input is required when the command runs. Example: ls "
              "/any/directory would be entered as, ls ? .For each question "
              "mark(?) in your command, if any, use the User Input field to "
              "provide a hint for each variable. Using our example ls ? you "
              "could put directory as the User Input. Lastly provide a brief "
              "Description."))

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
            ## update commandsand sync with screen '''
            view.CMNDS.append(text1, text2, text3)
            mw.sync_cmnds()
            view.CMNDS.save()

        ## The destroy method must be called otherwise the 'Close' button will
        ## not work.
        dialog.destroy()
        #return text

    ## This the edit function
    def edit_command(self, mw):
        if not view.ROW:
            return
        lst_index = int(view.ROW[0][0])
        model = mw.treeview.get_model()
        cmd = ''.join(model[lst_index][0])
        ui = ''.join(model[lst_index][1])
        desc = ''.join(model[lst_index][2])

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
        entry1.set_text(cmd)
        entry2 = gtk.Entry()
        entry2.set_text(ui)
        entry3 = gtk.Entry()
        entry3.set_text(desc)
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
        dialog.add_button(_('Cancel'), gtk.RESPONSE_DELETE_EVENT)
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
            cmd = entry1.get_text()
            ui = entry2.get_text()
            desc = entry3.get_text()

            if cmd != "":
                cmd_index = model[lst_index][3]
                dbg('Got index %d for command at pos %d'%(cmd_index, lst_index))
                view.CMNDS[cmd_index] = [cmd, ui, desc]
            mw.sync_cmnds()
            view.CMNDS.save()
        ## The destroy method must be called otherwise the 'Close' button will
        ## not work.
        dialog.destroy()


    ## Remove command from command file and GUI
    def remove_command(self, mw):
        if not view.ROW:
            return
        ## get selected row
        lst_index = int(view.ROW[0][0])
        ## get selected element index, even from search filter
        model = mw.treeview.get_model()
        cmd_index = model[lst_index][3]
        ## delete element from liststore and CMNDS
        del view.CMNDS[cmd_index]
        mw.sync_cmnds()
        ## save changes
        view.CMNDS.save()


    def _filter_commands(self, widget, liststore, treeview):
        """
        Show commands matching a given search term.
        The user should enter a term in the search box and the treeview should
        only display the rows which contain the search term.
        Pretty straight-forward.
        """
        search_term = widget.get_text().lower()
        ## If the search term is empty, restore the liststore
        if search_term == "":
            view.FILTER = 0
            treeview.set_model(liststore)
            return

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
        ## save the old liststore and cmnds
        treeview.set_model(modelfilter)

    ## send the command to the terminal
    def run_command(self, mw):

        ## if called without selecting a command from the list return
        if not view.ROW:
            return
        text = ""
        lst_index = int(view.ROW[0][0]) ## removes everything but number from [5,]

        ## get the current notebook page so the function knows which terminal to run the command in.
        pagenum = mw.notebook.get_current_page()
        widget = mw.notebook.get_nth_page(pagenum)
        page_widget = widget.get_child()

        model = mw.treeview.get_model()
        cmd = ''.join(model[lst_index][0])
        ui = ''.join(model[lst_index][1])
        desc = ''.join(model[lst_index][2])
            
        ## find how many ?(user arguments) are in command
        match = re.findall('\?', cmd) 
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
            new_cmnd = self.replace(cmd, num, ran)

        if len(match) > 0: # command with user input
            dbg('command with ui')
            f_cmd = ""
            while True:
                try:
                    ui_text = self.get_info(cmd, ui, desc)
                    if ui_text == None:
                        return
                    dbg('Got ui "%s"'%' '.join(ui_text))
                    if ''.join(ui_text) == '':
                        raise IndexError
                    f_cmd = new_cmnd.format(ui_text)
                except IndexError, e: 
                    error = gtk.MessageDialog (None, gtk.DIALOG_MODAL, \
                        gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                        _("You need to enter full input. Space separated."))
                    error.connect('response', lambda err, *x: err.destroy())
                    error.run()
                    continue
                break
            page_widget.feed_child(f_cmd+"\n") #send command w/ input
            page_widget.show()
            page_widget.grab_focus()
        else: ## command that has no user input
            page_widget.feed_child(cmd+"\n") #send command
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
    def man_page(self, notebook):
        import subprocess as sp
        import shlex
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
            dialog.set_markup(_('You must choose a row to view the help'))
            dialog.show_all()
            dialog.run()
            dialog.destroy()     
            return 
        ## get the manpage for the command
        cmnd = view.CMNDS[row_int][0] #CMNDS is where commands are store
        ## get each command for each pipe, It's not 100 accurate, but good 
        ## enough (by now)
        commands = []
        next_part = True
        found_sudo = False
        for part in shlex.split(cmnd):
            if next_part:
                if part == 'sudo' and not found_sudo:
                    found_sudo = True
                    commands.append('sudo') 
                else:
                    if part not in commands:
                        commands.append(part)
                    next_part = False
            else:
                if part in [ '||', '&&', '&', '|']:
                    next_part = True
           
        notebook = gtk.Notebook()
        notebook.set_scrollable(True)
        notebook.popup_enable()
        notebook.set_properties(group_id=0, tab_vborder=0, tab_hborder=1, tab_pos=gtk.POS_TOP)
        ## create a tab for each command
        for command in commands:
            scrolled_page = gtk.ScrolledWindow()
            scrolled_page.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
            tab = gtk.HBox()
            tab_label = gtk.Label(command)
            tab_label.show()
            tab.pack_start(tab_label)
            page = gtk.TextView()
            page.set_wrap_mode(gtk.WRAP_WORD)
            page.set_editable(False)
            page.set_cursor_visible(False)
            try:
                manpage = sp.check_output(["man",command])
            except sp.CalledProcessError, e:
                manpage =  _('Failed to get manpage for command "%s"\nReason:\n%s')%(
                        command, e)
            textbuffer = page.get_buffer()
            textbuffer.set_text(manpage)
            scrolled_page.add(page)
            notebook.append_page(scrolled_page, tab)
        
        help_win = gtk.Dialog()
        help_win.set_title(_("Man page for %s")%cmnd)
        help_win.vbox.pack_start(notebook, True, True, 0)
        button = gtk.Button("close")
        button.connect_object("clicked", lambda self: self.destroy(), help_win)
        button.set_flags(gtk.CAN_DEFAULT)
        help_win.action_area.pack_start( button, True, True, 0)
        button.grab_default()
        help_win.set_default_size(500,600)
        help_win.show_all()


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
        dialog.set_comments(_('This is a CLI Companion program.'))

        # Add license information, this is connected to the 'License' button
        # and is displayed in a new window.
        dialog.set_license(_('Distributed under the GNU license. You can see it at <http://www.gnu.org/licenses/>.'))

        # Show the dialog
        dialog.run()

        # The destroy method must be called otherwise the 'Close' button will
        # not work.
        dialog.destroy()


    def help_event(self, widget, data=None):
        webbrowser.open("http://launchpad.net/clicompanion")
        

    def usage_event(self, widget, data=None):
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
        dbg('Changed encoding')
        model = combobox.get_model()
        index = combobox.get_active()
        if index>=0:
            text_e = model[index][0]
            encoding = text_e.split(':',1)[0].strip()
            dbg('Setting encoding to "%s"'%encoding)
            config.set("terminal", "encoding", encoding)

        
    def color_set_fg_cb(self, colorbutton_fg, config, tabs):
        dbg('Changing fg color')
        colorf = self.color2hex(colorbutton_fg)
        config.set("terminal", "colorf", str(colorf))          
        tabs.update_all_term_config(config)


    def color_set_bg_cb(self, colorbutton_bg, config, tabs):
        dbg('Changing bg color')
        colorb = self.color2hex(colorbutton_bg)
        config.set("terminal", "colorb", str(colorb))
        tabs.update_all_term_config(config)
        
        
    def color2hex(self, widget):
        """Pull the colour values out of a Gtk ColorPicker widget and return them
        as 8bit hex values, sinces its default behaviour is to give 16bit values"""
        widcol = widget.get_color()
        return('#%02x%02x%02x' % (widcol.red>>8, widcol.green>>8, widcol.blue>>8))
        
    def preferences(self, tabs, data=None):
        '''
        Preferences window
        '''
        dialog = gtk.Dialog(_("User Preferences"),
            None,
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            (gtk.STOCK_CANCEL, gtk.RESPONSE_CLOSE,
            gtk.STOCK_OK, gtk.RESPONSE_OK))
            
        config = cc_config.get_config_copy()
           
        ##create the text input fields
        entry1 = gtk.Entry()
        entry1.set_text(config.get('terminal', 'scrollb'))
        
        ##combobox for selecting encoding
        combobox = gtk.combo_box_new_text()
        i=0
        for encoding, desc in utils.encodings:
            combobox.append_text(encoding + ': '+desc)
            if encoding.strip().upper() == config.get('terminal','encoding').upper():
                active = i
            i=i+1
        combobox.set_active(active)
        combobox.connect('changed', self.changed_cb, config)
        
        ##colorbox for selecting text and background color
        colorbutton_fg = gtk.ColorButton(
            gtk.gdk.color_parse(config.get('terminal','colorf')))
        colorbutton_bg = gtk.ColorButton(
            gtk.gdk.color_parse(config.get('terminal','colorb')))

        colorbutton_fg.connect('color-set', self.color_set_fg_cb, config, tabs)
        colorbutton_bg.connect('color-set', self.color_set_bg_cb, config, tabs)
        
        ## allow the user to press enter to do ok
        entry1.connect("activate", self.responseToDialog, dialog, gtk.RESPONSE_OK)

        ## create the labels
        hbox1 = gtk.HBox()
        hbox1.pack_start(gtk.Label(_("Scrollback")), False, 5, 5)
        hbox1.pack_start(entry1, False, 5, 5)

        hbox1.pack_start(gtk.Label(_("Encoding")), False, 5, 5)
        hbox1.pack_start(combobox, False, 5, 5)

        hbox2 = gtk.HBox()
        hbox2.pack_start(gtk.Label(_("Font color")), False, 5, 5)
        hbox2.pack_start(colorbutton_fg, True, 5, 5)
        
        hbox2.pack_start(gtk.Label(_("Background color")), False, 5, 5)
        hbox2.pack_start(colorbutton_bg, True, 5, 5)
        
        ## add it and show it
        dialog.vbox.pack_end(hbox2, True, True, 0)
        dialog.vbox.pack_end(hbox1, True, True, 0)
        dialog.show_all()

        result = dialog.run()
        if result == gtk.RESPONSE_OK:
            ## user text assigned to a variable
            text_sb = entry1.get_text()
            config.set("terminal", "scrollb", text_sb)
            cc_config.save_config(config)
        tabs.update_all_term_config()

        ## The destroy method must be called otherwise the 'Close' button will
        ## not work.
        dialog.destroy()

