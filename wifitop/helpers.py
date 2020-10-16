'''helper functions'''

# vim: foldmethod=indent : tw=100
#
# This code is distributed under the MIT License
#
# pylint: disable=invalid-name, superfluous-parens
# pylint: disable=logging-not-lazy, logging-format-interpolation

import logging
import fileinput
import re
import sys
import subprocess
import os
import json
from wifitop.parse_args import args

logger = logging.getLogger(__name__)

# conversion strings for crypt strings
crypto_filter = {}
crypto_filter ["IEEE 802.11i/WPA2 Version 1"] = "WPA2"
crypto_filter ["WPA Version 1"] =               "WPA1"
#crypto_filter [""] = "                     "

def jprint(jsondata, do_print=True):
    '''json printer'''
    retval = json.dumps(jsondata, sort_keys=True, indent=4, separators=(',', ': '))
    if do_print:
        print (retval)
        return ""
    return retval

def shellcall(commandline):
    '''call a shell command'''
    if args.verbose > 1:
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

def read_ethermap(ethersFile):
    '''Read ethermap'''
    try:
        ethermap = {}
        with fileinput.input(ethersFile) as lines:
            for line in lines:
                entries = re.split(' ', line)
                key = entries[0]
                entries[-1] = entries[-1].rstrip("\n")
                ethermap[key] = ' '.join(entries[1:])
    except IOError as e:
        print("Error reading ethermap: " + str(e))
        sys.exit(1)
        return None
    return ethermap

def pretty_print_ether(mac):
    '''translate mac into known name from config file'''
    if args.prettyprintEthers:
        ethermap = read_ethermap(args.ethersFile)
        try:
            mac = ethermap[mac]
        except KeyError:
            pass
    return mac
