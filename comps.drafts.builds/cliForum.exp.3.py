#!/usr/bin/env python

import os
import curses

'''
def get_param(screen, prompt_string):
     screen.clear()
     screen.border(0)
     screen.addstr(2, 2, prompt_string)
     screen.refresh()
     input = screen.getstr(10, 10, 60)
     return input
'''

def get_param_new(screen,y,x, prompt_string):
     screen.addstr(y, x, prompt_string)
     screen.refresh()
     curses.echo(); curses.nocbreak(); screen.keypad(0)
     
     input = screen.getstr()
     
     curses.noecho(); curses.cbreak(); screen.keypad(1)
     
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
     
'''

def execute_cmd_new(screen,args):
    import subprocess
    p = subprocess.Popen(args,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE )
    
    output,errors = p.communicate()
    output = output.split('\n')

    showdata(screen,output)
'''
    
def showdata(screen,data):
    wy,wx=screen.getmaxyx()
    wy-=4
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
    wz=wy+2

    while inkey != '0':
        pad.refresh(y,x,1,1,wy,wx)
        inkey = screen.getkey(wz,2)
        
                
        if inkey=='KEY_UP':y=max(y-1,0)
        elif inkey=='KEY_DOWN':y=min(y+1,max_y)
        elif inkey=='KEY_LEFT':x=max(x-1,0)
        elif inkey=='KEY_RIGHT':x=min(x+1,max_x)
        elif inkey=='KEY_NPAGE':y=min(y+wy,max_y)
        elif inkey=='KEY_PPAGE':y=max(y-wy,0)
        elif inkey=='KEY_HOME':y=0
        elif inkey=='KEY_END':y=max_y
        elif inkey=='a':execute_cmd(screen, "dpkg -l")
        elif inkey=='b':execute_cmd(screen, "df -h")
        elif inkey=='c':execute_cmd(screen, "free -m")
        elif inkey=='d':execute_cmd(screen, "ifconfig")
        elif inkey=='e':execute_cmd(screen, "iwconfig")
        elif inkey=='f':execute_cmd(screen, "sudo iwlist scan")
        elif inkey=='g':execute_cmd(screen, "sudo /etc/init.d/networking restart")
        elif inkey=='h':execute_cmd(screen, "lsb_release -a")
        elif inkey=='i':execute_cmd(screen, "uname -a")
        elif inkey=='j':execute_cmd(screen, "sudo apt-get update && sudo apt-get upgrade")
        elif inkey=='k':
            package = get_param_new(screen, wz,2,"Enter the package name")
            execute_cmd(screen, "apt-cache search " + package)
        elif inkey == "l" :
            package = get_param_new(screen, wz,2,"Enter the file name")
            execute_cmd(screen, "locate " + package)
        elif inkey=='m':execute_cmd(screen, "sudo lshw")

        elif inkey == "n" :
            package = get_param_new(screen, wz,2,"Enter Path to File")
            execute_cmd(screen, "cat " + package)

        elif inkey == "o" :
            package = get_param_new(screen, wz,2,"Enter Path to Directory")
            execute_cmd(screen, "ls " + package)

        elif inkey == "p" :
            package = get_param_new(screen, wz,2,"Enter Path to Directory")
            execute_cmd(screen, "mv " + package)

        elif inkey == "q" :
            package = get_param_new(screen, wz,2,"Enter Path to Directory")
            execute_cmd(screen, "cp " + package)

       
        elif inkey=='r':execute_cmd(screen, "sudo lspci")
        elif inkey=='s':execute_cmd(screen, "lsb_release -a")
        elif inkey=='t':execute_cmd(screen, "lsb_release -a")
        elif inkey=='u':execute_cmd(screen, "lsb_release -a")
        elif inkey=='v':execute_cmd(screen, "lsb_release -a")
        elif inkey=='w':execute_cmd(screen, "lsb_release -a")
        elif inkey=='x':execute_cmd(screen, "lsb_release -a")
        elif inkey=='y':execute_cmd(screen, "lsb_release -a")
        elif inkey=='z':execute_cmd(screen, "lsb_release -a")



        
    

def getmax(lines): return max([len(str(l)) for l in lines])


def menu(screen):
        x = 0
  

        curses.cbreak()
        curses.noecho()
        screen.keypad(1)

        screen.clear()
        screen.border(0)
        data = "Please enter a letter... \n a - Find version of a package \
        \n b - List installed packages \n c - Show RAM usage  \
        \n d - Display network information \n e - Display network information  \
        \n f - Scan Wireless networks  \n g - Reset the network \
        \n h - What version of Ubuntu do I have?  \
        \n i - What kernel am I running   \
        \n j - Refresh update info and update all packages     \
        \n k - Find information on a package (not installed)  \
        \n l - List hardware   \
        \n m - Read File & Print to Standard Output\
        \n n - List Folders Contents \
        \n o - Move (Rename) Files \n p - Copy Files   \
        \n q - attached PCI devices \n r - Show disk space   \
        \n s - List installed packages \n t - Show disk space   \
        \n u - List installed packages \n v - Show disk space   \
        \n w - List installed packages \n x - Show disk space   \
        \n y - List installed packages \n z - Show disk space    \
        \n 1 - List installed packages \n 2 - Show disk space   \
        \n 3 - List installed packages \n 4 - Show disk space   \
        \n 5 - List installed packages \n 6 - Show disk space   \
        \n 7 - List installed packages \n 8 - Show disk space  \
        \n 9 - List installed packages \n 0 - Exit \
        \n 2 - List installed packages \n 3 - Show disk space \
        \n 2 - List installed packages \n 3 - Show disk space \
        \n 2 - List installed packages \n 3 - Show disk space \
        \n 2 - List installed packages \n 3 - Show disk space \
        \n 2 - List installed packages \n 3 - Show disk space \
        \n 2 - List installed packages \n 3 - Show disk space \
        \n 2 - List installed packages \n 3 - Show disk space \
        \n 2 - List installed packages \n 3 - Show disk space \
        \n 2 - List installed packages \n 3 - Show disk space \
        \n 2 - List installed packages \n 3 - Show disk space \
        \n 2 - List installed packages \n 3 - Show disk space \
        \n 2 - List installed packages \n 3 - Show disk space "

        screen.refresh()
       
        showdata(screen,data)

        '''
        if x == ord('1'):
            package = get_param_new(screen,10,4, "Enter the package name: ")
            execute_cmd_new(screen,["dpkg", "-s", package])

        elif x == ord('2'):
            execute_cmd_new(screen,["dpkg", "-l"])

        elif x == ord('3'):
            execute_cmd_new(screen,["df", "-h"])

        elif x == ord('s'):
            curses.nocbreak(); screen.keypad(0); curses.echo()
            wy,wx=screen.getmaxyx()

            screen.addstr(10,4,'Y:'+str(wy))
            screen.addstr(11,4,'X:'+str(wx))

            screen.refresh()
            curses.napms(1000)

        elif x == ord('t'): 

            showdata(screen,data)
        '''

curses.wrapper(menu)
curses.endwin()
