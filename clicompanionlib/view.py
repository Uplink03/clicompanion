#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# view.py - Main window for the clicompanon
#
# Copyright 2010 Duane Hinnen, Kenny Meyer, David Caro
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
# This file is where the main window is defined, depends on all the modules of
# the clicompanion libraries.
#
# Also holds the class that implements the commands notebook (the upper
# notebook), where all the tab plugins will be added (like LocalCommandList and
# CommandLineFU)


import os
import pygtk
pygtk.require('2.0')
import gobject
import webbrowser

# import vte and gtk or print error
try:
    import gtk
except:
    ## do not use gtk, just print
    print _("You need to install the python gtk bindings package"
            "'python-gtk2'")
    sys.exit(1)

try:
    import vte
except:
    error = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR,
        gtk.BUTTONS_OK,
        _("You need to install 'python-vte' the python bindings for libvte."))
    error.run()
    sys.exit(1)

import clicompanionlib.menus_buttons as cc_menus_buttons
import clicompanionlib.tabs as cc_tabs
import clicompanionlib.utils as cc_utils
from clicompanionlib.utils import dbg
import clicompanionlib.config as cc_config
import clicompanionlib.helpers as cc_helpers
import clicompanionlib.plugins as cc_plugins
import clicompanionlib.preferences as cc_pref

TARGETS = [
    ('MY_TREE_MODEL_ROW', gtk.TARGET_SAME_WIDGET, 0),
    ('text/plain', 0, 1),
    ('TEXT', 0, 2),
    ('STRING', 0, 3),
    ]


class CommandsNotebook(gtk.Notebook):
    '''
    This is the notebook where the commands list and the commandlinefu commands
    are displayed
    '''
    ### We need a way to tell the main window that a command must be runned on
    ## the selected terminal tab
    __gsignals__ = {
         'run_command': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                             (str, str, str)),
         'add_tab': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                             ()),
         'preferences': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                             ()),
         'show_man': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                             (str, )),
         'quit': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                             ()),
         }

    def __init__(self, config, pluginloader):
        self.config = config
        self.pluginloader = pluginloader
        gtk.Notebook.__init__(self)
        self.loaded_plugins = {}
        self.draw_all()

    def draw_all(self):
        ## Load the needed LocalCommandList plugin
        if 'LocalCommandList' not in self.pluginloader.plugins.keys():
            print _("ERROR: LocalCommandList plugin is needed for the "
                    "execution of CLI Companion, please retore the plugin or "
                    "reinstall.")
            self.emit('quit')
        else:
            self.commandstab = self.pluginloader.plugins['LocalCommandList'](
                    self.config.get_plugin_conf('LocalCommandList'))
        for pname, pclass in self.pluginloader.get_plugins('CommandTab'):
            if pname == 'LocalCommandList':
                tab = self.commandstab
            else:
                tab = pclass(self.config.get_plugin_conf('LocalCommandList'))
            self.append_tab(tab, pname)

    def append_tab(self, tab, pname):
        ## save the tab related to the plugin name
        self.loaded_plugins[pname] = tab
        self.append_page(tab, gtk.Label(tab.__title__ or pname))
        ##All the available signals for the plugins
        tab.connect('run_command',
                lambda wg, *args: self.run_command(*args))
        tab.connect('add_command',
                lambda wg, *args: self.commandstab.add_command(*args))
        tab.connect('remove_command',
                lambda wg, *args: self.remove_command(*args))
        tab.connect('edit_command',
                lambda wg, *args: self.edit_command(*args))
        tab.connect('add_tab',
                lambda wg, *args: self.emit('add_tab', *args))
        tab.connect('preferences',
                lambda wg, *args: self.emit('preferences', *args))
        tab.connect('show_man',
                lambda wg, *args: self.emit('show_man', *args))
        tab.connect('quit',
                lambda wg, *args: self.emit('quit', *args))

    def filter(self, filter_str, pagenum=None):
        if pagenum == None:
            pagenum = self.get_current_page()
        page = self.get_nth_page(pagenum)
        dbg('filtering by %s' % filter_str)
        page.filter(filter_str)

    def set_netbook(netbookmode=False):
        if netbookmode:
            self.set_size_request(700, 200)
        else:
            self.set_size_request(700, 220)

    def get_command(self):
        pagenum = self.get_current_page()
        page = self.get_nth_page(pagenum)
        return page.get_command()

    def run_command(self, cmd=None, ui=None, desc=None):
        if cmd == None:
            cmd, ui, desc = self.get_command()
        if cmd:
            dbg('running command %s' % cmd)
            self.emit('run_command', cmd, ui, desc)

    def add_command(self):
        if self.get_current_page() == 0:
            self.commandstab.add_command()
        else:
            command = self.get_command()
            if command[0] != None:
                self.commandstab.add_command(*command)
            else:
                self.commandstab.add_command()

    def remove_command(self):
        if self.get_current_page() == 0:
            self.commandstab.remove_command()

    def edit_command(self):
        if self.get_current_page() == 0:
            self.commandstab.edit_command()
        else:
            command = self.get_command()
            if command[0] != None:
                self.commandstab.add_command(*command)

    def update(self, config=None, force=None):
        if config:
            self.config = config
        newplugins = self.pluginloader.get_plugins('CommandTab')
        for plugin in self.loaded_plugins.keys():
            if plugin not in [name for name, cl in newplugins]:
                dbg('Disabling plugin %s' % plugin)
                self.remove_page(self.page_num(self.loaded_plugins[plugin]))
                self.loaded_plugins.pop(plugin)
        for pname, pclass in newplugins:
            if pname not in self.loaded_plugins.keys():
                dbg('Adding new selected plugin %s' % pname)
                self.append_tab(
                    pclass(self.config.get_plugin_conf('LocalCommandList')),
                    pname)
        for plugin in force:
            if plugin in self.loaded_plugins:
                dbg('Reloading plugin %s' % plugin)
                self.loaded_plugins[plugin].reload(
                        self.config.get_plugin_conf(plugin))
        self.show_all()


class MainWindow(gtk.Window):
    def __init__(self, config):
        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
        ###############
        ### Some state variables
        self.hiddenui = False
        self.maximized = False
        self.filtered = False
        self.fullscr = False

        self.clipboard = gtk.clipboard_get(gtk.gdk.SELECTION_CLIPBOARD)

        self.config = config

        self.load_plugins()

        ## two sections, the menus and search box and the expander with the
        ## commands notebook and in the botom, the terminals notebook

        ###########################
        #### Here we create the commands notebook for the expander
        self.cmd_notebook = CommandsNotebook(config, self.pluginloader)

        ## set various parameters on the main window (size, etc)
        self.init_config()
        self.term_notebook = cc_tabs.TerminalsNotebook(self.config,
                                                        self.pluginloader)

        ## Create the menus and the searchbox
        ## hbox for menu and search Entry
        self.menu_search_hbox = gtk.HBox(False)

        #### The menus
        ## instantiate 'File' and 'Help' Drop Down Menu [menus_buttons.py]
        menu_bar = cc_menus_buttons.FileMenu(self.config)
        self.menu_search_hbox.pack_start(menu_bar, True)

        #### the expander
        self.expander = gtk.Expander()
        self.menu_search_hbox.pack_end(self.expander, False, False, 0)
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
        self.expander.set_expanded(True)

        #### The search box
        self.search_hbox = gtk.HBox()
        #### the search label
        search_label = gtk.Label(_("Search:"))
        search_label.set_alignment(xalign=-1, yalign=0)
        self.search_box = gtk.Entry()
        self.search_box.connect("changed",
                lambda wg, *x: self.cmd_notebook.filter(wg.get_text()))
        ## search box tooltip
        self.search_box.set_tooltip_text(_("Search your list of commands"))
        self.search_hbox.pack_start(search_label, False, False, 8)
        self.search_hbox.pack_end(self.search_box, True)
        self.menu_search_hbox.pack_end(self.search_hbox, True)

        ############################
        ## and now the terminals notebook
        self.term_notebook.set_show_tabs(0)
        ##attach the style to the widget
        self.term_notebook.set_name("tab-close-button")

        ## Add the first tab with the Terminal
        self.term_notebook.add_tab()

        ## buttons at bottom of main window [menus_buttons.py]
        self.button_box = cc_menus_buttons.Buttons(10, gtk.BUTTONBOX_END)

        ## pack everything
        ## vbox for search, notebook, buttonbar
        ## pack everytyhing in the vbox
        h_vbox = gtk.VBox()
        h_vbox.pack_start(self.menu_search_hbox, False, False, 5)
        h_vbox.pack_start(self.cmd_notebook, True, True, 5)
        self.l_vbox = gtk.VBox()
        self.l_vbox.pack_start(self.term_notebook, True, True, 0)
        self.l_vbox.pack_start(self.button_box, False, False, 0)

        ## Pack it in a vpant bo allow the user to resize
        self.vpane = gtk.VPaned()
        self.vpane.pack1(h_vbox, True, False)
        self.vpane.pack2(self.l_vbox, True, True)
        self.add(self.vpane)

        ## signals from the tab plugins (LocalCommandsList and so)
        self.cmd_notebook.connect('run_command',
            lambda wdg, *args: self.term_notebook.run_command(*args))
        self.cmd_notebook.connect('show_man',
                lambda wgt, cmd: cc_helpers.ManPage(cmd).run())
        self.cmd_notebook.connect('quit', lambda *x: gtk.main_quit())
        ## Signals from the terminals notebook
        self.term_notebook.connect('quit', lambda *x: gtk.main_quit())
        self.term_notebook.connect('preferences', lambda *x: self.edit_pref())
        ## expander
        self.expander.connect('notify::expanded',
                lambda *x: self.expanded_cb())
        ## Signals on the main window
        self.connect("delete_event", self.delete_event)
        self.connect("key-press-event", self.key_clicked)
        ## Signals from the menus
        menu_bar.connect('quit', lambda *x: gtk.main_quit())
        menu_bar.connect('run_command',
                lambda *x: self.cmd_notebook.run_command())
        menu_bar.connect('cancel_command',
                lambda *x: self.term_notebook.cancel_command())
        menu_bar.connect('stop_command',
                lambda *x: self.term_notebook.stop_command())
        menu_bar.connect('resume_command',
                lambda *x: self.term_notebook.resume_command())
        menu_bar.connect('background_command',
                lambda *x: self.term_notebook.background_command())
        menu_bar.connect('foreground_command',
                lambda *x: self.term_notebook.foreground_command())
        menu_bar.connect('bgrun_command',
                lambda *x: self.term_notebook.bgrun_command())
        menu_bar.connect('add_command',
                lambda *x: self.cmd_notebook.add_command())
        menu_bar.connect('edit_command',
                lambda *x: self.cmd_notebook.edit_command())
        menu_bar.connect('remove_command',
                lambda *x: self.cmd_notebook.remove_command())
        menu_bar.connect('preferences', lambda *x: self.edit_pref())
        menu_bar.connect('add_tab', lambda *x: self.term_notebook.add_tab())
        menu_bar.connect('close_tab', lambda *x: self.term_notebook.quit_tab())
        ## signals from the buttons
        self.button_box.connect('quit', lambda *x: gtk.main_quit())
        self.button_box.connect('run_command',
                lambda *x: self.cmd_notebook.run_command())
        self.button_box.connect('cancel_command',
                lambda *x: self.term_notebook.cancel_command())
        self.button_box.connect('add_command',
                lambda *x: self.cmd_notebook.add_command())
        self.button_box.connect('edit_command',
                lambda *x: self.cmd_notebook.edit_command())
        self.button_box.connect('remove_command',
                lambda *x: self.cmd_notebook.remove_command())
        self.button_box.connect('show_man',
                lambda *x: cc_helpers.ManPage(
                    self.cmd_notebook.get_command()[0]).run())
        self.button_box.connect('add_tab',
                lambda *x: self.term_notebook.add_tab())
        ## show everything
        self.show_all()
        ## set the focus on the terminal
        self.term_notebook.focus()
        return

    def load_plugins(self):
        self.pluginloader = cc_plugins.PluginLoader()
        self.reload_plugins()

    def reload_plugins(self):
        (head, _tail) = os.path.split(cc_plugins.__file__)
        pluginspath = os.path.join(head.rsplit(os.sep, 1)[0], 'plugins')
        allowed = [plg.strip() for plg in self.config.get('general::default',
                                                        'plugins').split(',')]
        dbg('Allowed plugins: %s' % allowed.__repr__())
        self.pluginloader.load(pluginspath, allowed)

    def expanded_cb(self):
        #liststore in a scrolled window in an expander
        if self.expander.get_expanded():
            self.search_hbox.show_all()
            self.cmd_notebook.show_all()
            self.cmd_notebook.set_current_page(self.currentpage)
            self.button_box.show_all()
            self.vpane.set_position(self.currentpos)
        else:
            self.currentpage = self.cmd_notebook.get_current_page()
            self.currentpos = self.vpane.get_position()
            self.cmd_notebook.hide_all()
            self.search_hbox.hide_all()
            self.button_box.hide_all()
            self.vpane.set_position(0)
        return

    def init_config(self):
        ## Set the netbookmode if needed
        screen = gtk.gdk.display_get_default().get_default_screen()
        height = screen.get_height()
        if height < 750:
            self.cmd_notebook.set_netbook(True)
            self.set_default_size(700, 500)
        else:
            self.set_default_size(700, 625)
        self.set_border_width(5)
        ## Sets the position of the window relative to the screen
        self.set_position(gtk.WIN_POS_CENTER_ALWAYS)
        ## Allow user to resize window
        self.set_resizable(True)

        ## set Window title and icon
        self.set_title("CLI Companion")
        icon = gtk.gdk.pixbuf_new_from_file(
                "/usr/share/pixmaps/clicompanion.16.png")
        self.set_icon(icon)

        ##For now TERM is hardcoded to xterm because of a change
        ##in libvte in Ubuntu Maverick
        os.putenv('TERM', 'xterm')

        ## style to reduce padding around tabs
        ## TODO: Find a better place for this?
        gtk.rc_parse_string("style \"tab-close-button-style\"\n"
             "{\n"
               "GtkWidget::focus-padding = 0\n"
               "GtkWidget::focus-line-width = 0\n"
               "xthickness = 0\n"
               "ythickness = 0\n"
             "}\n"
             "widget \"*.tab-close-button\" style \"tab-close-button-style\"")

    def edit_pref(self):
        pref_win = cc_pref.PreferencesWindow(
            self.config.get_config_copy(), self.pluginloader)
        newconfig, changed_plugins = pref_win.run()
        if newconfig:
            self.config = newconfig
            self.config.save()
            dbg(', '.join([self.config.get('profile::default', opt)
                    for opt in self.config.options('profile::default')]))
        self.reload_plugins()
        self.term_notebook.update_all_term_config(self.config)
        self.cmd_notebook.update(self.config, changed_plugins)

    def delete_event(self, widget,  data=None):
        # close the window and quit
        gtk.main_quit()
        return False

    def key_pressed(self, event):
        keyname = cc_utils.get_keycomb(event)
        if keyname in cc_pref.KEY_BINDINGS.keys():
            key, func = cc_pref.KEY_BINDINGS[keyname]

    def key_clicked(self, widget, event):
        if cc_utils.only_modifier(event):
            return
        keycomb = cc_utils.get_keycomb(event)
        for func in cc_config.KEY_BINDINGS.keys():
            if keycomb == self.config.get('keybindings', func):
                getattr(self, func)()
                ## this is to stop sending the keypress to the widgets
                return True

    def run_command(self):
        self.cmd_notebook.run_command()

    def cancel_command(self):
        self.term_notebook.cancel_command()

    def add_command(self):
        self.cmd_notebook.add_command()

    def remove_command(self):
        self.cmd_notebook.remove_command()

    def edit_command(self):
        self.cmd_notebook.edit_command()

    def add_tab(self):
        self.term_notebook.add_tab()

    def close_tab(self):
        self.term_notebook.quit_tab()

    def next_tab(self):
        self.term_notebook.next_tab()

    def previous_tab(self):
        self.term_notebook.prev_tab()

    def move_tab_right(self):
        self.term_notebook.move_tab_right()

    def move_tab_left(self):
        self.term_notebook.move_tab_left()

    def copy(self):
        self.term_notebook.copy()

    def paste(self):
        text = self.clipboard.wait_for_text() or ''
        self.term_notebook.paste(text)

    def toggle_hide_ui(self):
        if self.hiddenui:
            self.show_ui()
        else:
            self.hide_ui()

    def hide_ui(self):
        if self.hiddenui:
            return
        dbg('Hide UI')
        self.set_border_width(0)
        self.l_vbox.remove(self.term_notebook)
        self.remove(self.vpane)
        self.add(self.term_notebook)
        self.hiddenui = True
        ## set the focus on the terminal
        self.term_notebook.focus()

    def show_ui(self):
        if not self.hiddenui:
            return
        dbg('Show UI')
        self.set_border_width(5)
        self.remove(self.term_notebook)
        btns = self.l_vbox.get_children()[0]
        self.l_vbox.remove(btns)
        self.l_vbox.pack_start(self.term_notebook, True, True, 0)
        self.l_vbox.pack_start(btns, False, False, 0)
        self.add(self.vpane)
        self.hiddenui = False
        ## set the focus on the terminal
        self.term_notebook.focus()

    def toggle_maximize(self):
        if not self.maximized:
            self.maximize()
        else:
            self.unmaximize()
        ## set the focus on the terminal
        self.term_notebook.focus()
        self.maximized = not self.maximized

    def toggle_fullscreen(self):
        '''
        Maximize and hide everything, or unmaximize and unhide if it was on
        fullscren mode
        '''
        if not self.fullscr:
            self.hide_ui()
            self.fullscreen()
            self.set_border_width(0)
        else:
            self.show_ui()
            self.unfullscreen()
            self.set_border_width(5)
        self.fullscr = not self.fullscr
        ## set the focus on the terminal
        self.term_notebook.focus()

    def main(self):
        try:
            gtk.main()
        except KeyboardInterrupt:
            pass


def run(options=None):
    if options and options.conffile:
        config = cc_config.CLIConfig(conffile)
    else:
        config = cc_config.CLIConfig()
    if config.get('general::default', 'debug') == 'True' or options.debug:
        cc_utils.DEBUG = True
    main_window = MainWindow(
                config=config)
    main_window.main()
