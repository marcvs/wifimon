#!/usr/bin/env python3
''' a wifi signal strength display '''

# vim: foldmethod=indent : tw=100
#
# This code is distributed under the MIT License
#
# pylint: disable=invalid-name, superfluous-parens
# pylint: disable=logging-not-lazy, logging-format-interpolation

import os
import sys
import logging
from time import sleep
# import threading
# import Queue
# from getch.getch import getch

from wifitop.parse_args import args
import wifitop.logsetup

from wifitop.wifiinformation import WifiInformation

logger = logging.getLogger(__name__)



if args.verbose:
    print ("device: %s" % args.wifiDevice)
wifiInfo = WifiInformation()

# for i in range(0,10):
print ("Collecting data......")
while True:
    info = ''
    try:
        wifiInfo.update_cells()
        wifiInfo.update_connected_cell()
        essids = wifiInfo.extract_essids()
        # info = wifiInfo.display()
        for essid in essids.values():
            info += essid.display()


        if not args.once:
            os.system('clear')

        print (info)
        print (wifiInfo.dupefinder())
            
        if args.once:
            sys.exit(0)
        sleep(0.5)
    except KeyboardInterrupt:
        print ("\n\nTschö!\n")
        sys.exit(0)
