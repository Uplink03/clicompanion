#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# plugins.py - Plugin related clases for the clicompanion
#
# Copyright 2012 David Caro <david.caro.estevez@gmail.com>
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
#################################################
## The plugins
##
## Here are defined the PluginLoader class and all the plugin base classes.
##
## The PluginLoader class
## This class handles the loading and handpling of the plugins, it get a
## directory and a list of the allowed plugins and loads all the allowed
## plugins that it found on the dir *.py files (a plugin is a class that
## inherits from the base class Plugin defined in this file).
##
## The Plugin class is the base class for all the plugins, if the plugin does
## not inherit from that class, it will not be loaded.
##
## TabPlugin: This is a plugin that will be used as a tab in the upper notebook
## of the application, like the LocalCommandList o CommandLineFU plugins
##
## PluginConfig: this will be the config tab in the preferences for the plugin.
##
## About the plugins:
## The plugins have some attributes that should be set, like the __authors__,
## and the __plugin_info__ attributes, that will be shown in the info page for the
## plugin, and the __title__ that will be the plugin name shown in the plugins
## list.

import gi

gi.require_version("Gtk", "3.0")

from gi.repository import GObject as gobject
from gi.repository import Gtk as gtk
import sys
import os
import inspect
import webbrowser
from clicompanionlib.utils import dbg


class PluginLoader:
    def __init__(self):
        self.plugins = {}
        self.allowed = []

    def load(self, pluginsdir, allowed):
        self.allowed = allowed
        dbg('Allowing only the plugins %s' % allowed.__repr__())
        sys.path.insert(0, pluginsdir)
        try:
            files = os.listdir(pluginsdir)
        except OSError:
            sys.path.remove(pluginsdir)
            return False
        for plugin in files:
            pluginpath = os.path.join(pluginsdir, plugin)
            if not os.path.isfile(pluginpath) or not  plugin[-3:] == '.py':
                continue
            dbg('Searching plugin file %s for plugins...' % plugin)
            try:
                module = __import__(plugin[:-3], globals(), locals(), [''])
                for cname, mclass \
                in inspect.getmembers(module, inspect.isclass):
                    dbg('  Checking if class %s is a plugin.' % cname)
                    if issubclass(mclass, Plugin):
                        if cname not in self.plugins.keys():
                            dbg('    Found plugin %s' % cname)
                            self.plugins[cname] = mclass
                            continue
            except Exception as ex:
                print('Error searching plugin file %s: %s' % (plugin, ex))

    def enable(self, plugins):
        for plugin in plugins:
            if plugin not in self.allowed:
                self.allowed.append(plugin)

    def get_plugins(self, capabilities=None):
        plugins = []
        if capabilities == None:
            return [(pg, cs) for pg, cs in self.plugins.items()
                        if pg in self.allowed()]
        for plugin, pclass in self.plugins.items():
            for capability in pclass.__capabilities__:
                if capability in capabilities \
                and plugin in self.allowed:
                    plugins.append((plugin, pclass))
                    dbg('Matching plugin %s for capability %s' % (plugin, capability))
        return plugins

    def get_plugin_conf(self, plugin):
        if plugin + 'Config' in self.plugins:
            return self.plugins[plugin + 'Config']

    def is_enabled(self, plugin):
        return plugin in self.allowed

    def get_allowed(self):
        return self.allowed

    def get_disallowed(self):
        disallowed = []
        for plugin, pclass in self.plugins.items():
            if plugin not in self.allowed \
            and pclass.__capabilities__ != ['Config']:
                disallowed.append(plugin)
        return disallowed

    def get_available_plugins(self):
        return [pg for pg, cl
                    in self.plugins.items()
                    if ['Config'] == cl.__capabilities__]

    def get_info(self, plugin):
        if plugin in self.plugins.keys():
            return self.plugins[plugin].__plugin_info__

    def get_authors(self, plugin):
        if plugin in self.plugins.keys():
            return self.plugins[plugin].__authors__


## To make all the classes inherit from this one
class Plugin(gtk.VBox):
    def __init__(self):
        gtk.VBox.__init__(self)


class TabPlugin(Plugin):
    '''
    Generic Tab plugin that implements all the possible signals.
    The *command signals are used to interact mainly with the LocalCommandList
    plugin that handles the locally stored commands.
    The add_tab is used to add  anew terminal tab.
    '''
    __gsignals__ = {
         'run_command': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                             (str, str, str)),
         'cancel_command': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                             ()),
         'add_command': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                             (str, str, str)),
         'remove_command': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                             (str, str, str)),
         'edit_command': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                             (str, str, str)),
         'add_tab': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                             ()),
         'preferences': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                             ()),
         'show_man': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                             (str,)),
         'quit': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                             ()),
         }
    __capabilities__ = ['CommandTab']
    __title__ = ''
    __authors__ = ''
    __plugin_info__ = ''

    def reload(self):
        '''
        This method is called when a signal 'reload' is sent from it's
        configurator
        '''
        pass

    def get_command(self):
        '''
        This method is uset to retrieve a command, not sure if it's needed yet
        '''
        return None, None, None

    def filter(self, string):
        '''
        This function is used to filter the commandslist, usually by the
        search box
        '''
        pass


class PluginConfig(Plugin):
    '''
    Generic plugin configuration window, to be used in the preferences plugins
    tab
    '''
    __gsignals__ = {
        ## when emited, this signal forces the reload of it's associated plugin
        ## to reload the plugin config without having to restart the program
         'reload': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                             ())
         }
    __capabilities__ = ['Config']

    def __init__(self, config):
        Plugin.__init__(self)
        self.config = config

class URLPlugin(Plugin):
    '''
    Plugion that matches an url in the screen and executes some action.
    '''
    __capabilities__ = [ 'URL' ]


    def __init__(self, config):
        Plugin.__init__(self)
        self.config = config
        ## This is the regexp that will trigger the callback
        matches = ['']

    def callback(self, url, matchnum):
        ## When the regexp is found, this function will be called
        pass

    def open_url(self, url):
        """
        Open a given URL, generic for all the URL plugins to use
        """
        oldstyle = False
        if gtk.gtk_version < (2, 14, 0) or \
           not hasattr(gtk, 'show_uri') or \
           not hasattr(gtk.gdk, 'CURRENT_TIME'):
            oldstyle = True
        if not oldstyle:
            try:
                gtk.show_uri(None, url, gtk.gdk.CURRENT_TIME)
            except:
                oldstyle = True
        if oldstyle:
            dbg('Old gtk (%s,%s,%s), calling xdg-open' % gtk.gtk_version)
            try:
                subprocess.Popen(["xdg-open", url])
            except:
                dbg('xdg-open did not work, falling back to webbrowser.open')
                webbrowser.open(url)
