#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# LocalCommandList.py - Plugin for handling locally stored commands
#
# Copyright 2010 Duane Hinnen, Kenny Meyer, David Caro
#                                               <david.caro.estevez@gmail.com>
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


import os
import pygtk
pygtk.require('2.0')
import gobject
import collections
import platform
import shutil

try:
    import gtk
except:
    ## do not use gtk, just print
    print _("You need to install the python gtk bindings package"
             "'python-gtk2'")
    sys.exit(1)

## we should try to absolutely detach it from the clicompanion libs someday
from clicompanionlib.utils import dbg
import clicompanionlib.plugins as plugins

CONFIG_ORIG = "/etc/clicompanion.d/clicompanion2.config"

## Targets for the Drag and Drop
TARGETS = [
    ('MY_TREE_MODEL_ROW', gtk.TARGET_SAME_WIDGET, 0),
    ('text/plain', 0, 1),
    ('TEXT', 0, 2),
    ('STRING', 0, 3),
    ]


class LocalCommandList(plugins.TabPlugin):
    '''
    Tab with the list of local stored commands, the only signals that should
    get emited (right now) are the run_command and show_man. The other can be
    processed inhouse
    '''
    __authors__ = ('Duane Hinnen\n'
                   'Kenny Meyer\n'
                   'Marcos Vanettai\n'
                   'Marek Bardoński\n'
                   'David Caro <david.caro.estevez@gmail.com>\n')
    __info__ = ('This is the main plugin for the CLI Companion, the one that '
                'handles the locally stored commands.')
    __title__ = 'Local Commands'

    def __init__(self, config):
        self.config = config
        plugins.TabPlugin.__init__(self)
        self.treeview = gtk.TreeView()
        self.filtering = False
        ## command, user input, description, and index in cmnds array
        self.liststore = gtk.ListStore(str, str, str, int)
        ## Load the given commands file
        self.cmnds = Cheatsheet(
                self.config.get('default', 'cheatsheet'))
        ## will hold the commands. Actually the first three columns
        ## note that this commands list will not change with searchers nor
        ## filters, instead, when adding a command to the liststore, we will
        ## add also the index of the command in the cmnds array as another
        ## field
        self.sync_cmnds(rld=True)
        self.treeview.set_model(DummySort(self.liststore))

        ### Only show the three firs columns
        ## create the TreeViewColumns to display the data
        self.add_text_col('Command', 0)
        self.add_text_col('User Input', 1)
        self.add_text_col('Description', 2)
        self.treeview.set_tooltip_column(2)
        self.treeview.set_reorderable(True)

        ## open with top command selected
        selection = self.treeview.get_selection()
        selection.select_path(0)
        selection.set_mode(gtk.SELECTION_SINGLE)
        ### double-click
        self.treeview.connect("row-activated", self.event_clicked)
        ##press enter to run command
        self.treeview.connect("key-press-event",
                lambda wg, event: self.event_key_pressed(event))
        ## Right click event
        self.treeview.connect("button_press_event", self.right_click)
        # Allow enable drag and drop of rows including row move
        self.treeview.enable_model_drag_source( gtk.gdk.BUTTON1_MASK,
                                                TARGETS,
                                                gtk.gdk.ACTION_DEFAULT |
                                                gtk.gdk.ACTION_COPY)
        self.treeview.enable_model_drag_dest(TARGETS,
                                                gtk.gdk.ACTION_DEFAULT)

        self.treeview.connect ("drag_data_get", self.drag_data_get_event)
        self.treeview.connect ("drag_data_received",
                self.drag_data_received_event)
        self.treeview.connect("drag_drop", self.on_drag_drop )


        sw = gtk.ScrolledWindow()
        sw.add(self.treeview)
        self.pack_start(sw)
        self.show_all()

    def add_text_col(self, colname, n=0):
        col = gtk.TreeViewColumn()
        col.set_title(_(colname))
        render = gtk.CellRendererText()
        col.pack_start(render, expand=True)
        col.add_attribute(render, 'text', n)
        col.set_resizable(True)
        col.set_sort_column_id(n)
        col.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        col.set_min_width(20)
        col.set_fixed_width(230)
        self.treeview.append_column(col)

    def sync_cmnds(self, rld=False, filt_str=None):
        dbg('syncing commands')
        if rld:
            ## reload the commands list from the file
            self.cmnds.load()
        self.liststore.clear()
        ## Store also the index of the command in the CMNDS list
        i = 0
        for cmd, ui, desc in self.cmnds:
            if filt_str and filt_str in cmd + ui + desc or not filt_str:
                self.liststore.append((cmd, ui, desc, i - 1))
            i = i + 1
        self.cmnds.save()

    def get_command(self, path=None):
        if not path:
            selection = self.treeview.get_selection()
            model, iterator = selection.get_selected()
            if not iterator:
                return None, None, None
            path = model.get_path(iterator)
        lst_index = int(path[0])  # removes everything but number from [5,]
        model = self.treeview.get_model()
        cmd = ''.join(model[lst_index][0])
        ui = ''.join(model[lst_index][1])
        desc = ''.join(model[lst_index][2])
        return cmd, ui, desc

    def add_command(self, cmd='', ui='', desc=''):
        add_cmd_win = AddCommandWindow(cmd, ui, desc)
        new_cmd = add_cmd_win.run()
        if not new_cmd:
            return
        self.cmnds.append(*new_cmd)
        self.sync_cmnds()

    def edit_command(self, cmd='', ui='', desc=''):
        if not cmd:
            cmd, ui, desc = self.get_command()
        if cmd == None:
            return
        edit_cmd_win = EditCommandWindow(cmd, ui, desc)
        edited_cmd = edit_cmd_win.run()
        if not edited_cmd:
            return
        index = self.cmnds.index(cmd, ui, desc)
        del self.cmnds[index]
        self.cmnds.insert(*edited_cmd, pos=index)
        self.sync_cmnds()

    def remove_command(self, cmd=None, ui=None, desc=None):
        if not cmd:
            cmd, ui, desc = self.get_command()
        if cmd == None:
            return
        remove_command_win = RemoveCommandWindow()
        removed = remove_command_win.run()
        if not removed:
            return
        self.cmnds.del_by_value(cmd, ui, desc)
        self.sync_cmnds()

    def event_clicked(self, widget, path, column):
        ## double click to run a command
        cmd, ui, desc = self.get_command(path)
        if cmd:
            self.emit('run_command', cmd, ui, desc)

    def event_key_pressed(self, event):
        ## press enter to run a command
        keyname = gtk.gdk.keyval_name(event.keyval)
        dbg('Key %s pressed' % keyname)
        if event.type == gtk.gdk.KEY_PRESS:
            if keyname == 'Return':
                cmd, ui, desc = self.get_command()
                if cmd:
                    self.emit('run_command', cmd, ui, desc)
            if keyname == 'Delete' or keyname == 'BackSpace':
                self.remove_command()

    def filter(self, search_term):
        """
        Show commands matching a given search term.
        The user should enter a term in the search box and the treeview should
        only display the rows which contain the search term.
        No reordering allowed when filtering.
        """
        ## If the search term is empty, and we change filtering state
        ## restore the liststore, else do nothing
        if search_term == "":
            if self.filtering:
                dbg("Uniltering...")
                self.filtering = False
                self.treeview.set_model(DummySort(self.liststore))
            return
        dbg("Filtering...")
        self.filtering = True
        ## Create a TreeModelFilter object which provides auxiliary functions
        ## for filtering data.
## http://www.pygtk.org/pygtk2tutorial/sec-TreeModelSortAndTreeModelFilter.html
        modelfilter = self.liststore.filter_new()

        def search(model, iter, search_term):
            ## Iterate through every column and row and check if the search
            ## term is there:
            cmd, ui, desc = model.get(iter, 0, 1, 2)
            if search_term in ('%s %s %s' % (cmd, ui, desc)).lower():
                    return True
        modelfilter.set_visible_func(search, search_term)
        self.treeview.set_model(DummySort(modelfilter))

    #right-click popup menu for the Liststore(command list)
    def right_click(self, widget, event):
        if event.button == 3:
            x = int(event.x)
            y = int(event.y)
            time = event.time
            row = self.treeview.get_path_at_pos(x, y)
            if row:
                path, col, x, y = row
            popupMenu = gtk.Menu()
            if row:
                self.treeview.grab_focus()
                self.treeview.set_cursor(path, col, 0)
                command = self.get_command(path)
                if command[0] == None:
                    return
                # right-click popup menu Apply(run)
                menuPopup1 = gtk.ImageMenuItem(gtk.STOCK_APPLY)
                popupMenu.add(menuPopup1)
                menuPopup1.connect("activate",
                    lambda *x: self.emit('run_command', *command))
                # right-click popup menu Edit
                menuPopup2 = gtk.ImageMenuItem(gtk.STOCK_EDIT)
                popupMenu.add(menuPopup2)
                menuPopup2.connect("activate",
                    lambda *x: self.edit_command(*command))
                # right-click popup menu Delete
                menuPopup3 = gtk.ImageMenuItem(gtk.STOCK_DELETE)
                popupMenu.add(menuPopup3)
                menuPopup3.connect("activate",
                    lambda *x: self.remove_command(*command))
                # right-click popup menu Help
                menuPopup4 = gtk.ImageMenuItem(gtk.STOCK_HELP)
                popupMenu.add(menuPopup4)
                menuPopup4.connect("activate",
                    lambda wg, cmd: self.emit('show_man', cmd), command[0])
            # right-click popup menu Help
            menuPopup4 = gtk.ImageMenuItem(gtk.STOCK_ADD)
            popupMenu.add(menuPopup4)
            menuPopup4.connect("activate",
                lambda *x: self.add_command())
            # right-click popup menu Load file
            menuPopup4 = gtk.ImageMenuItem(gtk.STOCK_OPEN)
            box = menuPopup4.get_children()[0]
            box.set_label(_('Load another cheatsheet'))
            popupMenu.add(menuPopup4)
            menuPopup4.connect("activate",
                lambda *x: self.load_file())
            # Show popup menu
            popupMenu.show_all()
            popupMenu.popup(None, None, None, event.button, time)
            return True

    def load_file(self):
        chooser = CHFileSelector()
        resp = chooser.run()
        if resp:
            self.config.set('default', 'cheatsheet', resp)
            self.reload()

    def reload(self, config=None):
        if config:
            self.config = config
        self.cmnds = Cheatsheet(
                self.config.get('default', 'cheatsheet'))
        self.sync_cmnds()
        self.config.save()

    def on_drag_drop(self, treeview, context, x, y, time):
        '''
        Stop the signal when in search mode
        '''
        if self.filtering:
            treeview.stop_emission('drag_drop')

    def drag_data_get_event(self, treeview, context, selection, target_id,
                            etime):
        """
        Executed on dragging
        """
        treeselection = treeview.get_selection()
        model, iter = treeselection.get_selected()
        data = model.get(iter, 0, 1, 2)
        selection.set(selection.target, 8, '\t'.join(data))

    def drag_data_received_event(self, treeview, context, x, y, selection,
                                info, time):
        """
        Executed when dropping.
        """
        ## if we are in a search, do nothing
        if self.filtering:
            return
        model = treeview.get_model()
        ## get the destination
        drop_info = treeview.get_dest_row_at_pos(x, y)
        if drop_info:
            path, position = drop_info
            iter = model.get_iter(path)
            dest = list(model.get(iter, 0, 1, 2))

        ## parse all the incoming commands
        for data in selection.data.split('\n'):
            # if we got an empty line skip it
            if not data.replace('\r', ''):
                continue
            # format the incoming string
            orig = data.replace('\r', '').split('\t', 2)
            orig = [fld.strip() for fld in orig]
            # fill the empty fields
            if len(orig) < 3:
                orig = list(orig) + ['', ] * (3 - len(orig))
            dbg('Got drop of command %s' % '_\t_'.join(orig))

            if drop_info:
                if (position == gtk.TREE_VIEW_DROP_BEFORE
                        or position == gtk.TREE_VIEW_DROP_INTO_OR_BEFORE):
                    dbg('\t to before dest %s' % '_\t_'.join(dest))
                    self.cmnds.drag_n_drop(orig, dest, before=True)
                else:
                    dbg('\t to after dest %s' % '_\t_'.join(dest))
                    self.cmnds.drag_n_drop(orig, dest, before=False)
            else:
                dbg('\t to the end')
                self.cmnds[len(self.cmnds)] = orig
        context.finish(True, True, time)
        self.sync_cmnds()

    def main(self):
        try:
            gtk.main()
        except KeyboardInterrupt:
            pass


## The name of the config widget must be the same, but ended with 'Config'
class LocalCommandListConfig(plugins.PluginConfig):
    '''
    Config tab for the plugin, just select the cheatsheet file.
    '''
    def __init__(self, config):
        plugins.PluginConfig.__init__(self, config)
        self.draw_all()

    def draw_all(self):
        hbox = gtk.HBox()
        hbox.pack_start(gtk.Label('Cheatsheet file:'))
        self.file_btn = gtk.Button(
                            self.config.get('default', 'cheatsheet'))
        self.file_btn.connect('clicked', self.select_file)
        hbox.pack_end(self.file_btn, False, False, 8)
        self.pack_start(hbox, False, False, 8)
        hbox2 = gtk.HBox()
        hbox3 = gtk.HBox()
        self.file_btn2 = gtk.Button("Revert cheatsheet to clean Ubuntu version")
        self.file_btn3 = gtk.Button("Revert cheatsheet to clean Debian version")
        self.file_btn2.connect('clicked', self.revert_cheatsheet_to_ubuntu_version)
        self.file_btn3.connect('clicked', self.revert_cheatsheet_to_debian_version)
        hbox2.pack_start(self.file_btn2)
        hbox3.pack_start(self.file_btn3)
        self.pack_start(hbox2, False, False, 8)
        self.pack_start(hbox3, False, False, 8)
        
    def select_file(self, btn):
        chooser = CHFileSelector()
        resp = chooser.run()
        if resp:
            self.config.set('default', 'cheatsheet', newfile)
            ## notify that the plugin must be reloaded
            self.emit('reload')
        self.update()

    def update(self):
        for child in self.children():
            self.remove(child)
        self.draw_all()
        self.show_all()
        
    def revert_cheatsheet_to_ubuntu_version(self, btn):
        distribution = platform.linux_distribution()
        if distribution[0] == 'debian':
            self.show_warning()    
        shutil.copy2('/etc/clicompanion.d/clicompanion2.config.ubuntu', os.path.expanduser('~') + '/.clicompanion2')
        self.emit('reload')
        self.show_information()
         
    def revert_cheatsheet_to_debian_version(self, btn):
        distribution = platform.linux_distribution()
        if distribution[0] == 'Ubuntu':
            self.show_warning()    
        shutil.copy2('/etc/clicompanion.d/clicompanion2.config.debian', os.path.expanduser('~') + '/.clicompanion2')
        self.emit('reload')
        self.show_information()

    def show_warning(self):
        dlg = gtk.MessageDialog(
                     None,
                     gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                     gtk.MESSAGE_ERROR,
                     gtk.BUTTONS_CLOSE,
                     message_format=_('Warning!'))
        dlg.format_secondary_text(_('You are changing cheatsheet to version for another distribution'))
        dlg.run()
        dlg.destroy()
        
    def show_information(self):
        dlg = gtk.MessageDialog(
                     None,
                     gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                     gtk.MESSAGE_INFO,
                     gtk.BUTTONS_CLOSE,
                     message_format=_('Information'))
        dlg.format_secondary_text(_('Cheatsheet was changed.'))
        dlg.run()
        dlg.destroy()

class CHFileSelector(gtk.FileChooserDialog):
    '''
    Popup for selecting the cheatsheet file
    '''
    def __init__(self, current_file='~'):
        gtk.FileChooserDialog.__init__(self,
            'Select cheatsheet file',
            None,
            gtk.FILE_CHOOSER_ACTION_OPEN,
            (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
            gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        filter = gtk.FileFilter()
        filter.set_name("All files")
        filter.add_pattern("*")
        self.add_filter(filter)
        filter = gtk.FileFilter()
        filter.set_name("Cheatsheets")
        filter.add_pattern("*cheatsheet")
        filter.add_pattern("*clicompanion*")
        filter.add_pattern("*.cs")
        self.add_filter(filter)
        self.set_uri(current_file)

    def run(self):
        newfile = None
        resp = gtk.FileChooserDialog.run(self)
        if resp == gtk.RESPONSE_OK:
            newfile = self.get_filename()
        self.destroy()
        return newfile


class DummySort(gtk.TreeModelSort, gtk.TreeDragDest):
    '''
    This class is needed to implement the drag and drop in a TreeModelSort
    '''
    __gtype_name__ = 'DummySort'

    def __init__(self, *x):
        gtk.TreeModelSort.__init__(self, *x)


class Cheatsheet:
    '''
    Container class for the cheatsheet of commands

    Example of usage:
    >>> c = config.Cheatsheet()
    >>> c.load('/home/myuser/.clicompanion2')
    >>> c[3]
    ['uname -a', '', 'What kernel am I running\n']
    >>> c.file
    '/home/cascara/.clicompanion2'
    >>> c[2]=[ 'mycmd', 'userui', 'desc' ]
    >>> c[2]
    ['mycmd', 'userui', 'desc']
    >>> del c[2]
    >>> c[2]
    ['ps aux | grep ?', 'search string',
        'Search active processes for search string\n']
    >>> c.insert('cmd2','ui2','desc2',2)
    >>> c[2]
    ['cmd2', 'ui2', 'desc2']

    '''
    def __init__(self, cheatsheet):
        self.cheatsheet = cheatsheet
        self.commands = []
        self.load()

    def __repr__(self):
        return 'Config: %s - %s' % (self.cheatsheet, self.commands)

    def load(self):
        if not os.path.exists(self.cheatsheet):
            if os.path.exists(CONFIG_ORIG):
                os.system("cp %s %s" % (CONFIG_ORIG, self.cheatsheet))
            else:
                # Oops! Looks like there's no default cheatsheet.
                # Then, create an empty cheatsheet.
                open(self.cheatsheet, 'w').close()
        try:
            dbg('Reading cheatsheet from file %s' % self.cheatsheet)
            with open(self.cheatsheet, 'r') as ch_fd:
                ## try to detect if the line is a old fashines config line
                ## (separated by ':'), when saved will rewrite it
                no_tabs = True
                some_colon = False
                for line in ch_fd:
                    line = line.strip()
                    if not line:
                        continue
                    cmd, ui, desc = [l.strip()
                                    for l in line.split('\t', 2)] + ['', ] * \
                                        (3 - len(line.split('\t', 2)))
                    if ':' in cmd:
                        some_colon = True
                    if ui or desc:
                        no_tabs = False
                    if cmd and [cmd, ui, desc] not in self.commands:
                        self.commands.append([cmd, ui, desc])
                        dbg('Adding command %s' % [cmd, ui, desc])
                if no_tabs and some_colon:
                    ## None of the commands had tabs, and all had ':' in the
                    ## cmd... most probably old config style
                    print _("Detected old cheatsheet style at") \
                            + " %s" % self.cheatsheet \
                            + _(", parsing to new one.")
                    for i in range(len(self.commands)):
                        cmd, ui, desc = self.commands[i]
                        cmd, ui, desc = [l.strip()
                                        for l in cmd.split(':', 2)] + ['', ] \
                                            * (3 - len(cmd.split(':', 2)))
                        self.commands[i] = [cmd, ui, desc]
                    self.save()
        except IOError, e:
            print _("Error while loading cheatfile") + \
                    " %s: %s" % (self.cheatsheet, e)

    def save(self, cheatfile=None):
        '''
        Saves the current config to the file cheatfile, or the file that was
        loaded.
        NOTE: It does not overwrite the value self.cheatsheet, that points to
        the file that was loaded
        '''
        if not cheatfile and self.cheatsheet:
            cheatfile = self.cheatsheet
        elif not cheatfile:
            return False
        try:
            with open(cheatfile, 'wb') as ch_fd:
                for command in self.commands:
                    ch_fd.write('\t'.join(command) + '\n')
        except IOError, e:
            print _("Error writing cheatfile") + " %s: %s" % (cheatfile, e)
            return False
        return True

    def __len__(self):
        return len(self.commands)

    def __getitem__(self, key):
        return self.commands[key]

    def __setitem__(self, key, value):
        if not isinstance(value, collections.Iterable) or len(value) < 3:
            raise ValueError('Value must be a container with three items, '
                            'but got %s' % value)
        if key < len(self.commands):
            self.commands[key] = list(value)
        else:
            try:
                self.insert(*value, pos=key)
            except ValueError, e:
                raise ValueError('Value must be a container with three items, '
                                'but got %s' % value)

    def __iter__(self):
        for command in self.commands:
            yield command

    def insert(self, cmd, ui, desc, pos=None):
        if not [cmd, ui, desc] in self.commands:
            if not pos:
                self.commands.append([cmd, ui, desc])
            else:
                self.commands.insert(pos, [cmd, ui, desc])

    def append(self, cmd, ui, desc):
        self.insert(cmd, ui, desc)

    def index(self, cmd, ui, desc):
        return self.commands.index([cmd, ui, desc])

    def __delitem__(self, key):
        del self.commands[key]

    def pop(self, key):
        return self.commands.pop(key)

    def del_by_value(self, cmd, ui, desc):
        if [cmd, ui, desc] in self.commands:
            return self.commands.pop(self.commands.index([cmd, ui, desc]))

    def drag_n_drop(self, cmd1, cmd2, before=True):
        if cmd1 in self.commands:
            dbg('Dropping command from inside %s' % '_\t_'.join(cmd1))
            i1 = self.commands.index(cmd1)
            del self.commands[i1]
            if cmd2:
                i2 = self.commands.index(cmd2)
                if before:
                    self.commands.insert(i2, cmd1)
                else:
                    self.commands.insert(i2 + 1, cmd1)
            else:
                self.commands.append(cmd1)
        else:
            dbg('Dropping command from outside %s' % '_\t_'.join(cmd1))
            if cmd2:
                i2 = self.commands.index(cmd2)
                if before:
                    self.commands.insert(i2, cmd1)
                else:
                    self.commands.insert(i2 + 1, cmd1)
            else:
                self.commands.append(cmd1)


class RemoveCommandWindow(gtk.MessageDialog):
    def __init__(self):
        gtk.MessageDialog.__init__(self,
            None,
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            gtk.MESSAGE_WARNING,
            gtk.BUTTONS_YES_NO,
            None)

        self.set_markup(_("Are you sure you want to delete this command?"))

    def run(self):
        result = gtk.MessageDialog.run(self)
        self.destroy()
        if result == gtk.RESPONSE_YES:
            return True
        return False


## Add command dialog box
class AddCommandWindow(gtk.MessageDialog):
    def __init__(self, cmd='', ui='', desc=''):
        ## Create Dialog object
        gtk.MessageDialog.__init__(self,
            None,
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            gtk.MESSAGE_QUESTION,
            gtk.BUTTONS_OK,
            None)

        ## primaary text
        self.set_markup(_("Add a command to your command list"))

        #create the text input field
        self.cmd_txt = gtk.Entry()
        self.cmd_txt.set_text(cmd)
        self.ui_txt = gtk.Entry()
        self.ui_txt.set_text(ui)
        self.desc_txt = gtk.Entry()
        self.desc_txt.set_text(desc)
        ## allow the user to press enter to do ok
        self.cmd_txt.connect("activate",
                lambda *x: self.response(gtk.RESPONSE_OK))
        self.ui_txt.connect("activate",
                lambda *x: self.response(gtk.RESPONSE_OK))
        self.desc_txt.connect("activate",
                lambda *x: self.response(gtk.RESPONSE_OK))

        ## create three labels
        hbox1 = gtk.HBox()
        hbox1.pack_start(gtk.Label(_("Command")), False, 5, 5)
        hbox1.pack_start(self.cmd_txt, False, 5, 5)

        hbox1.pack_start(gtk.Label(_("User Input")), False, 5, 5)
        hbox1.pack_start(self.ui_txt, False, 5, 5)

        hbox2 = gtk.HBox()
        hbox2.pack_start(gtk.Label(_("Description")), False, 5, 5)
        hbox2.pack_start(self.desc_txt, True, 5, 5)

        ## cancel button
        self.add_button(_('Cancel'), gtk.RESPONSE_DELETE_EVENT)
        ## some secondary text
        self.format_secondary_markup(
            _("When entering a command use question marks(?) as placeholders "
          "if user input is required when the command runs. Example: ls "
          "/any/directory would be entered as, ls ? .For each question "
          "mark(?) in your command, if any, use the User Input field to "
          "provide a hint for each variable. Using our example ls ? you "
          "could put directory as the User Input. Lastly provide a brief "
          "Description."))

        ## add it and show it
        self.vbox.pack_end(hbox2, True, True, 0)
        self.vbox.pack_end(hbox1, True, True, 0)
        self.show_all()

    def run(self):
        result = None
        command = None
        while not result:
            ## Show the dialog
            result = gtk.MessageDialog.run(self)
            if result == gtk.RESPONSE_OK:
                ## user text assigned to a variable
                cmd = self.cmd_txt.get_text()
                ui = self.ui_txt.get_text()
                desc = self.desc_txt.get_text()
                if cmd:
                    command = cmd, ui, desc
                else:
                    self.show_nocmd_error()
                    result = None
        self.destroy()
        return command

    def show_nocmd_error(self):
        error = gtk.MessageDialog(None, gtk.DIALOG_MODAL, \
            gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
            _("You need to enter at least a command."))
        error.connect('response', lambda err, *x: err.destroy())
        error.run()

class EditCommandWindow(AddCommandWindow):
    """
    Reuse the add window changing the name
    """
    def __init__(self, cmd, ui, desc):
        if not cmd:
            cc_helpers.choose_row_error()
            return
        AddCommandWindow.__init__(self, cmd, ui, desc)
        self.set_markup(_("Edit a command in your command list"))
