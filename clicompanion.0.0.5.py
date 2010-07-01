#!/usr/bin/env python
#
# Key up / Key Down to scroll
# Select a character to run the command that line describes
# 0 to quit
#
# Author: Duane Hinnen <duanedesign@ubuntu.com>
#
# Copyright 2010 Duane Hinnen.
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

import os
import curses

cheatsheet = os.path.expanduser("~/.cheatsheet")

if os.path.exists(cheatsheet):
    pass
else:
#    print "File does not exist.\nCreating file..."
    os.system("touch ~/.cheatsheet")

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
    '''create window, pause for user
    input connect keys to a command'''

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

    pad.setscrreg(0,20)

    for i,line in enumerate(data):
        pad.addstr(i,0,str(line))
    
    x=0
    y=0
    
    inkey=1
    wz=wy+2

    while inkey != 48:
        pad.refresh(y,x,1,1,wy,wx)
        inkey = screen.getch(wz,2)
#        print inkey  #used to find keycodes for assignment to var
# 1 = 49 add a command 259 & 258 up and down arrows
        if inkey==49:addcommand()                
        elif inkey==259:y=max(y-1,0)
        elif inkey==258:y=min(y+1,max_y)
        elif inkey=='KEY_LEFT':x=max(x-1,0)
        elif inkey=='KEY_RIGHT':x=min(x+1,max_x)
        elif inkey=='KEY_NPAGE':y=min(y+wy,max_y)
        elif inkey=='KEY_PPAGE':y=max(y-wy,0)
        elif inkey=='KEY_HOME':y=0
        elif inkey=='KEY_END':y=max_y 
        ####### lowercase a-z ##########
        elif inkey==97:execute_cmd(screen, "dpkg -l")
        elif inkey==98:execute_cmd(screen, "df -h")
        elif inkey==99:execute_cmd(screen, "free -m")
        elif inkey==100:execute_cmd(screen, "ifconfig")
        elif inkey==101:execute_cmd(screen, "iwconfig")
        elif inkey==102:execute_cmd(screen, "sudo iwlist scan")
        elif inkey==103:execute_cmd(screen, "sudo /etc/init.d/networking restart")
        elif inkey==104:execute_cmd(screen, "lsb_release -a")
        elif inkey==105:execute_cmd(screen, "uname -a")
        elif inkey==106:execute_cmd(screen, "sudo apt-get update && sudo apt-get upgrade")
        elif inkey==107:
            package = get_param_new(screen, wz,2,"Enter the package name")
            execute_cmd(screen, "apt-cache search " + package)
        elif inkey == 108 :
            package = get_param_new(screen, wz,2,"Enter the file name")
            execute_cmd(screen, "locate " + package)
        elif inkey==109:execute_cmd(screen, "sudo lshw")
        elif inkey == 110 :
            package = get_param_new(screen, wz,2,"Enter Path to File")
            execute_cmd(screen, "cat " + package)
        elif inkey == 111 :
            package = get_param_new(screen, wz,2,"Enter Path to Directory")
            execute_cmd(screen, "ls " + package)
        elif inkey == 112 :
            package = get_param_new(screen, wz,2,"Enter Path to Directory")
            execute_cmd(screen, "mv " + package)
        elif inkey == 113 :
            package = get_param_new(screen, wz,2,"Enter Path to Directory")
            execute_cmd(screen, "cp " + package)     
        elif inkey==114:execute_cmd(screen, "sudo lspci")
        elif inkey==115:execute_cmd(screen, "lsb_release -a")
        elif inkey==116:execute_cmd(screen, "lsb_release -a")
        elif inkey==117:execute_cmd(screen, "lsb_release -a")
        elif inkey==118:execute_cmd(screen, "lsb_release -a")
        elif inkey==119:execute_cmd(screen, "lsb_release -a")
        elif inkey==120:execute_cmd(screen, "lsb_release -a")
        elif inkey==121:execute_cmd(screen, "lsb_release -a")
        elif inkey==122:execute_cmd(screen, "lsb_release -a")

####### uppercase A-Z ##########    

        elif inkey==65:execute_cmd(screen, "lsb_release -a")    
        elif inkey==66:execute_cmd(screen, "lsb_release -a")            
        elif inkey==67:execute_cmd(screen, "lsb_release -a")          
        


def getmax(lines): return max([len(str(l)) for l in lines])

def menu(screen):
        x = 0


        with open(cheatsheet, 'r') as cmnds:
            co = cmnds.read()



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
        \n s - open \n t - open   \
        \n u - open \n v - open   \
        \n w - open \n x - open   \
        \n y - open \n z - open    \
        \n 1 - Add a command to dict \n 2 - open   \
        \n 3 - open \n 4 - open   \
        \n 5 - open \n 6 - open   \
        \n 7 - open \n 8 - open  \
        \n 9 - open \n 0 - Exit "


        screen.refresh()
       
        showdata(screen,data + co)

        '''
        if x == ord('1'):
            package = get_param_new(screen,10,4, "Enter the package name: ")
            execute_cmd_new(screen,["dpkg", "-s", package])

        elif x == ord('s'):
            curses.nocbreak(); screen.keypad(0); curses.echo()
            wy,wx=screen.getmaxyx()

            screen.addstr(10,4,'Y:'+str(wy))
            screen.addstr(11,4,'X:'+str(wx))

            screen.refresh()
            curses.napms(1000)

        '''
def addcommand():




    singles = ["--list", "--clear", "--debug"]

    argv = sys.argv
    if len(argv) < 3 and argv[1] not in singles:
        help()
    else:
        pass

    if argv[1] == "--store":
        file = open(cheatsheet, 'a')
        num_lines = len(open(cheatsheet).readlines())
        if len(argv) > 3:
            file.write(str(command_letter(num_lines)) + ": " + argv[2] + " {{{" + argv[3] + "}}}" + "\n")
            print "Stored: %s: %s, with key {{{%s}}}" % (num_lines + 1, argv[2], argv[3])
            file.close()
            sys.exit()
        else:
            file.write(str((num_lines + 1)) + ": " + argv[2] + "\n")
            print "Stored: %s: %s" % (num_lines + 1, argv[2])
            file.close()
            sys.exit()

    elif argv[1] == "--lookup":
        try:
            int(argv[2])
        except ValueError:
            file = open(cheatsheet)
            lines = file.readlines()
            itr = 0
            for i in range(len(lines)):
                if "{{{%s}}}" % argv[2] in lines[itr]:
                    print lines[itr]
                    if itr >= len(lines):
                        break
                else:
                    pass
                itr += 1
            file.close()
            
        file = open(cheatsheet)
        lines = file.readlines()
        itr = 0
        for i in range(len(lines)):
            if lines[itr].startswith(argv[2]):
                print lines[itr]
                break
            else:
                pass
            itr += 1
        file.close()

    elif argv[1] == "--list":
        os.system("cat ~/.cheatsheet | more")

    elif argv[1] == "--clear":
        if len(argv) > 2:
            try:
                int(argv[2])
            except:
                file = open(cheatsheet, 'r')
                lines = file.readlines()
                file.close()
                file = open(cheatsheet, 'w')
                itr = 0
                for i in lines:
                    if ("{{{%s}}}" % argv[2]) in i:
                        lines.pop(itr)
                        break
                    itr += 1
                file.writelines(lines)
                file.close()

            file = open(cheatsheet, 'r')
            lines = file.readlines()
            file.close()
            file = open(cheatsheet, 'w')
            itr = 0
            for i in lines:
                if i.startswith(argv[2]):
                    lines.pop(itr)
                    break
                itr += 1
            file.writelines(lines)
            file.close()
        
        else:
            os.remove(cheatsheet)
            print "%s, cleared." % cheatsheet

    elif argv[1] == "--use":
        file = open(cheatsheet)
        lines = file.readlines()
        itr = 0
        for i in range(len(lines)):
            if argv[2] in lines[itr]:
                if "{{{" in lines[itr]:
                    command = lines[itr].split(":")[1].split("{{{")[0].rstrip()                    
                else:
                    command = lines[itr].split(":")[1].rstrip()
                
                print "Using: ", command
                os.system(command)
                break
            itr += 1
    elif argv[1] == "--debug":
        itr = 0
        os.system("cat ~/.cheatsheet | more")
        for i in range(len(argv)):
            print argv[itr]
            itr += 1
                

def command_letter(num_lines):

    new_line = num_lines + 1

if new_line = 1
    comcam = 'A'
elif new_line = 2
    comcam = 'B'
elif new_line = 3
    com_cam = 'C'
elif new_line = 4
    comcam = 'D'
elif new_line = 5
    com_cam = 'E'
elif new_line = 6
    comcam = 'F'
elif new_line = 7
    com_cam = 'G'
elif new_line = 8
    comcam = 'H'
elif new_line = 9
    com_cam = 'I'
elif new_line = 10
    comcam = 'J'
elif new_line = 11
    com_cam = 'K'
elif new_line = 12
    comcam = 'L'
elif new_line = 13
    com_cam = 'M'
elif new_line = 14
    comcam = 'N'
elif new_line = 15
    comcam = 'O'
elif new_line = 16
    comcam = 'P'
elif new_line = 17
    comcam = 'Q'
elif new_line = 18
    comcam = 'R'
elif new_line = 19
    comcam = 'S'
elif new_line = 20
    comcam = 'T'
elif new_line = 21
    comcam = 'U'
elif new_line = 22
    comcam = 'V'
elif new_line = 23
    comcam = 'W'
elif new_line = 24
    comcam = 'X'
elif new_line = 25
    comcam = 'Y'
elif new_line = 26
    comcam = 'Z'







def help():
    print "\nUsage: cheat [option]"
    print "   or: cheat [option] string\n\n"
    print "\t--store <command> <key>"
    print "\t\tStores command <command> and allows for an optional <key>."
    print "\t--list"
    print "\t\tLists the current enntries and their index numbers and keys."
    print "\t--use <index>/<key>"
    print "\t\tRuns the command stored at/with index/key."
    print "\t--clear (<index/key>)"
    print "\t\tClears the ~/.cheatsheet file or clears specified entry."
    print "\t--debug"
    print "\t\tPrints some useful debugging information."
    print "\t--help"
    print "\t\tPrints this help message.\n"

    sys.exit()

curses.wrapper(menu)
curses.endwin()
