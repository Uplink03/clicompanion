#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# config.py - Configuration classes for the clicompanion
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
#
# This file has the CLIConfig class definition, and the CLIConfigView, the
# first is the main configuration model of the progran, where all the config
# is stored and processed to be correct, also sets up all the required
# configuration (default sections and keybindings) if they are not set.
#
# The CLIConfigViewer, is something similar to a view in MySQL, is an object
# that has the same (almos all) methods than the normal CLIConfig, but only
# shows a part of it, used to allow the plugins to handle their own
# configurations (a prefix will be added, like the 'profiles::' prefix or the
# name of the plugin that stores the config).


import os
import ConfigParser
import collections
import gtk
import pango
import clicompanionlib.utils as cc_utils
from clicompanionlib.utils import dbg

CONFIGDIR = os.path.expanduser("~/.config/clicompanion/")
CONFIGFILE = os.path.expanduser("~/.config/clicompanion/config")


## All the options (except keybindings) passed as name: (default, test), where
## test can be one of 'bool', 'str', 'encoding', 'font', or a function to test
## the value (the function must throw an exception on fail)
DEFAULTS = {'profile': {"scrollb": ('500', 'int'),
                         "color_scheme": ("Custom", 'str'),
                         "colorf": ('#FFFFFF', gtk.gdk.color_parse),
                         "colorb": ('#000000', gtk.gdk.color_parse),
                         "use_system_colors": ("False", 'bool'),
                         "encoding": ('UTF-8', 'encoding'),
                         "font": (cc_utils.get_system_font(), 'font'),
                         "use_system_font": ("False", 'bool'),
                         "use_system_colors": ("False", 'bool'),
                         "bold_text": ("False", 'bool'),
                         "antialias": ("True", 'bool'),
                         "sel_word": (u"-A-Za-z0-9,./?%&#:_", 'str'),
                         "update_login_records": ("True", 'bool'),
                        },
             'general': {"debug": ('False', 'bool'),
                         "plugins": ('LocalCommandList, CommandLineFU, StandardURLs', 'str')
                        },
             'LocalCommandList': {"cheatsheet":
                               (os.path.expanduser("~/.clicompanion2"), 'str'),
                        },
             }

## Note that the modifiers must be specified as 'mod1+mod2+key', where the
## modifiers are 'shift', 'alt','ctrl', in that order (shift+alt+ctrl+key), and
## that the key pressed is the key affecteed by the modifiers, for example,
## shift+ctrl+D (not shift+ctrl+d). And the function keys go uppercase (F10).
DEFAULT_KEY_BINDINGS = {
        'run_command': 'F4',
        'cancel_command': 'ctrl+C',
        'add_command': 'F5',
        'remove_command': 'F6',
        'edit_command': 'unused',
        'add_tab': 'F7',
        'close_tab': 'unused',
        'next_tab': 'unused',
        'previous_tab': 'unused',
        'move_tab_right': 'unused',
        'move_tab_left': 'unused',
        'toggle_fullscreen': 'F12',
        'toggle_maximize': 'F11',
        'toggle_hide_ui': 'F9',
        'copy': 'shift+ctrl+C',
        'paste': 'shift+ctrl+V',
        }

### funcname : labelname
## a function with the name funcname and signature void(void) must exist in the
## main window class, and is the one that will be called when the keybinding is
## actibated
KEY_BINDINGS = {
        'run_command': 'Run command',
        'cancel_command': 'Cancel command',
        'add_command': 'Add command',
        'remove_command': 'Remove command',
        'edit_command': 'Edit command',
        'add_tab': 'Add tab',
        'close_tab': 'Close tab',
        'next_tab': 'Go to the next tab',
        'previous_tab': 'Go to the previous tab',
        'move_tab_right': 'Move the focused tab to the right',
        'move_tab_left': 'Move the focused tab to the left',
        'toggle_fullscreen': 'Toggle fullscreen',
        'toggle_maximize': 'Maximize',
        'toggle_hide_ui': 'Hide UI',
        'copy': 'Copy the selected text',
        'paste': 'Paste the text in the terminal',
        }


class CLIConfig(ConfigParser.RawConfigParser):
    def __init__(self, defaults=DEFAULTS, conffile=CONFIGFILE):
        ConfigParser.RawConfigParser.__init__(self)
        self.conffile = os.path.abspath(conffile)
        configdir = self.conffile.rsplit(os.sep, 1)[0]
        if not os.path.exists(configdir):
            try:
                os.makedirs(configdir)
            except Exception, e:
                print _('Unable to create config at dir %s (%s)') \
                        % (configdir, e)
                return False
        # set a number of default parameters, and fill the missing ones
        if os.path.isfile(self.conffile):
            self.read([self.conffile])
            print _("INFO: Reading config file at %s.") % self.conffile
        else:
            print _("INFO: Creating config file at %s.") % self.conffile

        for section in DEFAULTS.keys():
            fullsection = section + '::default'
            ## Set default profile options
            if fullsection not in self.sections():
                self.add_section(fullsection)
                for option, optdesc in DEFAULTS[section].items():
                    value, test = optdesc
                    self.set(fullsection, option, value)
        ## Set default keybindings
        if 'keybindings' not in self.sections():
            self.add_section("keybindings")
        for option, value in DEFAULT_KEY_BINDINGS.items():
            if not self.has_option('keybindings', option):
                self.set('keybindings', option, value)
        self.parse()
        # Writing our configuration file
        self.save()

    def parse(self):
        ## clean the default options to avoid seeing options where they are not
        for option in self.defaults().keys():
            self.remove_option('DEFAULT', option)
        ## now parse the rest of sections
        for section in self.sections():
            for option in self.options(section):
                if section == 'keybindings':
                    if option not in KEY_BINDINGS.keys():
                        print _("Option %s:%s not recognised, deleting." \
                                % (section, option))
                        self.remove_option(section, option)
                else:
                    if not '::' in section:
                        print _("Deleting unrecognzed section %s." % section)
                        self.remove_section(section)
                        break
                    secttype = section.split('::')[0]
                    if secttype not in DEFAULTS:
                        print _("Deleting unrecognized section %s." % section)
                        self.remove_section(section)
                        break
                    if option not in DEFAULTS[secttype].keys():
                        print _("Option %s:%s not recognised, deleting." \
                                % (section, option))
                        self.remove_option(section, option)
                    else:
                        val = self.get(section, option)
                        defval, test = DEFAULTS[secttype][option]
                        try:
                            if test == 'str':
                                continue
                            elif test == 'int':
                                res = self.getint(section, option)
                            elif test == 'bool':
                                res = self.getboolean(section, option)
                            elif test == 'encoding':
                                if val.lower() not in [enc.lower()
                                                       for enc, desc
                                                       in cc_utils.encodings]:
                                    raise ValueError(
                                        _('Option %s is not valid.') % test)
                            elif test == 'font':
                                fname, fsize = val.rsplit(' ', 1)
                                fsize = int(fsize)
                                cont = gtk.TextView().create_pango_context()
                                avail_fonts = cont.list_families()
                                found = False
                                for font in avail_fonts:
                                    if fname == font.get_name():
                                        found = True
                                        break
                                if not found:
                                    raise ValueError(
                                        _('Option %s is not valid.') % type)
                            elif callable(test):
                                res = test(val)
                                if not res:
                                    raise Exception
                            else:
                                        print _("Wrong specification for "
                                            "option %s in file %s") \
                                            % (option, __file__)
                        except Exception, e:
                            print (_('ERROR: Wrong config value for %s: %s ') \
                                    % (option, val) +
                                    _(',using default one %s.') % defval)
                            self.set(section, option, defval)

    def set(self, section, option, value):
        if section == 'DEFAULT':
            raise ConfigParser.NoSectionError(
                'Section "DEFAULT" is not allowed. Use section '
                    '"TYPE::default instead"')
        else:
            return ConfigParser.RawConfigParser.set(self, section,
                                                    option, value)

    def get(self, section, option):
        if '::' in section:
            sectiontag = section.split('::')[0]
            if not self.has_option(section, option):
                if not self.has_option(sectiontag + '::default', option):
                    raise ConfigParser.NoOptionError(option, section)
                return ConfigParser.RawConfigParser.get(self,
                            sectiontag + '::default', option)
        elif not self.has_option(section, option):
            raise ConfigParser.NoOptionError(option, section)
        return ConfigParser.RawConfigParser.get(self, section, option)

    def get_config_copy(self):
        new_cfg = CLIConfig(DEFAULTS)
        for section in self.sections():
            if section not in new_cfg.sections():
                new_cfg.add_section(section)
            for option in self.options(section):
                new_cfg.set(section, option, self.get(section, option))
        return new_cfg

    def save(self, conffile=None):
        if not conffile:
            conffile = self.conffile
        dbg('Saving conffile at %s' % conffile)
        with open(conffile, 'wb') as f:
            self.write(f)

    def get_plugin_conf(self, plugin):
        return CLIConfigView(plugin, self)


class CLIConfigView():
    '''
    This class implements an editable view (hiding unwanted options) of the
    CLIConfig class, for example, to avoid the plugins editing other options
    but their own, some methods of the configRaw Parser are not implemented.
    '''
    def __init__(self, sectionkey, config):
        self.key = sectionkey + '::'
        self._config = config

    def get(self, section, option):
        if section == 'DEFAULT':
            section = 'default'
        if self.key + section not in self._config.sections():
            raise ConfigParser.NoSectionError(
                'The section %s does not exist.' % section)
        return self._config.get(self.key + section, option)

    def getint(self, section, option):
        return self._config.getint(self.key + section, option)

    def getfloat(self, section, option):
        return self._config.getfloat(self.key + section, option)

    def getboolean(self, section, option):
        return self._config.getboolean(self.key + section, option)

    def items(self, section):
        return self._config.items(self.key + section)

    def write(self, fileobject):
        pass

    def remove_option(self, section, option):
        return self._config.remove_option(self.key + section, option)

    def optionxform(self, option):
        pass

    def set(self, section, option, value):
        if section == 'DEFAULT':
            section = 'default'
        if self.key + section not in self._config.sections():
            raise ConfigParser.NoSectionError(
                'The section %s does not exist.' % section)
        return self._config.set(self.key + section, option, value)

    def add_section(self, section):
        return self._config.add_section(self.key + section)

    def remove_section(self, section):
        return self._config.remove_section(self.key + section)

    def sections(self):
        sections = []
        for section in self._config.sections():
            if section.startswith(self.key):
                sections.append(section.split('::', 1)[1])
        return sections

    def options(self, section):
        return self._config.options(self.key + section)

    def defaults(self):
        return self._config.options(self.key + 'default')

    def has_section(self, section):
        return self._config.has_section(self.key + section)

    def has_option(self, section, option):
        return self._config.has_option(self.key + section, option)

    def readfp(self, filedesc, name='<???>'):
        tempconf = ConfigParser.RawConfigParser()
        tempconf.readfp(filedesc, name)
        for option in tempconf.defaults():
            self.set('DEFAULT', option, tempconf.get('DEFAULT', option))
        for section in tempconf.sections():
            if not self.has_section(section):
                self.add_section(section)
            for option in tempconf.options():
                self.set(section, option)

    def read(self, files):
        for file in files:
            with open(file, 'r') as fd:
                self.readfp(fd)

    def save(self):
        self._config.save()
