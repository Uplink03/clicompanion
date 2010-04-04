#!/usr/bin/env python

from os import system
import curses
import subprocess

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


def execute_cmd(args):
       p = subprocess.Popen(args,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE )
    
       output,errors = p.communicate()
       input = output.split('\n')
       return input


def execute_cmd_new(screen,args):

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


def menu(screen):
  x = 0

  while x != ord('q'):
       curses.cbreak()
       curses.noecho()
       screen.keypad(1)

       screen.clear()
       screen.border(0)


       data = execute_cmd("cat $HOME/.clicompanion")




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
    

       inkey = screen.getkey()
        
                
       if inkey=='KEY_UP':y=max(y-1,0)
       elif inkey=='KEY_DOWN':y=min(y+1,max_y)
       elif inkey=='KEY_LEFT':x=max(x-1,0)
       elif inkey=='KEY_RIGHT':x=min(x+1,max_x)
       elif inkey=='KEY_NPAGE':y=min(y+wy,max_y)
       elif inkey=='KEY_PPAGE':y=max(y-wy,0)
       elif inkey=='KEY_HOME':y=0
       elif inkey=='KEY_END':y=max_y



       screen.refresh()
       x = screen.getch()

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
            data = range(101)
            showdata(screen,data)

curses.wrapper(menu)  
