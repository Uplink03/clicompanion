#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
# This file contains the menus, buttons, and right clicks
#

import gtk
import tabs


class FileMenu(object):

    def the_menu(self, actions, notebook, liststore, tabs):
        menu = gtk.Menu()
        #color = gtk.gdk.Color(65555, 62000, 65555)
        #menu.modify_bg(gtk.STATE_NORMAL, color)
        root_menu = gtk.MenuItem(_("File"))       
        root_menu.set_submenu(menu)
 
        menu2 = gtk.Menu()       
        #color = gtk.gdk.Color(65555, 62000, 60000)
        #menu2.modify_bg(gtk.STATE_NORMAL, color)
        root_menu2 = gtk.MenuItem(_("Help"))
        root_menu2.set_submenu(menu2)

        ##FILE MENU ##     
        ## Make 'Run' menu entry
        menu_item1 = gtk.MenuItem(_("Run Command [F4]"))
        menu.append(menu_item1)
        menu_item1.connect("activate", actions.run_command, notebook, liststore)
        menu_item1.show()

        ## Make 'Add' file menu entry
        menu_item2 = gtk.MenuItem(_("Add Command [F5]"))
        menu.append(menu_item2)
        menu_item2.connect("activate", actions.add_command, liststore)
        menu_item2.show()
        
        ## Make 'Remove' file menu entry
        menu_item3 = gtk.MenuItem(_("Remove Command [F6]"))
        menu.append(menu_item3)
        menu_item3.connect("activate", actions.remove_command, liststore)
        menu_item3.show()
        
        ## Make 'Add Tab' file menu entry
        menu_item4 = gtk.MenuItem(_("Add Tab [F7]"))
        menu.append(menu_item4)
        menu_item4.connect("activate", tabs.add_tab, notebook)
        menu_item4.show()
        
        ## Make 'User Preferences' file menu entry
        menu_item5 = gtk.MenuItem(_("Preferences"))
        menu.append(menu_item5)
        menu_item5.connect("activate", actions.preferences, tabs)
        menu_item5.show()

        ## Make 'Quit' file menu entry
        menu_item6 = gtk.MenuItem(_("Quit"))
        menu.append(menu_item6)
        menu_item6.connect("activate", actions.delete_event)
        menu_item6.show()
        
        
        ## HELP MENU ##
        ## Make 'About' file menu entry
        menu_item11 = gtk.MenuItem(_("About"))
        menu2.append(menu_item11)
        menu_item11.connect("activate", actions.about_event)
        menu_item11.show()

        ## Make 'Usage' file menu entry
        menu_item22 = gtk.MenuItem(_("Usage"))
        menu2.append(menu_item22)
        menu_item22.connect("activate", actions.usage_event)
        menu_item22.show()
        
        ## Make 'Help' file menu entry
        menu_item22 = gtk.MenuItem(_("Help-online"))
        menu2.append(menu_item22)
        menu_item22.connect("activate", actions.help_event)
        menu_item22.show()
       
        

        menu_bar = gtk.MenuBar()
        #color = gtk.gdk.Color(60000, 65533, 60000) 
        #menu_bar.modify_bg(gtk.STATE_NORMAL, color)
        
        menu_bar.append (root_menu) ##Menu bar(file)
        menu_bar.append (root_menu2) ##Menu bar(help)       
        #menu_bar.show() ##show File Menu # Menu Bar
        ##Show 'File' Menu
        #root_menu.show()
        return menu_bar
        
        
        
    def buttons(self, actions,  spacing, layout, notebook, liststore):
        #button box at bottom of main window
        frame = gtk.Frame()
        bbox = gtk.HButtonBox()
        bbox.set_border_width(5)
        frame.add(bbox)

        # Set the appearance of the Button Box
        #color = gtk.gdk.Color(65000, 61000, 61000)
        bbox.set_layout(layout)
        bbox.set_spacing(spacing)
        # Run button
        buttonRun = gtk.Button(_("Run"))
        bbox.add(buttonRun)
        buttonRun.connect("clicked", actions.run_command, notebook, liststore)
        buttonRun.set_tooltip_text(_("Click to run a highlighted command"))
        #buttonRun.modify_bg(gtk.STATE_NORMAL, color)        
        #buttonRun.modify_bg(gtk.STATE_PRELIGHT, color)        
        #buttonRun.modify_bg(gtk.STATE_INSENSITIVE, color)        
        # Add button
        buttonAdd = gtk.Button(stock=gtk.STOCK_ADD)
        bbox.add(buttonAdd)
        buttonAdd.connect("clicked", actions.add_command, liststore)
        buttonAdd.set_tooltip_text(_("Click to add a command to your command list"))
        #buttonAdd.modify_bg(gtk.STATE_NORMAL, color)        
        #buttonAdd.modify_bg(gtk.STATE_PRELIGHT, color)        
        #buttonAdd.modify_bg(gtk.STATE_INSENSITIVE, color)
        # Edit button
        buttonEdit = gtk.Button(_("Edit"))
        bbox.add(buttonEdit)
        buttonEdit.connect("clicked", actions.edit_command, liststore)
        buttonEdit.set_tooltip_text(_("Click to edit a command in your command list"))
        #buttonEdit.modify_bg(gtk.STATE_NORMAL, color)        
        #buttonEdit.modify_bg(gtk.STATE_PRELIGHT, color)        
        #buttonEdit.modify_bg(gtk.STATE_INSENSITIVE, color)
        # Delete button
        buttonDelete = gtk.Button(stock=gtk.STOCK_DELETE)
        bbox.add(buttonDelete)
        buttonDelete.connect("clicked", actions.remove_command, liststore)
        buttonDelete.set_tooltip_text(_("Click to delete a command in your command list"))
        #buttonDelete.modify_bg(gtk.STATE_NORMAL, color)        
        #buttonDelete.modify_bg(gtk.STATE_PRELIGHT, color)        
        #buttonDelete.modify_bg(gtk.STATE_INSENSITIVE, color)
        #Help Button
        buttonHelp = gtk.Button(stock=gtk.STOCK_HELP)
        bbox.add(buttonHelp)
        buttonHelp.connect("clicked", actions.man_page, notebook)
        buttonHelp.set_tooltip_text(_("Click to get help with a command in your command list"))
        #buttonHelp.modify_bg(gtk.STATE_NORMAL, color)        
        #buttonHelp.modify_bg(gtk.STATE_PRELIGHT, color)        
        #buttonHelp.modify_bg(gtk.STATE_INSENSITIVE, color)
        # Cancel button
        buttonCancel = gtk.Button(stock=gtk.STOCK_QUIT)
        bbox.add(buttonCancel)
        buttonCancel.connect("clicked", actions.delete_event)
        buttonCancel.set_tooltip_text(_("Click to quit CLI Companion"))
        #buttonCancel.modify_bg(gtk.STATE_NORMAL, color)        
        #buttonCancel.modify_bg(gtk.STATE_PRELIGHT, color)        
        #buttonCancel.modify_bg(gtk.STATE_INSENSITIVE, color)
        return frame      
        
        
    #right-click popup menu for the Liststore(command list)
    def right_click(self, widget, event, actions, treeview, notebook, liststore):
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
                menuPopup1.connect("activate", actions.run_command, notebook, liststore)
                # right-click popup menu Edit        
                menuPopup2 = gtk.ImageMenuItem (gtk.STOCK_EDIT)
                popupMenu.add(menuPopup2)
                menuPopup2.connect("activate", actions.edit_command, liststore)
                # right-click popup menu Delete                 
                menuPopup3 = gtk.ImageMenuItem (gtk.STOCK_DELETE)
                popupMenu.add(menuPopup3)
                menuPopup3.connect("activate", actions.remove_command, liststore)
                # right-click popup menu Help                
                menuPopup4 = gtk.ImageMenuItem (gtk.STOCK_HELP)
                popupMenu.add(menuPopup4)
                menuPopup4.connect("activate", actions.man_page, notebook)
                # Show popup menu
                popupMenu.show_all()
                popupMenu.popup( None, None, None, event.button, time)
            return True          


