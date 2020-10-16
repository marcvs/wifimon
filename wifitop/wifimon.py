#!/usr/bin/env python3
''' a wifi signal strength display '''
# vim: tw=100 foldmethod=marker
# pylint: disable=invalid-name, superfluous-parens
# pylint: disable=logging-not-lazy, logging-format-interpolation


import argparse
import os
import subprocess
import re
from datetime import datetime
from time import sleep
from sys import stdout, exit
import copy
import fileinput
import operator
from xtermcolor import colorize
# import threading
# import Queue
# from getch.getch import getch

def read_ethermap(ethersFile):
    '''Read ethermap'''
    try:
        ethermap = {}
        for line in fileinput.input(args.ethersFile):
            entries = re.split(' ', line)
            key = entries[0]
            entries[-1] = entries[-1].rstrip("\n")
            ethermap[key] = ' '.join(entries[1:])
    except Exception as e:
        print("Error: " + str(e))
        return None
    return ethermap
def parseOptions():
    '''Parse the commandline options'''
    parser = argparse.ArgumentParser(description='google-doc-watcher')
    parser.add_argument('--verbose','-v', dest='verbose', action='count',
                        default=0)
    parser.add_argument('--device','-d', dest='wifiDevice',
                        default='wlan0')
    parser.add_argument('-n', dest='prettyprintEthers',
                        default=True, action='store_false')
    parser.add_argument('--ethers','-e', dest='ethersFile',
                        default=os.getenv("HOME")+"/.config/wifimon/ethers")
    parser.add_argument('--input','-i', dest='inputFromFile',
                        default=None)
    parser.add_argument('-cc', dest='col_crypto',   default=0x44bb44)
    parser.add_argument('-ce', dest='col_essid',    default=0x00ff00)
    parser.add_argument('-cm', dest='col_mac',      default=0x66ff66)
    parser.add_argument('-ch', dest='col_ch',       default=0xffff22)
    parser.add_argument('-cf', dest='col_fr',       default=0xffff99)
    parser.add_argument('-cq', dest='col_qu',       default=0x22ffff)
    parser.add_argument('-cl', dest='col_le',       default=0x99ffff)
    parser.add_argument('-co', dest='col_mo',       default=0xff9999)
    parser.add_argument('-ct', dest='col_meter',    default=0x00ff00)
    parser.add_argument('-cs', dest='col_speed',    default=0x0000ff)
    parser.add_argument('-ca', dest='col_last',     default=0x555555)
    parser.add_argument('-ci', dest='col_hi',       default=0xff9999)
    parser.add_argument('-up', dest='update_interval',  default=2)
    #parser.add_argument('--outputdir','-o', dest='basedir',
                        #default=defaultpath)
                        ##default=os.getenv("HOME")+"/.google-doc-downloader")
    #parser.add_argument('--width','-w', dest='mailOutputWidth',
                        #default=66)
    #parser.add_argument('--no-reflow', dest='mailOutputReflow',
                        #action='store_false', default=True)
    #parser.add_argument('--colordiffOptions', dest='colordiffOptions',
                        #default='-u7')
    #parser.add_argument('--ansi2html', dest='path_ansitohtml',
                        #default=defaultpath+"/ansi2html.sh")
    #parser.add_argument('--smtp-user', '-u', dest='smtpUser',
                        #default="")
    #parser.add_argument('--smtp-pass', '-p', dest='smtpPass',
                        #default="")
    #parser.add_argument('--smtp-host', '-s', dest='smtpHost',
                        #default="")
    #parser.add_argument('--quiet', '-q', dest='quiet', action='store_true',
                        #default=False)
    args = parser.parse_args()
    return args
args = parseOptions()

# conversion strings for crypt strings
crypto_filter = {}
crypto_filter ["IEEE 802.11i/WPA2 Version 1"] = "WPA2"
crypto_filter ["WPA Version 1"] =               "WPA1"
#crypto_filter [""] = "                     "


ethermap = read_ethermap(args.ethersFile)

#startupCwd = os.getcwd()
#os.chdir(args.basedir)

class wifiCell:
    '''encapsulate wifi cell information'''
    def __init__(self):
        self.mac                = ""
        self.channel            = 0
        self.frequency          = 0
        self.quality            = ""
        self.encryption         = False
        self.encryption_type    = ""
        self.essid              = ""
        self.bitrates           = ""
        self.bitrate            = ""
        self.txpower            = ""
        self.mode               = ""
        self.last_seen          = ""
        self.crypto             = []
        self.authentication     = []
        self.group_cipher       = []
        self.pair_cipher        = []
        self.connected          = False

    def display(self, show_essid=True):
        '''pretty print'''
        output = ""
        multiplier = 1
        now = datetime.now()
        age = (now - self.last_seen).total_seconds()

        if age > 60:
            return ""

        bg = 0x000000
        col_mac     = args.col_mac
        col_ch      = args.col_ch
        col_fr      = args.col_fr
        col_qu      = args.col_qu
        col_le      = args.col_le
        col_mo      = args.col_mo
        col_meter   = args.col_meter
        col_speed   = args.col_speed
        col_last    = args.col_last 

        # print (F" connected: {self.connected}")

        if age > 20:
            col_mac     = 0x118811
            col_ch      = 0xaaaa22
            col_fr      = 0xaaaa99
            col_qu      = 0x22aaaa
            col_le      = 0x66aaaa
            col_mo      = 0xaa9999
            col_meter   = 0x008800
            col_speed   = 0x000088
            col_last    = 0x555555

        if self.connected:
            multiplier = 1
            col_mac     = args.col_hi
            col_ch      = args.col_hi
            col_fr      = args.col_hi
            col_qu      = args.col_hi
            col_le      = args.col_hi
            col_mo      = args.col_hi
            col_meter   = args.col_hi
            col_speed   = args.col_hi
            col_last    = args.col_hi

        # preformatting: mac addresses:
        # FIXME: asdfsdf 
        formatted_mac = self.mac
        if args.prettyprintEthers:
            try:
                formatted_mac = ethermap[self.mac]
                # print (F"  mac: formatted: {formatted_mac} -- orig: {self.mac}")
            except KeyError as e:
                pass

        #output += ' %s' %   colorize(               self.mac,           int(multiplier*col_mac), bg=bg))
        output += '  %s' %   colorize("{:<17}".format(formatted_mac[:17]),   int(multiplier*col_mac), bg=bg)
        if age > 40:
            output += colorize (F" --------------------------------[ expired: {age:2.0f}s ] \n", col_last, bg=bg)
            return output

        output += ' %s'  %   colorize("{:<3}".format(self.channel),      int(multiplier*col_ch), bg=bg)
        output += ' (%s)' %  colorize("{:<5}".format(self.frequency),    int(multiplier*col_fr), bg=bg)
        output += ' %s'  %   colorize("{:<5}".format(self.quality),      int(multiplier*col_qu), bg=bg)
        output += ' (%s)' %  colorize("{:<3}".format(self.level),        int(multiplier*col_le), bg=bg)
        output += ' %s'  %   colorize("{:<7}".format(self.mode),         int(multiplier*col_mo), bg=bg)
        #output += ' (%5s)' % self.frequency )
        #output += ' (%3s)' % self.level)
        if show_essid:
                output += ' '  + self.essid

        # meter
        output += colorize(" [", col_meter, bg=bg)
        i=0
        for i in range (0, int(self.quality/5)):
            output += colorize("*", col_meter, bg=bg)
        if i==0:
            for i in range (int(70/5)):
                output += colorize("-", col_meter, bg=bg)
        else:
            for x in range (i+1,int(70/5)):
                output += colorize("·", col_meter, bg=bg)
        output += colorize("]", col_meter, bg=bg)

        # speed
        if self.bitrate != "" or self.txpower != "":
            output += colorize(" [", col_speed, bg=bg)
            if self.bitrate != "":
                output += colorize("{:} Mb/s  ".format(self.bitrate), col_speed, bg=bg)
            if self.txpower != "":
                output += colorize("{:>2} dBm".format(self.txpower), col_speed, bg=bg)
            output += colorize("]", col_speed, bg=bg)

        # last seen
        if (age > 10):
            output += colorize(F" age: {age:2.0f}s", int(multiplier*col_last), bg=bg)

        output += '\n'

        return output

    def display_long(self, show_essid=True):
        '''pretty print'''
        # for (k,v) in crypto_filter.items():
            # encryption_string = encryption_string.replace(k,v)
        
        print ('''        %s:
         Channel:    %s (%s GHz)
         Quality:    %s (%s dBm)
         Encryption: %s''' % (self.mac, self.channel, self.frequency,
                            self.quality, self.level, self.encryption))
        if show_essid:
            print ('''       ESSID:      %s''' % self.essid)
        print ('''       Mode:       %s''' % self.mode)
        print ('''       Last Seen:  %s''' % self.last_seen )

class wifiEssid:
    '''collect wifi cells with the same essid'''
    def __init__(self):
        self.cells      = {}
        self.encryption = False
        self.crypto     = ""

    def display(self):
        '''pretty print'''
        # preformatting: Crypto
        output = ""
        temp = []
        if self.encryption:
            for i in range(len(self.crypto)):
                temp.append (self.crypto[i] + \
                        "(" + self.authentication[i] + \
                        "/" + self.group_cipher[i] + \
                        "/" + self.pair_cipher[i] + ")" )
        else:
            temp.append ("insecure")
        encryption_string = " + ".join (temp)
        for (k,v) in crypto_filter.items():
            encryption_string = encryption_string.replace(k,v)
        encryption_string = colorize("%s" % "["+encryption_string+"]", args.col_crypto)

        output += ("%s %s\n" % (colorize("%s" % self.essid, args.col_essid),\
                                encryption_string.rstrip()))

        for cell in sorted(self.cells.values(), key=operator.attrgetter('quality')):
            output += cell.display(show_essid=False)
            # print (F"   quality: {cell.quality}")
            # print (F"   level  : {cell.level}")
        output += "\n"
        return output

    def add_cell(self, cell):
        if not cell.mac in self.cells.keys():
            self.cells[cell.mac] = copy.deepcopy(cell)
            self.encryption      = self.cells[cell.mac].encryption
            self.crypto          = self.cells[cell.mac].crypto
            self.authentication  = self.cells[cell.mac].authentication
            self.group_cipher    = self.cells[cell.mac].group_cipher
            self.pair_cipher     = self.cells[cell.mac].pair_cipher
        else: # if the cell already exists we don't copy the crypto settings
            self.cells[cell.mac] = copy.deepcopy(cell)

class WifiInformation:
    '''collect and updates wifi essids'''
    def __init__(self):
        self.essids = {}

    def shellcall(self, commandline):
        '''call a shell command'''
        if args.verbose:
            print (F"shellcall cmdline: {commandline}")
        tmpout = "/tmp/shellcall-"+os.getpid().__str__()+"out"
        tmperr = "/tmp/shellcall-"+os.getpid().__str__()+"err"

        retval = subprocess.call(commandline, shell=True,
                        stdout = open(tmpout, "w"), stderr = open(tmperr, "w"))

        output = open(tmpout, "r").read()
        errors = open(tmperr, "r").read()

        if not args.verbose:
            os.remove (tmpout)
            os.remove (tmperr)

        return retval, output, errors

    def update(self):
        '''Gather input for the currently connected AP'''
        current_cell = wifiCell()
        try:
            (retval, iwcfgOutput, errors) = self.shellcall("iwconfig "+args.wifiDevice)
        except Exception as e:
            print (str(e))


        (retval, iwlistOutput, errors) = self.shellcall("ifconfig "+args.wifiDevice+" up")
        if args.inputFromFile == None:
            (retval, iwlistOutput, errors) = self.shellcall("iwlist "+args.wifiDevice+" scan")
        else:
            with open(args.inputFromFile, 'r') as fd:
                iwlistOutput = fd.read()

        status_cell = ""
        status_last_cell = ""
        status_essid = ""
        for line in iwlistOutput.split("\n"):
            if args.verbose > 1:
                print (line)
            line = line.rstrip().lstrip()
            if re.match("Cell", line): # a new cell is starting
                f = line.split(" ")
                (cell, number, dash, label, mac) = (f[0], f[1], f[2], f[3], f[4])
                # cycle the info:
                status_last_cell = status_cell
                status_cell = mac
                # if there was a previous cell, that one is finished now
                # and we can add that one to it's coresponding essid
                if status_cell != status_last_cell and status_last_cell != "":
                    if status_essid not in self.essids.keys():
                        self.essids[status_essid] = wifiEssid()
                    self.essids[status_essid].essid = status_essid
                    self.essids[status_essid].add_cell(new_cell)

                    # if status_essid == "knarz":
                    #     print (F"  status_essid: {status_essid}")
                    #     print (F"  len(self.essids[status_essid]): {len(self.essids[status_essid].cells)}")
                    #     print (F"  {self.essids[status_essid]}")
                    # self.essids[status_essid].display()

                new_cell = wifiCell()
                new_cell.mac = mac
                new_cell.last_seen = datetime.now()


            if re.match("Channel", line):
                new_cell.channel    = line.split(":")[1]

            if re.match("Frequency", line):
                new_cell.frequency  = line.split(":")[1].split(" ")[0]

            if re.match("Quality", line):
                # new_cell.quality    = line.split("=")[1].split(" ")[0]
                new_cell.quality    = int(line.split("=")[1].split(" ")[0].split("/")[0])
                new_cell.level      = int(line.split(" ")[3].split("=")[1])

            if re.match("Encryption", line):
                if re.search("on", line.split(":")[1]):
                    new_cell.encryption = True
                else:
                    new_cell.encryption = False

            if re.match("ESSID", line):
                status_essid = line.split(":")[1].replace('"','')
                new_cell.essid = status_essid

            #if re.match("Bit Rates", line): # too complicated to parse for now
                #new_cell.channel = line.split(":")[1].split(" ")[0]

            if re.match("Mode", line):
                new_cell.mode               = line.split(":")[1]

            if not re.match("IE: Unknown", line):
                if re.match("IE: ", line):
                    new_cell.crypto.append(line.split(":")[1].lstrip())

            if re.match("Group Cipher", line):
                new_cell.group_cipher.append(line.split(" : ")[1].lstrip())

            if re.match("Pairwise Ciphers", line):
                new_cell.pair_cipher.append(line.split(" : ")[1].lstrip())

            if re.match("Authentication Suites", line):
                new_cell.authentication.append(line.split(" : ")[1].lstrip())


        # if args.verbose:
        #     print (F"   wifiInformantion self: {dir(self)}")
        #     print (F"   Updater Loop done, gathered {len(self.essids)}")
        #     print (F"   Updater Loop done, gathered {self.essids}")
        # at the end of the for loop we also have to add the last cell
        if status_cell != status_last_cell:
            if not status_essid in self.essids.keys():
                self.essids[status_essid]   = wifiEssid()
            self.essids[status_essid].essid = status_essid
            self.essids[status_essid].add_cell(new_cell)


        # Gather input for the currently connected AP
        try:
            # current_cell.__init__()
            for line in iwcfgOutput.split("\n"):
                # print(line)
                line = line.rstrip().lstrip()
                if re.match(args.wifiDevice, line):
                    current_cell.essid      = line.split(":")[1].replace('"','')


                if re.match("Mode:", line):
                    #current_cell.mode      = line.split(":")[1].split(" ")[0]
                    current_cell.frequency  = line.split(":")[2].split(" ")[0]
                    current_cell.mac        = line.split(" ")[7]
                if re.match("Link Quality", line):
                    current_cell.quality    = int(line.split("=")[1].split(" ")[0].split("/")[0])
                    current_cell.level      = int(line.split("=")[2].split(" ")[0])
                if re.match("Bit Rate", line):
                    current_cell.bitrate    = line.split("=")[1].split(" ")[0]
                    current_cell.txpower    = line.split("=")[2].split(" ")[0]
                current_cell.last_seen      = datetime.now()
            current_cell.channel            = self.essids[current_cell.essid].cells[current_cell.mac].channel
            current_cell.connected = True
            self.essids[current_cell.essid].add_cell(current_cell)

            #stdout.write(str(current_cell.bitrate))
            #current_cell.display(show_essid=False)
        except Exception as e:
            print (str(e))
       
    def display(self):
        '''pretty print'''
        output = ""
        for essid in self.essids.keys():
            output += self.essids[essid].display()
        return output

if args.verbose: print ("device: %s" % args.wifiDevice)
wifiInfo = WifiInformation()

# for i in range(0,10):
print ("Collecting data......")
while True:
    try:
        wifiInfo.update()
        info = wifiInfo.display()
        os.system('clear')
        print (info)
        sleep(2)
    except KeyboardInterrupt:
        print ("\n\nTschö!\n")
        exit(0)
        
