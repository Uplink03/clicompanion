#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# tabs.py - Terminal tab handling classes for clicompanion
#
# Copyright 2010 Duane Hinnen, Kenny Meyer, Marcos Vanetta, David Caro
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
# This file contains the classes used to provide the terminals secion of the
# main window.
#
# TerminalTab: This class implements one tab of the terminals notebook, with
# it's own profile and vte associated.
#
# TerminalsNotebook: This class implements the notebook, where the terminals
# will be added.
#

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Vte", "2.91")

from gi.repository import Gtk as gtk
from gi.repository import Vte as vte
from gi.repository import Gdk as gdk
import re
from gi.repository import GObject as gobject
from gi.repository import Pango as pango
from clicompanionlib.utils import dbg, parse_rgba
import clicompanionlib.utils as cc_utils
import clicompanionlib.helpers as cc_helpers
import clicompanionlib.preferences as cc_pref
import clicompanionlib.config as cc_conf

from gi.repository import GLib

class TerminalTab(gtk.ScrolledWindow):
    __gsignals__ = {
         'quit': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                             ()),
         'add_tab': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                             ()),
         'rename': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                             (str, )),
         'preferences': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                             ()),
    }

    def __init__(self, title, config, profile='default', directory=None,
                    pluginloader=None):
        gtk.ScrolledWindow.__init__(self)
        self.config = config
        self.pluginloader = pluginloader
        self.title = title
        self.profile = 'profile::' + profile
        self.vte = vte.Terminal()
        self.matches = {}
        self.add(self.vte)
        self.vte.connect("child-exited", lambda *x: dbg(x))
        self.update_records = self.config.getboolean(self.profile,
                                        'update_login_records')
        dbg('Updating login records: ' + self.update_records.__repr__())
        self.pid = self.vte.spawn_async(
            vte.PtyFlags.DEFAULT,
            directory,
            [cc_utils.shell_lookup()],
            None,
            GLib.SpawnFlags.DEFAULT,
            None,
            (None, ),
            -1,
            None,
            None,
            None,
        )
        self.vte.connect("button_press_event", self.on_click)
        self.update_config()
        self.show_all()

    def update_config(self, config=None, preview=False):
        if not config:
            config = self.config
        elif not preview:
            self.config = config
        if self.profile not in config.sections():
            self.profile = 'profile::default'
            if self.profile not in config.sections():
                config.add_section(self.profile)
        dbg(self.profile)
        dbg(','.join([config.get(self.profile, option)
                     for option in config.options(self.profile)]))

        ## Scrollback
        try:
            config_scrollback = config.getint(self.profile, 'scrollb')
        except ValueError:
            print(_("WARNING: Invalid value for property '%s', int expected:"
                    " got '%s', using default '%s'") % (
                        'scrollb',
                        config.get(self.profile, 'scrollb'),
                        config.get('DEFAULT', 'scrollb')))
            config.set(self.profile, 'scrollb',
                        config.get('DEFAULT', 'scrollb'))
            config_scrollback = config.getint('DEFAULT', 'scrollb')
        self.vte.set_scrollback_lines(config_scrollback)

        color = ('#2e3436:#cc0000:#4e9a06:#c4a000:#3465a4:#75507b:#06989a:'
                '#d3d7cf:#555753:#ef2929:#8ae234:#fce94f:#729fcf:#ad7fa8:'
                '#34e2e2:#eeeeec')
        colors = color.split(':')
        palette = []
        for color in colors:
            if color:
                palette.append(parse_rgba(color))

        #### Colors
        if config.getboolean(self.profile, 'use_system_colors'):
            config_color_fore = self.vte.get_style().text[gtk.StateType.Normal]
            config_color_back = self.vte.get_style().base[gtk.StateType.Normal]
        else:
            color_scheme = config.get(self.profile, 'color_scheme')
            if color_scheme != 'Custom':
                fgcolor, bgcolor = cc_pref.COLOR_SCHEMES[color_scheme]
            else:
                fgcolor = config.get(self.profile, 'colorf')
                bgcolor = config.get(self.profile, 'colorb')

            try:
                config_color_fore = parse_rgba(fgcolor)
            except ValueError as e:
                print(_("WARNING: Invalid value for property '%s':"
                        " got '%s', using default '%s'.") % (
                            'colorf',
                            fgcolor,
                            config.get('DEFAULT', 'colorf')))
                config.set(self.profile, 'colorf',
                            config.get('DEFAULT', 'colorf'))
                config_color_fore = parse_rgba(config.get('DEFAULT',
                                                            'colorf'))

            try:
                config_color_back = parse_rgba(bgcolor)
            except ValueError as e:
                print(_("WARNING: Invalid value for property '%s':"
                        " got '%s', using default '%s'.") % (
                            'colorb',
                            bgcolor,
                            config.get('DEFAULT', 'colorb')))
                config.set(self.profile, 'colorb',
                        config.get('DEFAULT', 'colorb'))
                config_color_back = parse_rgba(config.get('DEFAULT',
                                                        'colorb'))
        self.vte.set_colors(config_color_fore, config_color_back, palette)

        ### Encoding
        config_encoding = config.get(self.profile, 'encoding')
        if config_encoding.upper() not in [enc.upper()
                                          for enc, desc
                                          in cc_utils.encodings]:
            print(_("WARNING: Invalid value for property '%s':"
                    " got '%s', using default '%s'") \
                    % ('encoding', config_encoding,
                        config.get('DEFAULT', 'encoding')))
            config.set(self.profile, 'encoding',
                        config.get('DEFAULT', 'encoding'))
            config_encoding = config.get('DEFAULT', 'encoding')
        self.vte.set_encoding(config_encoding)

        ## Font
        if config.getboolean(self.profile, 'use_system_font'):
            fontname = cc_utils.get_system_font(
                        lambda *x: self.update_config())
        else:
            fontname = config.get(self.profile, 'font')
        font = pango.FontDescription(fontname)
        if not font or not fontname:
            print(_("WARNING: Invalid value for property '%s':"
                    " got '%s', using default '%s'") % (
                        'font',
                        fontname,
                        cc_utils.get_system_font()))
            config.set('DEFAULT', 'font', c_utils.get_system_font())
            fontname = config.get('DEFAULT', 'font')
        font = pango.FontDescription(fontname)
        if font:
            self.vte.set_font(font)

        update_records = config.getboolean(self.profile,
                                           'update_login_records')
        if update_records != self.update_records:
            if not preview:
                self.update_records = update_records
            dbg('Updating login records: ' + update_records.__repr__())
            self.vte.feed('\n\r')
            self.vte.fork_command(cc_utils.shell_lookup(),
               logutmp=update_records,
               logwtmp=update_records,
               loglastlog=update_records)

        self.vte.set_allow_bold(config.getboolean(self.profile, 'bold_text'))
        self.vte.set_word_char_exceptions(config.get(self.profile, 'sel_word'))
        self.vte.match_remove_all()
        self.load_url_plugins()

    def check_for_match(self, event):
        """
        Check if the mouse is over a URL
        """
        return (self.vte.match_check(int(event.x / self.vte.get_char_width()),
            int(event.y / self.vte.get_char_height())))

    def run_match_callback(self, match):
        url = match[0]
        match = match[1]
        for plg, m_plg in self.matches.items():
            if match in m_plg[1]:
                dbg('Matched %s for url %s' % (plg, url))
                matchnum = m_plg[1].index(match)
                m_plg[0].callback(url, matchnum)

    def on_click(self, vte, event):
        ## left click
        if event.button == 1:
            # Ctrl+leftclick on a URL should open it
            if event.state & gdk.ModifierType.CONTROL_MASK == gdk.ModifierType.CONTROL_MASK:
                match = self.check_for_match(event)
                if match:
                    self.run_match_callback(match)
        ## Rght click menu
        if event.button == 3:
            time = event.time
            ## right-click popup menu Copy
            popupMenu = gtk.Menu()
            menuPopup1 = gtk.ImageMenuItem(gtk.STOCK_COPY)
            popupMenu.add(menuPopup1)
            menuPopup1.connect('activate', lambda x: vte.copy_clipboard())
            ## right-click popup menu Paste
            menuPopup2 = gtk.ImageMenuItem(gtk.STOCK_PASTE)
            popupMenu.add(menuPopup2)
            menuPopup2.connect('activate', lambda x: vte.paste_clipboard())
            ## right-click popup menu Rename
            menuPopup3 = gtk.ImageMenuItem(gtk.STOCK_EDIT)
            menuPopup3.set_label(_('Rename'))
            popupMenu.add(menuPopup3)
            menuPopup3.connect('activate', lambda x: self.rename())
            ## right-click popup menu Configure
            menuPopup3 = gtk.ImageMenuItem(gtk.STOCK_PREFERENCES)
            menuPopup3.set_label(_('Configure'))
            popupMenu.add(menuPopup3)
            menuPopup3.connect('activate', lambda x: self.emit('preferences'))
            ## right-click popup menu Add Tab
            menuPopup3 = gtk.ImageMenuItem(gtk.STOCK_ADD)
            menuPopup3.set_label(_('Add tab'))
            popupMenu.add(menuPopup3)
            menuPopup3.connect('activate', lambda x: self.emit('add_tab'))
            ## right-click popup menu Process
            menu_signal = gtk.ImageMenuItem(gtk.STOCK_JUMP_TO)
            menu_signal.set_label(_('Process'))
            submenu_signal = gtk.Menu()
            menu_signal.set_submenu(submenu_signal)
            popupMenu.add(menu_signal)
            ## Submenu Abort
            subitem = gtk.ImageMenuItem(gtk.STOCK_STOP)
            subitem.set_label(_('Abort (Ctrl+c)'))
            submenu_signal.add(subitem)
            subitem.connect('activate',
                                lambda *x: self.cancel_command())
            ## Submenu Pause
            subitem = gtk.ImageMenuItem(gtk.STOCK_MEDIA_PAUSE)
            subitem.set_label(_('Pause (Ctrl+s)'))
            submenu_signal.add(subitem)
            subitem.connect('activate',
                                lambda *x: self.stop_command())
            ## Submenu Resume
            subitem = gtk.ImageMenuItem(gtk.STOCK_MEDIA_PLAY)
            subitem.set_label(_('Resume (Ctrl+q)'))
            submenu_signal.add(subitem)
            subitem.connect('activate',
                                lambda *x: self.resume_command())
            ## Submenu Background Suspend
            subitem = gtk.ImageMenuItem(gtk.STOCK_GOTO_BOTTOM)
            subitem.set_label(_('Stop and Background (Ctrl+z)'))
            submenu_signal.add(subitem)
            subitem.connect('activate',
                                lambda *x: self.background_command())
            ## Submenu Foreground
            subitem = gtk.ImageMenuItem(gtk.STOCK_GO_UP)
            subitem.set_label(_('Foreground (%)'))
            submenu_signal.add(subitem)
            subitem.connect('activate',
                                lambda *x: self.foreground_command())
            ## Submenu Background run
            subitem = gtk.ImageMenuItem(gtk.STOCK_GO_DOWN)
            subitem.set_label(_('Run in background (% &)'))
            submenu_signal.add(subitem)
            subitem.connect('activate',
                                lambda *x: self.bgrun_command())
            ## right-click popup menu Profiles
            menuit_prof = gtk.MenuItem()
            menuit_prof.set_label(_('Profiles'))
            submenu_prof = gtk.Menu()
            menuit_prof.set_submenu(submenu_prof)
            popupMenu.add(menuit_prof)
            for section in self.config.sections():
                if section.startswith('profile::'):
                    subitem = gtk.MenuItem()
                    subitem.set_label(_(section[9:]))
                    submenu_prof.add(subitem)
                    subitem.connect('activate',
                        lambda wg, *x: self.change_profile(
                            wg.get_label()))
            ## right-click popup menu Close Tab
            menuPopup3 = gtk.ImageMenuItem(gtk.STOCK_CLOSE)
            menuPopup3.set_label(_('Close tab'))
            popupMenu.add(menuPopup3)
            menuPopup3.connect('activate', lambda x: self.emit('quit'))
            ## Show popup menu
            popupMenu.show_all()
            popupMenu.popup_at_pointer()
            return True

    def rename(self):
        dlg = gtk.Dialog("Enter the new name",
                   None,
                   gtk.DialogFlags.MODAL | gtk.DialogFlags.DESTROY_WITH_PARENT,
                   (gtk.STOCK_CANCEL, gtk.ResponseType.REJECT,
                    gtk.STOCK_OK, gtk.ResponseType.ACCEPT))
        entry = gtk.Entry()
        entry.connect("activate", lambda *x: dlg.response(gtk.ResponseType.ACCEPT))
        entry.set_text(self.title)
        dlg.vbox.pack_start(entry, True, True, 0)
        dlg.show_all()
        response = dlg.run()
        if response == gtk.ResponseType.ACCEPT:
            text = entry.get_text()
            self.emit('rename', text)
        dlg.destroy()

    def run_command(self, cmd, ui, desc):
        if not cmd:
            dbg('Empty command... doing nothing')
            return
        '''
        Make sure user arguments were found. Replace ? with something
        .format can read. This is done so the user can just enter ?, when
        adding a command where arguments are needed, instead
        of {0[1]}, {0[1]}, {0[2]}
        '''
        ## find how many ?(user arguments) are in command
        match = re.findall('\\?', cmd)
        if match:
            num = len(match)
            ran = 0
            new_cmd = cc_utils.replace(cmd, num, ran)

        if len(match) > 0:  # command with user input
            dbg('command with ui')
            cmd_info_win = cc_helpers.CommandInfoWindow(new_cmd, ui, desc)
            cmd = cmd_info_win.run()
            if cmd == None:
                return
        self.vte.feed_child(bytes(cmd + "\n", 'UTF-8'))  # send command
        self.show()
        self.grab_focus()

    def cancel_command(self):
        self.vte.feed_child(bytes(chr(3), 'ASCII'))

    def stop_command(self):
        self.vte.feed_child(bytes(chr(19), 'ASCII'))

    def resume_command(self):
        self.vte.feed_child(bytes(chr(17), 'ASCII'))

    def background_command(self):
        self.vte.feed_child(bytes(chr(26), 'ASCII'))

    def foreground_command(self):
        self.vte.feed_child(bytes('%\n', 'UTF-8'))

    def bgrun_command(self):
        self.vte.feed_child(bytes('% &\n', 'UTF-8'))

    def change_profile(self, profile):
        dbg(profile)
        self.profile = 'profile::' + profile
        self.update_config()

    def load_url_plugins(self):
        for pg_name, pg_class in self.pluginloader.get_plugins(['URL']):
            pg_conf = cc_conf.CLIConfigView(pg_name, self.config)
            self.matches[pg_name] = (pg_class(pg_conf), [])
            for match in self.matches[pg_name][0].matches:
                dbg('Adding match %s for plugin %s' % (match, pg_name))

                PCRE2_FLAGS = 1074398208  # PCRE2_UTF | PCRE2_NO_UTF_CHECK | PCRE2_UCP | PCRE2_MULTILINE
                self.matches[pg_name][1].append(self.vte.match_add_regex(vte.Regex.new_for_match(match, len(match), PCRE2_FLAGS), 0))


class TerminalsNotebook(gtk.Notebook):
    __gsignals__ = {
         'quit': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                             ()),
         'preferences': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                             ()),
    }

    def __init__(self, config, pluginloader):
        gtk.Notebook.__init__(self)
        #definition gcp - global page count, how many pages have been created
        self.gcp = 0
        self.global_config = config
        self.pluginloader = pluginloader
        ## The "Add Tab" tab
        add_tab_button = gtk.Button("+")
        ## tooltip for "Add Tab" tab
        add_tab_button.set_tooltip_text(_("Click to add another tab"))
        ## create first tab
        self.append_page(gtk.Label(""), add_tab_button)
        self.set_tab_reorderable(add_tab_button, False)
        add_tab_button.connect("clicked", lambda *x: self.add_tab())
        self.set_size_request(700, 120)
        self.connect('page-reordered', self.check_order)

    def check_order(self, notebook, child, page_num):
        if page_num == self.get_n_pages() - 1:
            self.reorder_child(child, self.get_n_pages() - 2)

    def move_tab_right(self):
        page = self.get_current_page()
        child = self.get_nth_page(page)
        if page != self.get_n_pages() - 2:
            self.reorder_child(child, page + 1)
        else:
            self.reorder_child(child, 0)

    def move_tab_left(self):
        page = self.get_current_page()
        child = self.get_nth_page(page)
        if page == 0:
            self.reorder_child(child, self.get_n_pages() - 2)
        else:
            self.reorder_child(child, page - 1)

    def focus(self):
        num = self.get_current_page()
        self.get_nth_page(num).vte.grab_focus()

    def add_tab(self, title=None):
        dbg('Adding a new tab')
        self.gcp += 1
        if title == None:
            title = 'Tab %d' % self.gcp

        cwd = None
        if self.get_n_pages() > 1:
            dbg('More than one tab, showing them.')
            self.set_show_tabs(True)
            current_page = self.get_nth_page(self.get_current_page())
            cwd = cc_utils.get_pid_cwd(current_page.pid)
        if cwd:
            newtab = TerminalTab(title, self.global_config, directory=cwd,
                                    pluginloader=self.pluginloader)
        else:
            newtab = TerminalTab(title, self.global_config,
                                    pluginloader=self.pluginloader)
        label = self.create_tab_label(title, newtab)
        self.insert_page(newtab, label, self.get_n_pages() - 1)
        self.set_current_page(self.get_n_pages() - 2)
        self.set_scrollable(True)
        # signal handler for tab
        newtab.connect("quit", lambda *x: self.quit_tab(newtab))
        newtab.connect("add_tab", lambda *x: self.add_tab())
        newtab.connect("preferences", lambda *x: self.emit('preferences'))
        newtab.connect("rename",
                lambda wg, text: self.rename_tab(newtab, text))
        self.set_tab_reorderable(newtab, True)
        self.focus()
        return newtab

    def create_tab_label(self, title, tab):
        ## Create the tab's labe with button
        box = gtk.HBox()
        label = gtk.Label(title)
        box.pack_start(label, True, True, 0)
        ## x image for tab close button
        close_image = gtk.Image.new_from_stock(gtk.STOCK_CLOSE,
                                               gtk.IconSize.MENU)
        ## close button
        closebtn = gtk.Button()
        closebtn.set_relief(gtk.ReliefStyle.NONE)
        closebtn.set_focus_on_click(True)
        closebtn.add(close_image)
        ## put button in a box and show box
        box.pack_end(closebtn, False, False, 0)
        box.show_all()
        closebtn.connect("clicked", lambda *x: self.close_tab(tab))
        return box

    def rename_tab(self, tab, newname):
        dbg('Renaming tab to %s' % newname)
        label = self.create_tab_label(newname, tab)
        self.set_tab_label(tab, label)
        self.focus()

    ## Remove a page from the notebook
    def close_tab(self, tab):
        ## get the page number of the tab we wanted to close
        pagenum = self.page_num(tab)
        ## and close it
        self.remove_page(pagenum)
        if self.get_n_pages() < 3:
            self.set_show_tabs(False)

        # check if the focus does not go to the last page (ie with only a +
        # sign)
        if self.get_current_page() == self.get_n_pages() - 1:
            self.prev_page()
        if self.get_n_pages() != 1:
            self.focus()

    def next_tab(self):
        if self.get_current_page() == self.get_n_pages() - 2:
            self.set_current_page(0)
        else:
            self.next_page()

    def prev_tab(self):
        if self.get_current_page() == 0:
            self.set_current_page(self.get_n_pages() - 2)
        else:
            self.prev_page()

    def quit_tab(self, tab=None):
        if not tab:
            tab = self.get_nth_page(self.get_current_page())
        self.close_tab(tab)
        if self.get_n_pages() == 1:
            self.emit('quit')

    def get_page(self):
        ## get the current notebook page
        pagenum = self.get_current_page()
        return self.get_nth_page(pagenum)

    def run_command(self, cmd, ui, desc):
        self.get_page().run_command(cmd, ui, desc)
        self.focus()

    def cancel_command(self):
        self.get_page().cancel_command()
        self.focus()

    def stop_command(self):
        self.get_page().stop_command()
        self.focus()

    def resume_command(self):
        self.get_page().resume_command()
        self.focus()

    def background_command(self):
        self.get_page().background_command()
        self.focus()

    def foreground_command(self):
        self.get_page().foreground_command()
        self.focus()

    def bgrun_command(self):
        self.get_page().bgrun_command()
        self.focus()

    def update_all_term_config(self, config=None):
        self.global_config = config
        for pagenum in range(self.get_n_pages()):
            page = self.get_nth_page(pagenum)
            if isinstance(page, TerminalTab):
                self.update_term_config(page, config)

    def update_term_config(self, tab, config=None):
        ##set terminal preferences from conig file data
        if not config:
            config = self.global_config
        tab.update_config(config)

    def copy(self):
        self.get_page().vte.copy_clipboard()

    def paste(self, text):
        self.get_page().vte.feed_child(bytes(text, 'UTF-8'))
