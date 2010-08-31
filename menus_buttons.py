#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2010 Duane Hinnen, Kenny Meyer, Marcos Vanetta
#
# This file contains the menus, buttons, and right clicks
#
#import clicompanion
import gtk

class FileMenu(object):
    def the_menu(self, cli):
        menu = gtk.Menu()
        root_menu = gtk.MenuItem(_("File"))       
        root_menu.set_submenu(menu)
 
        menu2 = gtk.Menu()       
        root_menu2 = gtk.MenuItem(_("Help"))
        root_menu2.set_submenu(menu2)

        ##FILE MENU ##     
        ## Make 'Run' menu entry
        menu_item1 = gtk.MenuItem(_("Run Command"))
        menu.append(menu_item1)
        menu_item1.connect("activate", cli.run_command)
        menu_item1.show()

        ## Make 'Add' file menu entry
        menu_item2 = gtk.MenuItem(_("Add Command"))
        menu.append(menu_item2)
        menu_item2.connect("activate", cli.add_command)
        menu_item2.show()
        
        ## Make 'Remove' file menu entry
        menu_item2 = gtk.MenuItem(_("Remove Command"))
        menu.append(menu_item2)
        menu_item2.connect("activate", cli.remove_command)
        menu_item2.show()

        ## Make 'Quit' file menu entry
        menu_item3 = gtk.MenuItem(_("Quit"))
        menu.append(menu_item3)
        menu_item3.connect("activate", cli.delete_event)
        menu_item3.show()


        ## Make 'Add Tab' file menu entry
        menu_item4 = gtk.MenuItem(_("Add Tab"))
        menu.append(menu_item4)
        menu_item4.connect("activate", cli.add_tab)
        menu_item4.show()
        
        
        ## HELP MENU ##
        ## Make 'About' file menu entry
        menu_item11 = gtk.MenuItem(_("About"))
        menu2.append(menu_item11)
        menu_item11.connect("activate", cli.about_event)
        menu_item11.show()


        ## Make 'Help' file menu entry
        menu_item22 = gtk.MenuItem(_("Help"))
        menu2.append(menu_item22)
        menu_item22.connect("activate", cli.help_event)
        menu_item22.show()
        

        menu_bar = gtk.MenuBar()
        
        menu_bar.append (root_menu) ##Menu bar(file)
        menu_bar.append (root_menu2) ##Menu bar(help)       
        #menu_bar.show() ##show File Menu # Menu Bar
        ##Show 'File' Menu
        #root_menu.show()
        return menu_bar
        
        
        
    def buttons(self, cli,  spacing, layout):
        #button box at bottom of main window
        frame = gtk.Frame()
        bbox = gtk.HButtonBox()
        bbox.set_border_width(5)
        frame.add(bbox)

        # Set the appearance of the Button Box
        bbox.set_layout(layout)
        bbox.set_spacing(spacing)
        # APPLY button
        buttonRun = gtk.Button(_("Run"))
        bbox.add(buttonRun)
        buttonRun.connect("clicked", cli.run_command)
        # Add button
        buttonAdd = gtk.Button(stock=gtk.STOCK_ADD)
        bbox.add(buttonAdd)
        buttonAdd.connect("clicked", cli.add_command)
        # Edit button
        buttonEdit = gtk.Button("Edit")
        bbox.add(buttonEdit)
        buttonEdit.connect("clicked", cli.edit_command)
        # Delete button
        buttonDelete = gtk.Button(stock=gtk.STOCK_DELETE)
        bbox.add(buttonDelete)
        buttonDelete.connect("clicked", cli.remove_command)
        #Help Button
        buttonHelp = gtk.Button(stock=gtk.STOCK_HELP)
        bbox.add(buttonHelp)
        buttonHelp.connect("clicked", cli.man_page)
        # Cancel button
        buttonCancel = gtk.Button(stock=gtk.STOCK_QUIT)
        bbox.add(buttonCancel)
        buttonCancel.connect("clicked", cli.delete_event)

        
        return frame      
        
        
    #right-click popup menu for the Liststore(command list)
    def right_click(self, treeview, event, data=None):
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

