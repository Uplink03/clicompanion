#!/usr/bin/env python

from os import system
import curses

screen = curses.initscr()

def get_param(prompt_string):
     screen.clear()
     screen.border(0)
     screen.addstr(2, 2, prompt_string)
     screen.refresh()
     input = screen.getstr(10, 10, 60)
     return input

def execute_cmd(cmd_string):
     system("clear")
     a = system(cmd_string)
     print ""
     if a == 0:
          print "Command executed correctly"
          print x
     else:
          print "Command terminated with error"
     raw_input("Press enter")
     print ""
     
x = "0"
bye = "20"

while x != "20":
     

     curses.noecho()
     curses.nocbreak()
     screen.keypad(1)


     screen.clear()
     screen.border(0)
     screen.addstr(2, 2, "Please enter a number then hit Enter")
     screen.addstr(4, 4, "1 - Find version of an installed package")
     screen.addstr(5, 4, "2 - List installed packages")
     screen.addstr(6, 4, "3 - Show disk space")
     screen.addstr(7, 4, "4 - Show RAM usage")
     screen.addstr(8, 4, "5 - Display network information")
     screen.addstr(9, 4, "6 - Display wireless information")
     screen.addstr(10, 4, "7 - Scan wireless networks")
     screen.addstr(11, 4, "8 - Reset the network")
     screen.addstr(12, 4, "9 - What version of Ubuntu do I have?")
     screen.addstr(13, 4, "10 - Kernel Information")
     screen.addstr(14, 4, "11 - Refresh update info and update all packages")
     screen.addstr(15, 4, "12 - Find information on a package (not installed)")
     screen.addstr(16, 4, "13 - Locate a file on your computer")
     screen.addstr(17, 4, "20 - Exit")
     screen.refresh()
     

     x = screen.getstr()

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



curses.nocbreak(); screen.keypad(0); curses.echo()
curses.endwin()


