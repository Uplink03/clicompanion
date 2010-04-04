#!/usr/bin/env python
# psax.py; illustration of curses library
# runs the shell command ps ax and saves the last lines of its output,
# as many as the window will fit; allows the user to move up and down
# within the window, killing those processes
# run line:
#python psax.py
# user commands:
''''u':
move highlight up a line
'd':
move highlight down a line
'k':
kill process in currently highlighted line
'r':
re-run 'ps ax' for update
'q':
quit'''
# possible extensions: allowing scrolling, so that the user could go
# through all the ps ax output; allow wraparound for long lines; ask
# user to confirm before killing a process

import curses, os, sys, traceback

# global variables
class gb:
    scrn = None # will point to Curses window object
    cmdoutlines = [] # output of 'ps ax' (including the lines we don't

# use, for possible future extension)

winrow = None # current row position in screen
startrow = None # index of first row in cmdoutlines to be displayed
def runpsax():
    p = os.popen('ps ax','r')
    gb.cmdoutlines = []
    row = 0

    for ln in p:
    # don't allow line wraparound, so truncate long lines
        ln = ln[:curses.COLS]

# remove EOLN if it is still there
    if ln[-1] == '\n': ln = ln[:-1]

    gb.cmdoutlines.append(ln)
    p.close()

# display last part of command output (as much as fits in screen)
def showlastpart():
    # clear screen
    gb.scrn.clear()
    # prepare to paint the (last part of the) 'ps ax' output on the screen
    gb.winrow = 0
    ncmdlines = len(gb.cmdoutlines)
    # two cases, depending on whether there is more output than screen rows
    if ncmdlines <= curses.LINES:
        gb.startrow = 0
        nwinlines = ncmdlines
        gb.startrow = ncmdlines - curses.LINES - 1
        nwinlines = curses.LINES
        lastrow = gb.startrow + nwinlines - 1

# now paint the rows
    for ln in gb.cmdoutlines[gb.startrow:lastrow]:
        gb.scrn.addstr(gb.winrow,0,ln)



        gb.winrow += 1
        # last line highlighted
        gb.scrn.addstr(gb.winrow,0,gb.cmdoutlines[lastrow],curses.A_BOLD)
        gb.scrn.refresh()

# move highlight up/down one line
def updown(inc):
    tmp = gb.winrow + inc
# ignore attempts to go off the edge of the screen
    if tmp >= 0 and tmp < curses.LINES:
# unhighlight the current line by rewriting it in default attributes
        gb.scrn.addstr(gb.winrow,0,gb.cmdoutlines[gb.startrow+gb.winrow])
# highlight the previous/next line
        gb.winrow = tmp
        ln = gb.cmdoutlines[gb.startrow+gb.winrow]
        gb.scrn.addstr(gb.winrow,0,ln,curses.A_BOLD)
        gb.scrn.refresh()

# kill the highlighted process
def kill():
    ln = gb.cmdoutlines[gb.startrow+gb.winrow]
    pid = int(ln.split()[0])
    os.kill(pid,9)

# run/re-run 'ps ax'
    def rerun():
        runpsax()
        showlastpart()

def main():
# window setup
    gb.scrn = curses.initscr()
    curses.noecho()
    curses.cbreak()
    # rpdb.set_trace() (I used RPDB for debugging)
    # run 'ps ax' and process the output
    gb.psax = runpsax()
    # display in the window
    showlastpart()
    # user command loop
    while True:
        # get user command
        c = gb.scrn.getch()
        c = chr(c)
        if c == 'u': updown(-1)
        elif c == 'd': updown(1)
        elif c == 'r': rerun()
        elif c == 'k': kill()
        else: break

    restorescreen()

    def restorescreen():
        curses.nocbreak()
        curses.echo()
        curses.endwin()

if __name__ =='__main__':
    main()
    restorescreen()

    # print error message re exception
    traceback.print_exc()

