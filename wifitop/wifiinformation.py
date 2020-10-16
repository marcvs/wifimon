'''informatin about many essids'''

# vim: foldmethod=indent : tw=100
#
# This code is distributed under the MIT License
#
# pylint: disable=invalid-name, superfluous-parens
# pylint: disable=logging-not-lazy, logging-format-interpolation

import logging
import re
from datetime import datetime
from pprint import pprint

from wifitop.parse_args import args
from wifitop.helpers import shellcall, jprint
from wifitop.wifiessid import WifiEssid
from wifitop.wifiessid import WifiCell
import wifitop.logsetup

logger = logging.getLogger(__name__)

class WifiInformation:
    '''collect and updates wifi essids'''
    def __init__(self):
        self.essids = {} # dict: maps string to WifiEssid

    def update(self):
        '''Gather input for the currently connected AP'''
        current_cell = WifiCell()
        try:
            (_, iwcfgOutput, _) = shellcall("iwconfig "+args.wifiDevice)
        except Exception as e:
            print (str(e))

        (_, iwlistOutput, _) = shellcall("ifconfig "+args.wifiDevice+" up")
        (_, iwlistOutput, _) = shellcall("iwlist "+args.wifiDevice+" scan")

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
                if status_last_cell not in (status_cell, ""):
                    if status_essid not in self.essids.keys():
                        # Create new essid if we didn't have the old one
                        self.essids[status_essid] = WifiEssid()
                    # store the cell
                    self.essids[status_essid].essid = status_essid
                    self.essids[status_essid].add_cell(new_cell)
                # prepare for the next cell
                new_cell = WifiCell()
                new_cell.mac = mac
                new_cell.last_seen = datetime.now()

            if re.match("Channel", line):
                new_cell.channel    = line.split(":")[1]

            if re.match("Frequency", line):
                new_cell.frequency  = line.split(":")[1].split(" ")[0]

            if re.match("Quality", line):
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
            if status_essid not in self.essids.keys():
                self.essids[status_essid]   = WifiEssid()
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
            # replace current cell with infromation of connection
            self.essids[current_cell.essid].add_cell(current_cell)

            #stdout.write(str(current_cell.bitrate))
            #current_cell.display(show_essid=False)
            # pprint (self.essids)
        except Exception as e:
            print (str(e))
       
    def display(self):
        '''pretty print'''
        output = ""
        for essid in self.essids.keys():
            output += self.essids[essid].display()
        return output

