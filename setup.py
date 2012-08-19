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

import sys
import glob
from distutils.core import setup
import platform
import shutil
try:
    from DistUtilsExtra.command import *
except ImportError:
    print "This program needs python's DistUtilsExtra module to run, see https://launchpad.net/python-distutils-extra"
    sys.exit(1)

distribution = platform.linux_distribution()
if distribution[0] == 'Ubuntu':
    shutil.copy2('data/clicompanion2.config.ubuntu', 'data/clicompanion2.config')
elif distribution[0] == 'debian':
    shutil.copy2('data/clicompanion2.config.debian', 'data/clicompanion2.config')

setup(  name='clicompanion',
        version='1.1',
        description='Run Terminal commands from a GUI. Store commands for later use.',
        author='Duane Hinnen',
        author_email='duanedesign@gmail.com',
        scripts=['clicompanion'],
        packages=['clicompanionlib', 'plugins'],
        data_files=[('/etc/clicompanion.d/', ['data/clicompanion2.config']),
            ('/etc/clicompanion.d/', ['data/clicompanion2.config.debian']),
            ('/etc/clicompanion.d/', ['data/clicompanion2.config.ubuntu']),
            ('/usr/share/pixmaps', ['data/clicompanion.16.png']),
            ('/usr/share/applications', ['data/clicompanion.desktop']),
            ('/usr/share/clicompanion/locale/', glob.glob('locale/*/LC_MESSAGES/*.mo')),
            ],
         
        cmdclass={ 'build'       : build_extra.build_extra,
                    'build_i18n' :  build_i18n.build_i18n,
		         },  
        )
