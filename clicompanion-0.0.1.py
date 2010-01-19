#!/usr/bin/env python

import os
import curses



def get_param(prompt_string):
    screen.clear()
    screen.border(0)
    screen.addstr(2, 2, prompt_string)
    screen.refresh()
    input = screen.getstr(10, 10, 60)
    return input

def execute_cmd(cmd_string):
    os.system("clear")
    a = os.system(cmd_string)
    print ""
    if a == 0:
        print "Command executed correctly"
        print cmd_string
    else:
        print "Command terminated with error"
    raw_input("Press enter")
    print ""
    

def main(screen):
    global stdscr
    stdscr = screen
 
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
            package = get_param("Enter the package name")
            curses.nocbreak(); screen.keypad(0); curses.echo()
            curses.endwin()
            execute_cmd("dpkg -s " + package)
        if x == "2" :
            curses.nocbreak(); screen.keypad(0); curses.echo()
            curses.endwin()
            execute_cmd("dpkg -l")
        if x == "3" :
            curses.nocbreak(); screen.keypad(0); curses.echo()
            curses.endwin()
            execute_cmd("df -h")
        if x == "4" :
            curses.nocbreak(); screen.keypad(0); curses.echo()
            curses.endwin()
            execute_cmd("free -m")
        if x == "5" :
            curses.nocbreak(); screen.keypad(0); curses.echo()
            curses.endwin()
            execute_cmd("ifconfig")
        if x == "6" :
            curses.nocbreak(); screen.keypad(0); curses.echo()
            curses.endwin()
            execute_cmd("iwconfig")
        if x == "7" :
            curses.nocbreak(); screen.keypad(0); curses.echo()
            curses.endwin()
            execute_cmd("sudo iwlist scan")
        if x == "8" :
            curses.nocbreak(); screen.keypad(0); curses.echo()
            curses.endwin()
            execute_cmd("sudo /etc/init.d/networking restart")
        if x == "9" :
            curses.nocbreak(); screen.keypad(0); curses.echo()
            curses.endwin()
            execute_cmd("lsb_release -a")
        if x == "10" :
            curses.nocbreak(); screen.keypad(0); curses.echo()
            curses.endwin()
            execute_cmd("uname -a")
        if x == "11" :
            curses.nocbreak(); screen.keypad(0); curses.echo()
            curses.endwin()
            execute_cmd("sudo apt-get update && sudo apt-get upgrade")
        if x == "12" :
            package = get_param("Enter the package name")
            curses.nocbreak(); screen.keypad(0); curses.echo()
            curses.endwin()
            execute_cmd("apt-cache search " + package)
        if x == "13" :
            package = get_param("Enter the file name")
            curses.nocbreak(); screen.keypad(0); curses.echo()
            curses.endwin()
            execute_cmd("locate " + package)


curses.wrapper(main)
curses.endwin()


