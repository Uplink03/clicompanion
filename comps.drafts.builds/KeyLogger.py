# KeyLogger_tk2.py
# show a character <strong class="highlight">key</strong> when pressed without using Enter <strong class="highlight">key</strong>
# hide the Tkinter GUI window, only console shows

try:
    # Python2
    import Tkinter as tk
except ImportError:
    # Python3
    import tkinter as tk

def key(event):
    """shows <strong class="highlight">key</strong> or tk code for the <strong class="highlight">key</strong>"""
    if event.keysym == 'Escape':
        root.destroy()
    if event.char == event.keysym:
        # normal number and letter characters
        print( 'Normal Key %r' % event.char )
    elif len(event.char) == 1:
        # charcters like []/.,><#$ also Return and ctrl/key
        print( 'Punctuation Key %r (%r)' % (event.keysym, event.char) )
    else:
        # f1 to f12, shift keys, caps lock, Home, End, Delete ...
        print( 'Special Key %r' % event.keysym )


root = tk.Tk()
print( "Press a key (Escape key to exit):" )
root.bind_all('<Key>',key)
# don't show the tk window
root.withdraw()
root.mainloop()
