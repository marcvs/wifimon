"""informatin about many essids"""

# vim: foldmethod=indent : tw=100
#
# This code is distributed under the MIT License
#
# pylint: disable=invalid-name, superfluous-parens
# pylint: disable=logging-not-lazy, logging-format-interpolation, logging-fstring-interpolation

import logging
import re
import os.path
from datetime import datetime

from wifitop.parse_args import args
from wifitop.helpers import shellcall, pretty_print_ether
from wifitop.wifiessid import WifiEssid
from wifitop.wificell import WifiCell
import wifitop.logsetup

logger = logging.getLogger(__name__)


class WifiInformation:
    """collect and updates wifi essids"""

    def __init__(self):
        # self.essids = {} # dict: maps string to WifiEssid
        self.cells = {}  # dict: maps mac to WifiCell
        self.counter = 0

    def update_cells(self):
        """update cells from iwclist"""
        if args.fake_input:
            from time import sleep

            filename = args.fake_input + str(self.counter)
            if not os.path.isfile(filename):
                self.counter = 0
                filename = args.fake_input + str(self.counter)
            file = open(filename, mode="r")
            iwlistOutput = file.read()
            file.close()
            self.counter += 1
            logger.debug(f"loaded from {filename}")
            # sleep (3)
        else:
            (_, iwlistOutput, _) = shellcall("ifconfig " + args.wifiDevice + " up")
            (_, iwlistOutput, _) = shellcall("iwlist " + args.wifiDevice + " scan")

        mac = ""
        last_mac = ""
        cellinfo = {}
        cellinfo["crypto"] = []
        cellinfo["group_cipher"] = []
        cellinfo["pair_cipher"] = []
        cellinfo["authentication"] = []
        for line in iwlistOutput.split("\n"):
            if args.verbose > 1:
                # print (F" len crypto: {len(cellinfo['crypto'])}")
                print(line)
            line = line.rstrip().lstrip()
            if re.match("Cell", line):  # a new cell is starting
                f = line.split(" ")
                (cell, number, dash, _, next_mac) = (f[0], f[1], f[2], f[3], f[4])
                # cycle the info:
                last_mac = mac
                mac = next_mac
                # if there was a previous cell, that one is finished now
                # and we can add that one to it's coresponding essid
                if last_mac not in (mac, ""):
                    # Then either update or store:
                    if mac not in self.cells.keys():
                        self.cells[mac] = WifiCell(cellinfo)
                    else:
                        self.cells[mac].update(cellinfo)
                    # And reset some values:
                    cellinfo["crypto"] = []
                    cellinfo["group_cipher"] = []
                    cellinfo["pair_cipher"] = []
                    cellinfo["authentication"] = []

                # prepare for the next cell
                # new_cell = WifiCell()
                cellinfo["mac"] = mac
                # new_cell.last_seen = datetime.now()
                cellinfo["last_seen"] = datetime.now()
                logger.debug(F"setting last seen for {cellinfo['mac']}: {datetime.now()}")

            if re.match("Channel", line):
                cellinfo["channel"] = line.split(":")[1]

            if re.match("Frequency", line):
                cellinfo["frequency"] = line.split(":")[1].split(" ")[0]

            if re.match("Quality", line):
                cellinfo["quality"] = int(line.split("=")[1].split(" ")[0].split("/")[0])
                cellinfo["level"] = int(line.split(" ")[3].split("=")[1])

            if re.match("Encryption", line):
                if re.search("on", line.split(":")[1]):
                    cellinfo["encryption"] = True
                else:
                    cellinfo["encryption"] = False

            if re.match("ESSID", line):
                cellinfo["essid"] = line.split(":")[1].replace('"', "")
                # status_essid = line.split(":")[1].replace('"','')
                # new_cell.essid = status_essid

            # if re.match("Bit Rates", line): # too complicated to parse for now
            # new_cell.channel = line.split(":")[1].split(" ")[0]

            if re.match("Mode", line):
                cellinfo["mode"] = line.split(":")[1]

            if not re.match("IE: Unknown", line):
                if re.match("IE: ", line):
                    cellinfo["crypto"].append(line.split(":")[1].lstrip())

            if re.match("Group Cipher", line):
                cellinfo["group_cipher"].append(line.split(" : ")[1].lstrip())

            if re.match("Pairwise Ciphers", line):
                cellinfo["pair_cipher"].append(line.split(" : ")[1].lstrip())

            if re.match("Authentication Suites", line):
                cellinfo["authentication"].append(line.split(" : ")[1].lstrip())

        # if args.verbose:
        #     print (F"   wifiInformantion self: {dir(self)}")
        #     print (F"   Updater Loop done, gathered {len(self.essids)}")
        #     print (F"   Updater Loop done, gathered {self.essids}")

        # at the end of the for loop we also have to add the last cell
        if mac != last_mac:
            if mac not in self.cells.keys():
                self.cells[mac] = WifiCell(cellinfo)
            # FIXME: In case there is only one AP it's never updated.
            #   => Text it with two APs
            # else:
            #     self.cells[mac] = WifiCell(cellinfo)
            # if status_essid not in self.essids.keys():
            #     self.essids[status_essid]   = WifiEssid()
            # self.essids[status_essid].essid = status_essid
            # self.essids[status_essid].add_cell(new_cell)

        # Gather input for the currently connected AP

    def update_connected_cell(self):
        """Update information from currently connected cell"""
        cellinfo = {}
        # cellinfo["crypto"]         = []
        # cellinfo["group_cipher"]   = []
        # cellinfo["pair_cipher"]    = []
        # cellinfo["authentication"] = []
        iwcfgOutput = str()
        if args.fake_input_iw:
            file = open(args.fake_input_iw, mode="r")
            iwcfgOutput = file.read()
            file.close()
        else:
            try:
                (_, iwcfgOutput, _) = shellcall("iwconfig " + args.wifiDevice)
            except Exception as e:
                print("Exception in shellcall")
                print(str(e))
        try:
            # current_cell.__init__()
            mac = str()
            for line in iwcfgOutput.split("\n"):
                # print(line)
                line = line.rstrip().lstrip()
                if re.match(args.wifiDevice, line):
                    cellinfo["essid"] = line.split(":")[1].replace('"', "")

                if re.match("Mode:", line):
                    # current_cell.mode             = line.split(":")[1].split(" ")[0]
                    cellinfo["frequency"] = line.split(":")[2].split(" ")[0]
                    mac = line.split(" ")[7]
                    cellinfo["mac"] = mac
                if re.match("Link Quality", line):
                    cellinfo["quality"] = int(line.split("=")[1].split(" ")[0].split("/")[0])
                    cellinfo["level"] = int(line.split("=")[2].split(" ")[0])
                if re.match("Bit Rate", line):
                    cellinfo["bitrate"] = line.split("=")[1].split(" ")[0]
                    cellinfo["txpower"] = line.split("=")[2].split(" ")[0]
                cellinfo["last_seen"] = datetime.now()
            # cellinfo["channel"]                    = self.essids[current_cell.essid].cells[current_cell.mac].channel
            cellinfo["connected"] = True
            # update the cell with cellinfo:
            if mac not in self.cells.keys():
                self.cells[mac] = WifiCell(cellinfo)
            else:
                self.cells[mac].update(cellinfo)

        except KeyError as e:
            print(f"KeyError: {e}")
            raise

    def extract_essids(self):
        """return a dictionary of essids"""
        macs = []
        essids = {}
        for cell in self.cells.values():
            if cell.essid not in essids.keys():
                essids[cell.essid] = WifiEssid(cell.essid)
                # logger.debug(F"added essid: {cell.essid}")
            essids[cell.essid].add_cell(cell)
            # Dupefinder:
            mac = cell.mac
            if mac in macs:
                # logger.info(F"mac: {mac}")
                pretty_mac = pretty_print_ether(mac)
                other_cell = self.cells[mac]
                other_pretty_mac = pretty_print_ether(other_cell.mac)
                other_cid = other_cell.cid
                # logger.info( F"  ExtractEssids: Duplicate found: {self.cells[mac].cid}: {mac}")
                # logger.info( F"Dupe: {self.cells[mac].cid}-{pretty_mac:10} -- {other_pretty_mac:10}-{other_cid}")
                logger.info(
                    f"Dupe: {self.cells[mac].cid}-{mac:10} -- {other_cell.mac:10}-{other_cid}"
                )
                NL = "\n"
                logger.info(f"one:   {cell.display().rstrip(NL)}")
                logger.info(f"other: {self.cells[mac].display().rstrip(NL)}")
            macs.append(mac)
            # logger.debug(F"len of macs{len(macs)}")

        counter = 0
        for e in essids.values():
            for c in e.cells.values():
                counter += 1
        # logger.info(F"  ExtractEssids: essids: {counter}")

        return (essids, counter)

    def dupefinder(self):
        """Find duplicate entries"""
        macs = []
        for mac in self.cells.keys():
            if mac in macs:
                logger.info(f"Duplicate found: {self.cells[mac].cid}: {mac}")
            macs.append(mac)
        return len(self.cells)

    def display(self):
        """pretty print"""
        output = ""
        for cell in self.cells.values():
            output += cell.display(show_essid=False)
        # for essid in self.essids.keys():
        #     output += self.essids[essid].display()
        return output
