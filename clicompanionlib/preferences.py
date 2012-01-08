#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# preferences.py - Preferences dialogs for clicompanion
#                                                                                                             
# Copyright 2012 Duane Hinnen, Kenny Meyer, Marcos Vanettai, Marek Bardoński,
#                David Caro <david.caro.estevez@gmail.com>
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
############################################
## The preferences window is a popup that shows all the configuration options
## allowing the user to change them, also handles the profiles creatin and
## delete.
##
## The main class is the PreferencesWindow, that has all the other packed. Each
## as a tab inside the preferences window.
## The other classes are:
##   - PluginsTab: handles the plugin activation and configuration
##   - KeybindingsTab: handles the keybindings
##   - ProfilesTab: The main tab for the profiles setting, this class is a
##                   notebook with three classes (tabs) packed
##      - ProfScrollingTab: the scrolling options tab inside the profiles tab
##      - ProfColorsTab: the colors tab
##      - ProfGeneralTab: the general setting tab
##
## About the profiles: each profile is a configuration section in the config
## file with the name 'profile::profilename', having always the profile
## 'profile::default', the will have all the default options (if it is not
## found, it will be created with the harcoded options inside the code.

import pygtk
pygtk.require('2.0')
import gtk
import gobject
import clicompanionlib.config as cc_config
import clicompanionlib.utils as cc_utils
from clicompanionlib.utils import dbg

COLOR_SCHEMES = {
        'Grey on Black': ['#aaaaaa', '#000000'],
        'Black on Yellow': ['#000000', '#ffffdd'],
        'Black on White': ['#000000', '#ffffff'],
        'White on Black': ['#ffffff', '#000000'],
        'Green on Black': ['#00ff00', '#000000'],
        'Orange on Black': ['#e53c00', '#000000'],
        'Custom': []
        }


def color2hex(color_16b):
    """
    Pull the colour values out of a Gtk ColorPicker widget and return them
    as 8bit hex values, sinces its default behaviour is to give 16bit values
    """
    return('#%02x%02x%02x' % (color_16b.red >> 8,
                              color_16b.green >> 8,
                              color_16b.blue >> 8))


class ProfGeneralTab(gtk.VBox):
    def __init__(self, config, profile='default'):
        gtk.VBox.__init__(self)
        self.config = config
        self.profile = profile
        self.draw_all()

    def draw_all(self):
        ## 'use_system_font'
        self.systemfont = gtk.CheckButton(label=_('Use system fixed'
                                                  'width font'))
        self.pack_start(self.systemfont, False, False, 8)
        self.systemfont.set_active(
                self.config.getboolean('profile::' + self.profile,
                                       'use_system_font'))
        self.systemfont.connect('toggled', lambda *x: self.update_font_btn())

        ## 'font'
        font_box = gtk.HBox()
        font_box.pack_start(gtk.Label('Font:'), False, False, 8)
        self.fontbtn = gtk.FontButton(self.config.get('profile::'
                                            + self.profile, 'font'))
        font_box.pack_start(self.fontbtn, False, False, 8)
        self.pack_start(font_box, False, False, 8)
        ## 'bold_text'
        self.bold_text = gtk.CheckButton(label=_('Allow bold text'))
        self.pack_start(self.bold_text, False, False, 8)
        self.bold_text.set_active(self.config.getboolean('profile::'
                                                + self.profile, 'bold_text'))
        ## 'antialias'
        self.antialias = gtk.CheckButton(label=_('Anti-alias text'))
        self.pack_start(self.antialias, False, False, 8)
        self.antialias.set_active(self.config.getboolean('profile::'
                                                + self.profile, 'antialias'))
        ## 'sel_word'
        sel_word_box = gtk.HBox()
        sel_word_box.pack_start(gtk.Label('Select-by-word characters:'))
        self.sel_word_text = gtk.Entry()
        self.sel_word_text.set_text(self.config.get('profile::'
                                                + self.profile, 'sel_word'))
        sel_word_box.pack_start(self.sel_word_text, False, False, 0)
        self.pack_start(sel_word_box, False, False, 8)
        ## System subsection
        sys_lbl = gtk.Label()
        sys_lbl.set_markup('<b>System Configuration</b>')
        self.pack_start(sys_lbl, False, False, 4)
        ## 'update_login_records'
        self.update_login_records = gtk.CheckButton(
                                        label=_('Update login records'))
        self.pack_start(self.update_login_records, False, False, 8)
        self.update_login_records.set_active(
            self.config.getboolean('profile::' + self.profile,
                                    'update_login_records'))
        self.update_font_btn()

    def update_font_btn(self):
        if self.systemfont.get_active():
            self.fontbtn.set_sensitive(False)
        else:
            self.fontbtn.set_sensitive(True)

    def save_changes(self):
        if 'profile::' + self.profile in self.config.sections():
            self.config.set('profile::' + self.profile,
                'use_system_font', '%s' % self.systemfont.get_active())
            self.config.set('profile::' + self.profile,
                'font', '%s' % self.fontbtn.get_font_name())
            self.config.set('profile::' + self.profile,
                'bold_text', '%s' % self.bold_text.get_active())
            self.config.set('profile::' + self.profile,
                'antialias', '%s' % self.antialias.get_active())
            self.config.set('profile::' + self.profile,
                'sel_word', self.sel_word_text.get_text())
            self.config.set('profile::' + self.profile,
                'update_login_records',
                '%s' % self.update_login_records.get_active())

    def set_profile(self, profile='default'):
        self.save_changes()
        if profile != self.profile:
            self.profile = profile
            self.update()
            self.show_all()

    def update(self):
        for child in self.get_children():
            self.remove(child)
        self.draw_all()


class ProfColorsTab(gtk.VBox):
    def __init__(self, config, profile='default'):
        gtk.VBox.__init__(self)
        self.config = config
        self.profile = profile
        self.draw_all()

    def draw_all(self):
        ## 'use_system_colors'
        self.systemcols = gtk.CheckButton(
                            label=_('Use colors from system theme'))
        self.pack_start(self.systemcols, False, False, 8)
        self.systemcols.set_active(
                self.config.getboolean('profile::' + self.profile,
                                       'use_system_colors'))
        self.systemcols.connect('toggled', lambda *x: self.update_sys_colors())

        ## 'color_scheme'
        hbox = gtk.HBox()
        hbox.pack_start(gtk.Label('Color scheme:'), False, False, 8)
        self.colsch_combo = gtk.combo_box_new_text()
        color_scheme = self.config.get('profile::' + self.profile,
                                        'color_scheme')
        self.colsch_combo.append_text('Custom')
        if color_scheme == 'Custom':
            self.colsch_combo.set_active(0)
        hbox.pack_start(self.colsch_combo, False, False, 8)
        i = 0
        for cs, colors in COLOR_SCHEMES.items():
            i = i + 1
            self.colsch_combo.append_text(cs)
            if color_scheme == cs:
                self.colsch_combo.set_active(i)
        self.pack_start(hbox, False, False, 8)
        self.colsch_combo.connect('changed',
                lambda *x: self.update_color_btns())

        ## 'colorf'
        hbox = gtk.HBox()
        hbox.pack_start(gtk.Label('Font color:'), False, False, 8)
        self.colorf = gtk.ColorButton()
        hbox.pack_start(self.colorf, False, False, 8)
        self.pack_start(hbox, False, False, 8)
        self.colorf.connect('color-set', lambda *x: self.update_custom_color())

        ## 'colorb'
        hbox = gtk.HBox()
        hbox.pack_start(gtk.Label('Background color:'), False, False, 8)
        self.colorb = gtk.ColorButton()
        hbox.pack_start(self.colorb, False, False, 8)
        self.pack_start(hbox, False, False, 8)
        self.colorb.connect('color-set', lambda *x: self.update_custom_color())

        self.update_sys_colors()

    def update_sys_colors(self):
        if not self.systemcols.get_active():
            self.colsch_combo.set_sensitive(True)
            self.update_color_btns()
        else:
            self.colsch_combo.set_sensitive(False)
            self.update_color_btns()
            self.colorb.set_sensitive(False)
            self.colorf.set_sensitive(False)

    def update_color_btns(self):
        color_scheme = self.colsch_combo.get_active_text()
        if color_scheme != 'Custom':
            self.colorb.set_sensitive(False)
            self.colorf.set_sensitive(False)
            self.colorf.set_color(gtk.gdk.color_parse(
                    COLOR_SCHEMES[color_scheme][0]))
            self.colorb.set_color(gtk.gdk.color_parse(
                    COLOR_SCHEMES[color_scheme][1]))
        else:
            self.colorb.set_sensitive(True)
            self.colorf.set_sensitive(True)
            self.colorf.set_color(gtk.gdk.color_parse(
                    self.config.get('profile::' + self.profile, 'colorf')))
            self.colorb.set_color(gtk.gdk.color_parse(
                    self.config.get('profile::' + self.profile, 'colorb')))

    def update_custom_color(self):
        color_scheme = self.colsch_combo.get_active_text()
        if color_scheme == 'Custom':
            self.config.set('profile::' + self.profile, 'colorf',
                    color2hex(self.colorf.get_color()))
            self.config.set('profile::' + self.profile, 'colorb',
                    color2hex(self.colorb.get_color()))

    def save_changes(self):
        if 'profile::' + self.profile in self.config.sections():
            self.config.set('profile::' + self.profile, 'use_system_colors',
                    self.systemcols.get_active().__repr__())
            self.config.set('profile::' + self.profile, 'color_scheme',
                    self.colsch_combo.get_active_text())
            if self.colsch_combo.get_active_text() == 'Custom':
                self.config.set('profile::' + self.profile, 'colorf',
                        color2hex(self.colorf.get_color()))
                self.config.set('profile::' + self.profile, 'colorb',
                        color2hex(self.colorb.get_color()))

    def set_profile(self, profile='default'):
        self.save_changes()
        if profile != self.profile:
            self.profile = profile
            self.update()
            self.show_all()

    def update(self):
        for child in self.get_children():
            self.remove(child)
        self.draw_all()


class ProfScrollingTab(gtk.VBox):
    def __init__(self, config, profile='default'):
        gtk.VBox.__init__(self)
        self.config = config
        self.profile = 'profile::' + profile
        self.draw_all()

    def draw_all(self):
        hbox = gtk.HBox()
        hbox.pack_start(gtk.Label('Number of history lines:'), False, False, 8)
        self.scrollb_sb = gtk.SpinButton(
            adjustment=gtk.Adjustment(upper=9999, step_incr=1))
        self.scrollb_sb.set_wrap(True)
        self.scrollb_sb.set_numeric(True)
        self.scrollb_sb.set_value(self.config.getint(self.profile, 'scrollb'))
        hbox.pack_start(self.scrollb_sb, False, False, 8)
        self.pack_start(hbox, False, False, 8)

    def set_profile(self, profile='default'):
        if 'profile::' + profile != self.profile:
            self.profile = 'profile::' + profile
            self.update()
            self.show_all()

    def update(self):
        for child in self.get_children():
            self.remove(child)
        self.draw_all()

    def save_changes(self):
        if self.profile in self.config.sections():
            dbg('Setting scrollb to %d' % int(self.scrollb_sb.get_value()))
            self.config.set(self.profile,
                    'scrollb',
                    str(int(self.scrollb_sb.get_value())))


class ProfilesTab(gtk.HBox):
    def __init__(self, config):
        gtk.HBox.__init__(self)
        self.config = config
        self.tabs = []
        self.gprofs = 0

        vbox = gtk.VBox()
        self.proflist = gtk.TreeView(gtk.ListStore(str))
        self.init_proflist()
        hbox = gtk.HBox()
        add_btn = gtk.Button()
        add_btn.add(self.get_img_box('Add', gtk.STOCK_ADD))
        add_btn.connect('clicked', lambda *x: self.add_profile())
        del_btn = gtk.Button()
        del_btn.add(self.get_img_box('Remove', gtk.STOCK_DELETE))
        del_btn.connect('clicked', lambda *x: self.del_profile())
        hbox.pack_start(add_btn, False, False, 0)
        hbox.pack_start(del_btn, False, False, 0)

        vbox.pack_start(self.proflist, True, True, 0)
        vbox.pack_start(hbox, False, False, 0)
        self.pack_start(vbox)

        self.tabs.append(('General', ProfGeneralTab(config)))
        self.tabs.append(('Colors', ProfColorsTab(config)))
        self.tabs.append(('Scrolling', ProfScrollingTab(config)))

        self.options = gtk.Notebook()
        for name, tab in self.tabs:
            self.options.append_page(tab, gtk.Label(_(name)))

        self.proflist.connect('cursor-changed', lambda *x: self.update_tabs())
        self.pack_start(self.options)

    def get_img_box(self, text, img):
        box = gtk.HBox()
        image = gtk.Image()
        image.set_from_stock(img, gtk.ICON_SIZE_BUTTON)
        label = gtk.Label(text)
        box.pack_start(image, False, False, 0)
        box.pack_start(label, False, False, 0)
        return box

    def add_text_col(self, colname, n=0):
        col = gtk.TreeViewColumn()
        col.set_title(_(colname))
        self.render = gtk.CellRendererText()
        self.render.connect('edited',
                lambda cell, path, text: self.added_profile(path, text))
        col.pack_start(self.render, expand=True)
        col.add_attribute(self.render, 'text', n)
        col.set_resizable(True)
        col.set_sort_column_id(n)
        self.proflist.append_column(col)

    def init_proflist(self):
        self.add_text_col('Profile')
        model = self.proflist.get_model()
        for section in self.config.sections():
            if section.startswith('profile::'):
                last = model.append((section[9:],))
                if section == 'profile::default':
                    self.proflist.set_cursor_on_cell(
                        model.get_path(last),
                        self.proflist.get_column(0))
                self.gprofs += 1

    def update_tabs(self):
        selection = self.proflist.get_selection()
        model, iterator = selection.get_selected()
        if not iterator:
            return
        profile = model.get(iterator, 0)[0]
        for name, tab in self.tabs:
            if 'profile::' + profile in self.config.sections():
                tab.set_profile(profile)

    def save_all(self):
        for name, tab in self.tabs:
            tab.save_changes()

    def add_profile(self):
        self.gprofs += 1
        model = self.proflist.get_model()
        iterator = model.append(('New Profile %d' % self.gprofs,))
        self.render.set_property('editable', True)
        self.proflist.grab_focus()
        self.proflist.set_cursor_on_cell(model.get_path(iterator),
                self.proflist.get_column(0),
                start_editing=True)

    def added_profile(self, path, text):
        dbg('Added profile %s' % text)
        if 'profile::' + text in self.config.sections():
            return
        model = self.proflist.get_model()
        model[path][0] = text
        self.render.set_property('editable', False)
        self.config.add_section('profile::' + text)
        self.update_tabs()

    def del_profile(self):
        selection = self.proflist.get_selection()
        model, iterator = selection.get_selected()
        profile = model.get(iterator, 0)[0]
        if profile != 'default':
            self.config.remove_section('profile::' + profile)
            model.remove(iterator)


class KeybindingsTab(gtk.VBox):
    def __init__(self, config):
        gtk.VBox.__init__(self)
        self.config = config
        self.draw_all()

    def draw_all(self):
        self.labels = []
        for kb_func, kb_name in cc_config.KEY_BINDINGS.items():
            hbox = gtk.HBox()
            lbl = gtk.Label(_(kb_name))
            self.labels.append(lbl)
            btn = gtk.Button(self.config.get('keybindings', kb_func))
            btn.connect('clicked',
                lambda wg, func: self.get_key(func), kb_func)
            btn.set_size_request(100, -1)
            hbox.pack_start(btn, False, False, 8)
            del_btn = gtk.Button()
            del_img = gtk.Image()
            del_img.set_from_stock(gtk.STOCK_CLEAR, gtk.ICON_SIZE_BUTTON)
            del_btn.add(del_img)
            del_btn.connect('clicked',
                lambda wg, func: self.get_key(func, 'not used'), kb_func)
            hbox.pack_start(del_btn, False, False, 8)
            hbox.pack_start(lbl, True, True, 8)
            self.pack_start(hbox)

    def update(self):
        for child in self.children():
            self.remove(child)
        self.draw_all()
        self.show_all()

    def get_key(self, func, key=None):
        if key != None:
            self.config.set('keybindings', func, key)
            self.update()
            return
        self.md = gtk.Dialog("Press the new key for '%s'" % func,
                    None,
                    gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT)
        lbl = gtk.Label('Press a key')
        self.md.get_content_area().pack_start((lbl), True, True, 0)
        lbl.set_size_request(100, 100)
        self.md.connect('key-press-event',
            lambda w, event: self.key_pressed(func, event, lbl))
        self.md.connect('key-release-event',
            lambda w, event: self.key_released(event, lbl))
        self.md.show_all()
        self.md.run()

    def key_released(self, event, lbl):
        keycomb = cc_utils.get_keycomb(event)
        combname = ''
        activemods = keycomb.split('+')[:-1]
        released = keycomb.rsplit('+', 1)[-1]
        mods = {'shift': 'shift',
                 'control': 'ctrl',
                 'alt': 'alt',
                 'super': 'super'}
        for mod in mods.keys():
            if mod in released.lower():
                if mods[mod] in activemods:
                    activemods.pop(activemods.index(mods[mod]))
        combname = '+'.join(activemods) + '+'
        if combname == '+':
            combname = 'Press a key'
        lbl.set_text(combname)

    def key_pressed(self, func, event, lbl):
        keycomb = cc_utils.get_keycomb(event)
        if not cc_utils.only_modifier(event):
            self.md.destroy()
            self.config.set('keybindings', func, keycomb)
            self.update()
        else:
            combname = ''
            activemods = keycomb.split('+')[:-1]
            pressed = keycomb.rsplit('+', 1)[-1]
            mods = {'shift': 'shift',
                     'control': 'ctrl',
                     'alt': 'alt',
                     'super': 'super'}
            for mod in mods.keys():
                if mod in pressed.lower():
                    if mods[mod] not in activemods:
                        activemods.append(mods[mod])
            combname = '+'.join(activemods) + '+'
            if combname == '+':
                combname = 'Press a key'
            lbl.set_text(combname)

    def save_all(self):
        pass


class PluginsTab(gtk.HBox):
    __gsignals__ = {
         'changed-plugin': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                             (str, ))
         }

    def __init__(self, config, plugins):
        gtk.HBox.__init__(self)
        self.config = config
        self.plugins = plugins

        self.pluginlist = gtk.TreeView(gtk.ListStore(bool, str))
        first = self.init_pluginlist()
        self.pack_start(self.pluginlist, False, False, 8)

        self.infonb = gtk.Notebook()
        self.generate_infotabs(first)
        self.pack_start(self.infonb, True, True, 8)

        self.pluginlist.connect('row_activated',
                lambda *x: self.toggle_plugin())
        self.pluginlist.connect('cursor-changed',
                lambda *x: self.update_info())

    def init_pluginlist(self):
        self.add_cbox_col('Enabled', 0)
        self.add_text_col('Plugin Name', 1)
        model = self.pluginlist.get_model()
        first = None
        for plugin in self.plugins.get_allowed():
            if not first:
                first = plugin
            model.append((True, plugin))
        for plugin in self.plugins.get_disallowed():
            if not first:
                first = plugin
            model.append((False, plugin))
        self.pluginlist.set_cursor((0,))
        return first

    def add_cbox_col(self, colname, n=0):
        col = gtk.TreeViewColumn()
        col.set_title(_(colname))
        render = gtk.CellRendererToggle()
        col.pack_start(render, expand=True)
        col.add_attribute(render, 'active', n)
        col.set_resizable(True)
        col.set_sort_column_id(n)
        self.pluginlist.append_column(col)

    def add_text_col(self, colname, n=0):
        col = gtk.TreeViewColumn()
        col.set_title(_(colname))
        render = gtk.CellRendererText()
        col.pack_start(render, expand=True)
        col.add_attribute(render, 'text', n)
        col.set_resizable(True)
        col.set_sort_column_id(n)
        self.pluginlist.append_column(col)

    def toggle_plugin(self):
        selection = self.pluginlist.get_selection()
        model, iterator = selection.get_selected()
        oldvalue, plugin = model.get(iterator, 0, 1)
        if plugin == 'LocalCommandList':
            self.show_warning()
            return
        model.set(iterator, 0, not oldvalue)

    def generate_infotabs(self, plugin):
        '''
        Adds the plugins info and config page (if any) to the plugins info
        notebook
        '''
        confplg = self.plugins.get_plugin_conf(plugin)

        if confplg:
            conf_tab = confplg(self.config.get_plugin_conf(plugin))
            self.infonb.append_page(
                    conf_tab,
                    gtk.Label(_('Configutarion')))
            conf_tab.connect('reload',
                lambda wg, pl: self.emit('changed-plugin', plugin),
                plugin)

        self.infonb.append_page(self.generate_infopage(plugin),
                    gtk.Label(_('About')))

    def generate_infopage(self, plugin):
        '''
        Generates the plugins info page
        '''
        info = self.plugins.get_info(plugin)
        authors = self.plugins.get_authors(plugin)
        page = gtk.TextView()
        page.set_wrap_mode(gtk.WRAP_WORD)
        page.set_editable(False)
        buffer = page.get_buffer()
        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        scrolled_window.add(page)
        iter = buffer.get_iter_at_offset(0)
        buffer.insert(iter, info + '\n\nAuthors:\n' + authors)
        return scrolled_window

    def update_info(self):
        selection = self.pluginlist.get_selection()
        model, iterator = selection.get_selected()
        enabled, plugin = model.get(iterator, 0, 1)
        for child in self.infonb.get_children():
            self.infonb.remove(child)
        self.generate_infotabs(plugin)
        self.show_all()

    def save_all(self):
        newenabled = []
        model = self.pluginlist.get_model()
        elem = model.get_iter_first()
        while elem:
            enabled, plugin = model.get(elem, 0, 1)
            if enabled:
                newenabled.append(plugin)
            elem = model.iter_next(elem)
        self.config.set('general::default', 'plugins', ', '.join(newenabled))

    def show_warning(self):
        dlg = gtk.MessageDialog(
                     None,
                     gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                     gtk.MESSAGE_ERROR,
                     gtk.BUTTONS_CLOSE,
                     message_format=_('Can\'t disable "LocalCommandList'))
        dlg.format_secondary_text(_('The plugin "LocalCommandList is the main'
            ' plugin for CLI Companion, and can\'t be disalbed, sorry.'))
        dlg.run()
        dlg.destroy()


class PreferencesWindow(gtk.Dialog):
    '''
    Preferences window, the tabs are needed for the preview
    '''
    __gsignals__ = {
         'preview': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                             (str, str))
         }

    def __init__(self, config, plugins):
        gtk.Dialog.__init__(self, _("User Preferences"),
                     None,
                     gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                     (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                      gtk.STOCK_OK, gtk.RESPONSE_OK))
        self.config = config
        self.plugins = plugins
        self.config_bkp = self.config.get_config_copy()
        self.changed_plugins = []

        mainwdg = self.get_content_area()
        self.tabs = gtk.Notebook()
        mainwdg.pack_start(self.tabs, True, True, 0)

        ## profiles
        proftab = ProfilesTab(config)
        self.tabs.append_page(proftab, gtk.Label('Profiles'))
        ## keybindings
        keybind_tab = KeybindingsTab(config)
        self.tabs.append_page(keybind_tab, gtk.Label('Keybindings'))
        ## plugins
        plug_tab = PluginsTab(config, plugins)
        plug_tab.connect('changed-plugin',
            lambda wg, pl: self.mark_changed_plugins(pl))
        self.tabs.append_page(plug_tab, gtk.Label('Plugins'))

    def mark_changed_plugins(self, plugin):
        if plugin not in self.changed_plugins:
            self.changed_plugins.append(plugin)

    def run(self):
        self.show_all()
        response = gtk.Dialog.run(self)
        if response == gtk.RESPONSE_OK:
            for i in range(self.tabs.get_n_pages()):
                self.tabs.get_nth_page(i).save_all()
            config = self.config
        else:
            config = None
        self.destroy()
        return config, self.changed_plugins
