#!/usr/bin/env python

import os
import curses



def get_param(screen,y,x, prompt_string):

    screen.addstr(y, x, prompt_string)
    screen.refresh()
    input = screen.getstr(21, 4, 60)
    return input


def execute_cmd(screen,args):
    import subprocess
    p = subprocess.Popen(args,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE )
    
    output,errors = p.communicate()
    output = output.split('\n')

    showdata(screen,output)
    
    
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
        
        
def getmax(lines): return max([len(str(l)) for l in lines])
    

def main(screen):

    if curses.has_colors():

        bg = curses.COLOR_WHITE
        curses.init_pair(1, curses.COLOR_BLUE, bg)
        curses.init_pair(2, curses.COLOR_RED, bg)


    x = "0"
    bye = "20"

    while x != "20":

        curses.echo()
        curses.nocbreak()

        screen.clear()
        screen.border(0)
        screen.addstr(2, 2, "Please enter a number then hit Enter",curses.A_BOLD)
        screen.addstr(4, 4, "1 - Find version of an installed package", curses.color_pair(1))
        screen.addstr(5, 4, "2 - List installed packages", curses.color_pair(1))
        screen.addstr(6, 4, "3 - Show disk space", curses.color_pair(1))
        screen.addstr(7, 4, "4 - Show RAM usage", curses.color_pair(1))
        screen.addstr(8, 4, "5 - Display network information", curses.color_pair(1))
        screen.addstr(9, 4, "6 - Display wireless information", curses.color_pair(1))
        screen.addstr(10, 4, "7 - Scan wireless networks", curses.color_pair(1))
        screen.addstr(11, 4, "8 - Reset the network", curses.color_pair(1))
        screen.addstr(12, 4, "9 - What version of Ubuntu do I have?", curses.color_pair(1))
        screen.addstr(13, 4, "10 - Kernel Information", curses.color_pair(1))
        screen.addstr(14, 4, "11 - Refresh update info and update all packages", curses.color_pair(1))
        screen.addstr(15, 4, "12 - Find information on a package (not installed)", curses.color_pair(1))
        screen.addstr(16, 4, "13 - Locate a file on your computer", curses.color_pair(1))
        screen.addstr(17, 4, "20 - Exit", curses.color_pair(2))
        screen.refresh()
     

        x = screen.getstr(18,4, 2)

        if x == "1" :
            package = get_param(screen, 20, 4, "Enter the package name")
            execute_cmd(screen,["dpkg", "-s", package])

        if x == "2" :
            execute_cmd(screen,["dpkg", "-l"])

        if x == "3" :
            execute_cmd(screen, ["df", " -h"])

        if x == "4" :
            execute_cmd(screen, ["free", "-m"])

        if x == "5" :
            execute_cmd(screen, ["ifconfig"])

        if x == "6" :
            execute_cmd(screen, ["iwconfig"])

        if x == "7" :
            execute_cmd(screen, ["sudo", "iwlist scan"])

        if x == "8" :
            execute_cmd(screen, ["sudo /etc/init.d/networking restart"])

        if x == "9" :
            execute_cmd(screen, ["lsb_release"," -a"])

        if x == "10" :
            execute_cmd(screen, ["uname", "-a"])

        if x == "11" :
            execute_cmd(screen, ["sudo apt-get update && sudo apt-get upgrade"])

        if x == "12" :
            package = get_param(screen, 20, 4,"Enter the package name")
            execute_cmd(screen, ["apt-cache", "search " + package])

        if x == "13" :
            package = get_param(screen, 20, 4,"Enter the file name")
            execute_cmd(screen,["locate" + package])


curses.wrapper(main)
curses.endwin()


