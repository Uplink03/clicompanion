#!/usr/bin/env python
#
# Copyright 2010 Duane Hinnen
#
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

import glob
from distutils.core import setup
from DistUtilsExtra.command import *



setup(  name='clicompanion',
        version='0.1.0',
        description='Run Terminal commands from a GUI. Store commands for later use.',
        author='Duane Hinnen',
        author_email='duanedesign@gmail.com',
        scripts=['clicompanion'],
        packages=['clicompanionlib'],
        data_files=[('/etc/clicompanion.d/', ['data/clicompanion2.config']),
        ('/usr/share/pixmaps', ['data/clicompanion.16.png']),
        ('/usr/share/applications', ['data/clicompanion.desktop']),
        ('share/clicompanion/locale/', glob.glob('locale/*/LC_MESSAGES/*.mo')),
         ],
         
        cmdclass = { 'build'       : build_extra.build_extra,
                     'build_i18n' :  build_i18n.build_i18n,
        },  
        )
