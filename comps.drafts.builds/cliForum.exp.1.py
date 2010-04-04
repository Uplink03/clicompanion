#!/usr/bin/env python

from os import system
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

'''
def execute_cmd(cmd_string):
     system("clear")
     a = system(cmd_string)
     print ""
     if a == 0:
          print "Command executed correctly"
     else:
          print "Command terminated with error"
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
    
    


        
        
    

def getmax(lines): return max([len(str(l)) for l in lines])


def menu(screen):
    x = 0
    y=0
    inkey = 0
    while inkey != ord('q'):
        curses.cbreak()
        curses.noecho()
        screen.keypad(1)

        screen.clear()
        screen.border(0)
        data = "Please enter a number... \n 1 - Find version of a package \
        \n 2 - List installed packages \n 3 - \   Show disk space \n q - Exit \
        \n 2 - List installed packages \n 3 - \   Show disk space \n q - Exit \
        \n 2 - List installed packages \n 3 - \   Show disk space \n q - Exit \
        \n 2 - List installed packages \n 3 - \   Show disk space \n q - Exit \
        \n 2 - List installed packages \n 3 - \   Show disk space \n q - Exit \
        \n 2 - List installed packages \n 3 - \   Show disk space \n q - Exit \
        \n 2 - List installed packages \n 3 - \   Show disk space \n q - Exit \
        \n 2 - List installed packages \n 3 - \   Show disk space \n q - Exit \
        \n 2 - List installed packages \n 3 - \   Show disk space \n q - Exit \
        \n 2 - List installed packages \n 3 - \   Show disk space \n q - Exit \
        \n 2 - List installed packages \n 3 - \   Show disk space \n q - Exit \
        \n 2 - List installed packages \n 3 - \   Show disk space \n q - Exit \
        \n 2 - List installed packages \n 3 - \   Show disk space \n q - Exit \
        \n 2 - List installed packages \n 3 - \   Show disk space \n q - Exit \
        \n 2 - List installed packages \n 3 - \   Show disk space \n q - Exit \
        \n 2 - List installed packages \n 3 - \   Show disk space \n q - Exit \
        \n 2 - List installed packages \n 3 - \   Show disk space \n q - Exit \
        \n 2 - List installed packages \n 3 - \   Show disk space \n q - Exit \
        \n 2 - List installed packages \n 3 - \   Show disk space \n q - Exit \
        \n 2 - List installed packages \n 3 - \   Show disk space \n q - Exit \
        \n 2 - List installed packages \n 3 - \   Show disk space \n q - Exit \
        \n 2 - List installed packages \n 3 - \   Show disk space \n q - Exit \
        \n 2 - List installed packages \n 3 - \   Show disk space \n q - Exit \
        \n 2 - List installed packages \n 3 - \   Show disk space \n q - Exit \
        \n 2 - List installed packages \n 3 - \   Show disk space \n q - Exit \
        \n 2 - List installed packages \n 3 - \   Show disk space \n q - Exit \
        \n 2 - List installed packages \n 3 - \   Show disk space \n q - Exit \
        \n 2 - List installed packages \n 3 - \   Show disk space \n q - Exit \
        \n 2 - List installed packages \n 3 - \   Show disk space \n q - Exit \
        \n 2 - List installed packages \n 3 - \   Show disk space \n q - Exit \
        \n 2 - List installed packages \n 3 - \   Show disk space \n q - Exit \
        "

       

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







#        x = pad.getstr(0,0, 2)


        if x == "1" :
            package = get_param(screen, 20, 4, "Enter the package name")
            execute_cmd(screen,"dpkg -s " + package)

        if x == "2" :
            execute_cmd(screen, "dpkg -l")

        if inkey == 3 :
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



curses.wrapper(menu)  
curses.endwin()
