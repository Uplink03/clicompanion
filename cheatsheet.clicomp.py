#! /usr/bin/env python

import sys
import os

def addcommand():

    cheatsheet = os.path.expanduser("~/.cheatsheet")

    if os.path.exists(cheatsheet):
        pass
    else:
        print "File does not exist.\nCreating file..."
        os.system("touch ~/.cheatsheet")

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
            file.write(str((num_lines + 1)) + ": " + argv[2] + " {{{" + argv[3] + "}}}" + "\n")
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



main()

