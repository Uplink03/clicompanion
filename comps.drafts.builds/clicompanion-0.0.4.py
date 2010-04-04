#!/usr/bin/env python

import os
import curses
import subprocess


def get_param(screen,y,x, prompt_string):

    screen.addstr(y, x, prompt_string)
    screen.refresh()
    input = screen.getstr(21, 4, 60)
    return input

def execute_cmd(screen,args):

### subprocess.Popen(args,
###                        stdout=subprocess.PIPE,
###                        stderr=subprocess.PIPE )

    p = os.system(args)
    o = str(p)
#    output,errors = p.communicate()
#    output = output.split('\n')

    showdata(screen,o)

    
def getmax(lines): return max([len(str(l)) for l in lines])

def user_input(screen):


    win_user_input = curses.newwin(5,50,20,5)
    win_user_input.border(0)
    win_user_input.addstr(2, 2, 'Please enter a number then hit Enter',curses.A_BOLD)

    win_user_input.refresh()



def showdata(screen,data):
    wy,wx=screen.getmaxyx()
    wy-=2
    wx-=2
    if type(data)==str:
        data = data.split('\n')

    padx = max(getmax(data),wx)
    pady = max(len(data)+1,wy)
    max_x = padx-wx
    max_y = pady-wy
    
        
    pad = curses.newpad(pady,padx)
        
    for i,line in enumerate(data):
        pad.addstr(i,0,str(line))
    
    x=0
    y=0
    
    inkey=0
    
    while inkey != 'q':
        pad.refresh(y,x,1,1,wy,wx)
        inkey = screen.getkey()
        
                
        if inkey=='KEY_UP':y=max(y-1,0)
        elif inkey=='KEY_DOWN':y=min(y+1,max_y)
        elif inkey=='KEY_LEFT':x=max(x-1,0)
        elif inkey=='KEY_RIGHT':x=min(x+1,max_x)
        elif inkey=='KEY_NPAGE':y=min(y+wy,max_y)
        elif inkey=='KEY_PPAGE':y=max(y-wy,0)
        elif inkey=='KEY_HOME':y=0
        elif inkey=='KEY_END':y=max_y
        





def main(screen):

    pad = curses.newpad(110, 60)
    
    if curses.has_colors():

        bg = curses.COLOR_WHITE
        curses.init_pair(1, curses.COLOR_BLUE, bg)
        curses.init_pair(2, curses.COLOR_RED, bg)


    x = "0"
    bye = "20"

    while x != "20":



        pad.clear()
        pad.border()

        pad.addstr(4, 4, "1 - Find version of an installed package", curses.color_pair(1))
        pad.addstr(5, 4, "2 - List installed packages", curses.color_pair(1))
        pad.addstr(6, 4, "3 - Show disk space", curses.color_pair(1))
        pad.addstr(7, 4, "4 - Show RAM usage", curses.color_pair(1))
        pad.addstr(8, 4, "5 - Display network information", curses.color_pair(1))
        pad.addstr(9, 4, "6 - Display wireless information", curses.color_pair(1))
        pad.addstr(10, 4, "7 - Scan wireless networks", curses.color_pair(1))
        pad.addstr(11, 4, "8 - Reset the network", curses.color_pair(1))
        pad.addstr(12, 4, "9 - What version of Ubuntu do I have?", curses.color_pair(1))
        pad.addstr(13, 4, "10 - Kernel Information", curses.color_pair(1))
        pad.addstr(14, 4, "11 - Refresh update info and update all packages", curses.color_pair(1))
        pad.addstr(15, 4, "12 - Find information on a package (not installed)", curses.color_pair(1))
        pad.addstr(16, 4, "13 - Locate a file on your computer", curses.color_pair(1))
        pad.addstr(17, 4, "13 - Locate a file on your computer", curses.color_pair(1))
        pad.addstr(18, 4, "13 - Locate a file on your computer", curses.color_pair(1))
        pad.addstr(19, 4, "13 - Locate a file on your computer", curses.color_pair(1))
        pad.addstr(20, 4, "13 - Locate a file on your computer", curses.color_pair(1))
        pad.addstr(21, 4, "13 - Locate a file on your computer", curses.color_pair(1))
        pad.addstr(22, 4, "13 - Locate a file on your computer", curses.color_pair(1))
        pad.addstr(23, 4, "13 - Locate a file on your computer", curses.color_pair(1))
        pad.addstr(24, 4, "13 - Locate a file on your computer", curses.color_pair(1))
        pad.addstr(25, 4, "13 - Locate a file on your computer", curses.color_pair(1))
        pad.addstr(26, 4, "13 - Locate a file on your computer", curses.color_pair(1))
        pad.addstr(27, 4, "13 - Locate a file on your computer", curses.color_pair(1))
        pad.addstr(28, 4, "13 - Locate a file on your computer", curses.color_pair(1))
        pad.addstr(29, 4, "13 - Locate a file on your computer", curses.color_pair(1))
        pad.addstr(30, 4, "13 - Locate a file on your computer", curses.color_pair(1))
        pad.addstr(31, 4, "13 - Locate a file on your computer", curses.color_pair(1))
        pad.addstr(32, 4, "13 - Locate a file on your computer", curses.color_pair(1))
        pad.addstr(33, 4, "20 - Exit", curses.color_pair(2))
        yy=0
        xx=0
        pad.noutrefresh( yy,xx, 1,1, 20,60)
                
        #if x=='KEY_UP':y=y+1
        #elif x=='KEY_DOWN':x=x-1
        
        user_input(screen)
                        

        #for y in range(0, 60):
         #   for x in range(0, 60):
        #        try: pad.addch(y,x, ord('a') + (x*x+y*y) % 26 )
        #        except curses.error: pass

        x = pad.getstr(0,0, 2)


        if x == "1" :
            package = get_param(screen, 20, 4, "Enter the package name")
            execute_cmd(screen,"dpkg -s " + package)

        if x == "2" :
            execute_cmd(screen, "dpkg -l")

        if x == "3" :
            execute_cmd(screen, "df -h")

        if x == "4" :
            execute_cmd(screen, "free -m")

        if x == "5" :
            execute_cmd(screen, "ifconfig")

        if x == "6" :
            execute_cmd(screen, "iwconfig")

        if x == "7" :
            execute_cmd(screen, "sudo iwlist scan")

        if x == "8" :
            execute_cmd(screen, "sudo /etc/init.d/networking restart")

        if x == "9" :
            execute_cmd(screen, "lsb_release -a")

        if x == "10" :
            execute_cmd(screen, "uname -a")

        if x == "11" :
            execute_cmd(screen, "sudo apt-get update && sudo apt-get upgrade")

        if x == "12" :
            package = get_param(screen, 20, 4,"Enter the package name")
            execute_cmd(screen, "apt-cache search " + package)

        if x == "13" :
            package = get_param(screen, 20, 4,"Enter the file name")
            execute_cmd(screen, "locate " + package)


curses.wrapper(main)
curses.endwin()


