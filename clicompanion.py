#! /usr/bin/env python

import locale
import gettext
import os

from clicompanionlib.view import run


BASEDIR = '/usr/share/clicompanion/'

def get_language():
    """Return the language to be used by the system.

    If it finds the system language in the translated files, it
    returns it, otherwise it just returns None.
    """
    loc = locale.setlocale(locale.LC_ALL, "")
    loc = loc[:2]
    traducidos = os.listdir(locale_dir)
    if loc in traducidos:
        return loc
    return

locale_dir = os.path.join(BASEDIR, "locale")
gettext.install('clicompanion', locale_dir, unicode=True)
idioma = get_language()
if idioma is not None:
    mo = os.path.join(locale_dir, '%s/LC_MESSAGES/clicompanion.mo' % idioma)
    if not os.access(mo, os.F_OK):
        raise IOError("The l10n directory (for language %r) exists but "
                      "not the clicompanion.mo file" % idioma)
    trans = gettext.translation('clicompanion', locale_dir, languages=[idioma])
    trans.install(unicode=True)

if __name__ == "__main__":
    run()
