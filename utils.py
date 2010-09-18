# -*- mode: python; coding: utf-8; -*-
#
# clicompanion.py - commandline tool.
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

"""
A collection of useful functions.
"""

import getpass


def get_user_shell():
    """Get the user's shell defined in /etc/passwd ."""
    data = None
    try:
        # Read out the data in /etc/passwd
        with open('/etc/passwd') as f:
            data = f.readlines()
    except e:
        print "Something unexpected happened!"
        raise e

    for i in data:
        tmp = i.split(":")
        # Check for the entry of the currently logged in user
        if tmp[0] == getpass.getuser(): 
            # Columns are separated by colons, so split each column.
            # Sample /etc/passwd entry for a user:
            # 
            #  jorge:x:1001:1002:,,,:/home/jorge:/bin/bash
            #
            # The last column is relevant for us.
            # Don't forget to strip the newline at the end of the string!
            return i.split(":")[-1:][0].strip('\n')
