#!/usr/bin/env python

import os
import curses



def get_param(screen,y,x, prompt_string):

    screen.addstr(y, x, prompt_string)
    screen.refresh()
    input = screen.getstr(21, 4, 60)
    return input

def execute_cmd(screen, cmd_string):
    curses.endwin()
    os.system("clear")
    a = os.system(cmd_string)
    print ""
    if a == 0:
        print  cmd_string + " executed correctly"

    else:
        print cmd_string + " terminated with error"
    raw_input("Press enter")
    print ""

    
#def getmax(lines): return max([len(str(l)) for l in lines])

def user_input(screen):


    pad_user_input = curses.newwin(5,50,20,5)


    pad_user_input.border(0)
    pad_user_input.addstr(2, 2, 'Please enter a number then hit Enter',curses.A_BOLD)

    pad_user_input.refresh()



def main(screen):

    pad = curses.newpad(60, 60)
    
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
        


        pad.keypad(1)


        inkey = screen.getkey()
        if inkey == 'KEY_UP':yy=yy+1
        elif inkey == 'KEY_DOWN':yy=yy-1
        pad.refresh( yy,xx, 1,1, 20,60)
        user_input(screen)
                        

#        for y in range(0, 60):
#            for x in range(0, 60):
#                try: pad.addch(y,x, ord('a') + (x*x+y*y) % 26 )
#                except curses.error: pass

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


