"""Commandline parameter handling"""

# vim: foldmethod=indent
# vim: tw=100 foldmethod=marker
#
# This code is distributed under the MIT License
#
# pylint: disable=invalid-name, superfluous-parens
# pylint: disable=logging-not-lazy, logging-format-interpolation

import argparse
import os


def parseOptions():
    """Parse the commandline options"""
    parser = argparse.ArgumentParser(description="google-doc-watcher")
    parser.add_argument("--verbose", "-v", dest="verbose", action="count", default=0)
    parser.add_argument("--once", action="count", default=0)
    parser.add_argument("--debug", "-d", dest="debug", action="count", default=0)
    parser.add_argument("--logfile", default="log_file", help="logfile")
    parser.add_argument(
        "--loglevel", default=os.environ.get("LOG", "WARNING").upper(), help="Debugging Level"
    )
    parser.add_argument("--interface", "-i", dest="wifiDevice", default="wlan0")
    parser.add_argument("-n", dest="prettyprintEthers", default=True, action="store_false")
    parser.add_argument(
        "--ethers", "-e", dest="ethersFile", default=os.getenv("HOME") + "/.config/wifimon/ethers"
    )
    parser.add_argument(
        "--oui", "-o", dest="ouiFile", default=os.getenv("HOME") + "/.config/wifimon/oui.processed"
    )
    parser.add_argument("--fake-input", default=None)
    parser.add_argument("--fake-input-iw", default=None)
    parser.add_argument("-cc", dest="col_crypto", default=0x44BB44)
    parser.add_argument("-ce", dest="col_essid", default=0x00FF00)
    parser.add_argument("-cm", dest="col_mac", default=0x66FF66)
    parser.add_argument("-ch", dest="col_ch", default=0xFFFF22)
    parser.add_argument("-cf", dest="col_fr", default=0xFFFF99)
    parser.add_argument("-cq", dest="col_qu", default=0x22FFFF)
    parser.add_argument("-cl", dest="col_le", default=0x99FFFF)
    parser.add_argument("-co", dest="col_mo", default=0xFF9999)
    parser.add_argument("-ct", dest="col_meter", default=0x00FF00)
    parser.add_argument("-cs", dest="col_speed", default=0x0000FF)
    parser.add_argument("-ca", dest="col_last", default=0x555555)
    parser.add_argument("-ci", dest="col_hi", default=0xFF9999)
    parser.add_argument("-up", dest="update_interval", default=2)
    args = parser.parse_args()
    return args


# reparse args on import
args = parseOptions()
