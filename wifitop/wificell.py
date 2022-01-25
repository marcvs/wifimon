"""information about one cell"""

# vim: foldmethod=indent : tw=100
#
# This code is distributed under the MIT License
#
# pylint: disable=invalid-name, superfluous-parens
# pylint: disable=logging-not-lazy, logging-format-interpolation

from datetime import datetime
from itertools import count
import logging
from typing import Union

from sqlalchemy import Boolean, Column, Integer, JSON, String
from xtermcolor import colorize

import wifitop.alchemy as alchemy
from wifitop.helpers import pretty_print_ether
from wifitop.parse_args import args


logger = logging.getLogger(__name__)


class WifiCell(alchemy.Base):
    # pylint: disable=too-many-instance-attributes
    """encapsulate wifi cell information"""
    __tablename__ = "wificell"
    # id                 = Column(Integer, primary_key=True)
    # id                 = Column(Integer)
    _ids = count(0)
    mac = Column(String, primary_key=True)
    channel = Column(Integer)
    frequency = Column(Integer)
    quality = Column(Integer)
    level = Column(Integer)
    encryption = Column(Boolean)
    # encryption_type    = Column(String)
    essid = Column(String)
    bitrates = Column(String)
    bitrate = Column(String)
    txpower = Column(String)
    mode = Column(String)
    last_seen = Column(String)
    crypto = Column(JSON)
    authentication = Column(JSON)
    group_cipher = Column(JSON)
    pair_cipher = Column(JSON)
    connected = Column(Boolean)

    def __init__(self, cellinfo=None):
        self.cid = next(self._ids)
        if cellinfo is not None:
            self.update(cellinfo)

    def update(self, cellinfo):
        """Update the cell"""
        try:
            self.mac = cellinfo["mac"]
        except KeyError:
            raise
        try:
            self.channel = cellinfo["channel"]
        except KeyError:
            self.channel = 0
        try:
            self.frequency = cellinfo["frequency"]
        except KeyError:
            self.frequency = 0
        try:
            self.quality = cellinfo["quality"]
        except KeyError:
            self.quality = 0
        try:
            self.level = cellinfo["level"]
        except KeyError:
            self.level = 0
        try:
            self.encryption = cellinfo["encryption"]
        except KeyError:
            self.encryption = False
        try:
            self.encryption_type = cellinfo["encryption_type"]
        except KeyError:
            self.encryption_type = ""
        try:
            self.essid = cellinfo["essid"]
        except KeyError:
            raise
        try:
            self.bitrates = cellinfo["bitrates"]
        except KeyError:
            self.bitrates = ""
        try:
            self.bitrate = cellinfo["bitrate"]
        except KeyError:
            self.bitrate = ""
        try:
            self.txpower = cellinfo["txpower"]
        except KeyError:
            self.txpower = ""
        try:
            self.mode = cellinfo["mode"]
        except KeyError:
            self.mode = ""
        try:
            self.last_seen = cellinfo["last_seen"]
        except KeyError:
            self.last_seen = 0
        try:
            self.crypto = cellinfo["crypto"]
        except KeyError:
            self.crypto = []
        try:
            self.authentication = cellinfo["authentication"]
        except KeyError:
            self.authentication = []
        try:
            self.group_cipher = cellinfo["group_cipher"]
        except KeyError:
            self.group_cipher = []
        try:
            self.pair_cipher = cellinfo["pair_cipher"]
        except KeyError:
            self.pair_cipher = []
        try:
            self.connected = cellinfo["connected"]
        except KeyError:
            self.connected = False

    def display(self, show_essid=True):
        # pylint: disable=too-many-locals
        """pretty print"""
        output = ""

        def get_seconds(t: Union[float, int, datetime]) -> float:
            if isinstance(t, datetime):
                return (t - datetime(1970, 1, 1)).total_seconds()
            return float(t)

        last_seen = get_seconds(self.last_seen)
        age = get_seconds(datetime.now()) - get_seconds(last_seen)

        if age > 60:
            return ""

        bg = 0x000000
        col_mac = args.col_mac
        col_ch = args.col_ch
        col_fr = args.col_fr
        col_qu = args.col_qu
        col_le = args.col_le
        col_mo = args.col_mo
        col_meter = args.col_meter
        col_speed = args.col_speed
        col_last = args.col_last

        # print (F" connected: {self.connected}")

        if age > 20:
            col_mac = 0x118811
            col_ch = 0xAAAA22
            col_fr = 0xAAAA99
            col_qu = 0x22AAAA
            col_le = 0x66AAAA
            col_mo = 0xAA9999
            col_meter = 0x008800
            col_speed = 0x000088
            col_last = 0x555555

        if self.connected:
            col_mac = args.col_hi
            col_ch = args.col_hi
            col_fr = args.col_hi
            col_qu = args.col_hi
            col_le = args.col_hi
            col_mo = args.col_hi
            col_meter = args.col_hi
            col_speed = args.col_hi
            col_last = args.col_hi

        # preformatting: mac addresses:
        pretty_mac = pretty_print_ether(self.mac)

        output += f"{self.cid:2} - "
        output += "  %s" % colorize("{:<17}".format(pretty_mac[:17]), col_mac, bg=bg)
        if age > 40:
            output += colorize(
                f" --------------------------------[ expired: {age:2.0f}s ] \n", col_last, bg=bg
            )
            return output

        if self.channel != 0:
            output += " %s" % colorize("{:<3}".format(self.channel), col_ch, bg=bg)
        else:
            output += " %s" % "   "
        output += " (%s)" % colorize("{:<5}".format(self.frequency), col_fr, bg=bg)
        output += " %s" % colorize("{:<5}".format(self.quality), col_qu, bg=bg)
        output += " (%s)" % colorize("{:<3}".format(self.level), col_le, bg=bg)
        output += " %s" % colorize("{:<7}".format(self.mode), col_mo, bg=bg)
        # output += ' (%5s)' % self.frequency )
        # output += ' (%3s)' % self.level)
        if show_essid:
            output += " " + self.essid

        # meter
        output += colorize(" [", col_meter, bg=bg)
        i = 0
        for i in range(0, int(self.quality / 5)):
            output += colorize("*", col_meter, bg=bg)
        if i == 0:
            for i in range(int(70 / 5)):
                output += colorize("-", col_meter, bg=bg)
        else:
            for _ in range(i + 1, int(70 / 5)):
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
        if age > 10:
            output += colorize(f" age: {age:2.0f}s", col_last, bg=bg)

        output += "\n"

        return output

    def display_long(self, show_essid=True):
        """pretty print"""
        output = ""
        # for (k,v) in crypto_filter.items():
        # encryption_string = encryption_string.replace(k,v)

        pretty_mac = pretty_print_ether(self.mac)

        output += """        %s:
        Channel:    %s (%s GHz)
        Quality:    %s (%s dBm)
        Encryption: %s""" % (
            pretty_mac,
            self.channel,
            self.frequency,
            self.quality,
            self.level,
            self.encryption,
        )
        if show_essid:
            output += """       ESSID:      %s""" % self.essid
        output += """       Mode:       %s""" % self.mode
        output += """       Last Seen:  %s""" % self.last_seen
        return output


alchemy.Base.metadata.create_all(alchemy.engine)
