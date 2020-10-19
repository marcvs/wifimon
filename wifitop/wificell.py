'''information about one cell'''

# vim: foldmethod=indent : tw=100
#
# This code is distributed under the MIT License
#
# pylint: disable=invalid-name, superfluous-parens
# pylint: disable=logging-not-lazy, logging-format-interpolation

import logging
from datetime import datetime
from xtermcolor import colorize

from wifitop.parse_args import args
from wifitop.helpers import pretty_print_ether
import wifitop.logsetup
import wifitop.alchemy as alchemy
from sqlalchemy import Column, Integer, String, Boolean, JSON


logger = logging.getLogger(__name__)

class WifiCell(alchemy.Base):
    # pylint: disable=too-many-instance-attributes
    '''encapsulate wifi cell information'''
    __tablename__      = "wificell"
    # id                 = Column(Integer, primary_key=True)
    # id                 = Column(Integer)
    mac                = Column(String, primary_key=True)
    channel            = Column(Integer)
    frequency          = Column(Integer)
    quality            = Column(Integer)
    level              = Column(Integer)
    encryption         = Column(Boolean)
    encryption_type    = Column(String)
    essid              = Column(String)
    bitrates           = Column(String)
    bitrate            = Column(String)
    txpower            = Column(String)
    mode               = Column(String)
    last_seen          = Column(String)
    crypto             = Column(JSON)
    authentication     = Column(JSON)
    group_cipher       = Column(JSON)
    pair_cipher        = Column(JSON)
    connected          = Column(Boolean)
    def __init__(self):
        self.mac                = ""
        self.channel            = 0
        self.frequency          = 0
        self.quality            = 0
        self.level              = 0
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
        # pylint: disable=too-many-locals
        '''pretty print'''
        output = ""
        age = (datetime.now() - self.last_seen).total_seconds()

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
        self.mac = pretty_print_ether(self.mac)

        output += '  %s' %  colorize("{:<17}".format(self.mac[:17]), col_mac, bg=bg)
        if age > 40:
            output += colorize (F" --------------------------------[ expired: {age:2.0f}s ] \n",
                col_last, bg=bg)
            return output

        output += ' %s'  %  colorize("{:<3}".format(self.channel),   col_ch, bg=bg)
        output += ' (%s)' % colorize("{:<5}".format(self.frequency), col_fr, bg=bg)
        output += ' %s'  %  colorize("{:<5}".format(self.quality),   col_qu, bg=bg)
        output += ' (%s)' % colorize("{:<3}".format(self.level),     col_le, bg=bg)
        output += ' %s'  %  colorize("{:<7}".format(self.mode),      col_mo, bg=bg)
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
            for _ in range (i+1,int(70/5)):
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
            output += colorize(F" age: {age:2.0f}s", col_last, bg=bg)

        output += '\n'

        return output

    def display_long(self, show_essid=True):
        '''pretty print'''
        output = ""
        # for (k,v) in crypto_filter.items():
        # encryption_string = encryption_string.replace(k,v)

        output += '''        %s:
        Channel:    %s (%s GHz)
        Quality:    %s (%s dBm)
        Encryption: %s''' % (self.mac, self.channel, self.frequency,
                 self.quality, self.level, self.encryption)
        if show_essid:
            output += '''       ESSID:      %s''' % self.essid
        output += '''       Mode:       %s''' % self.mode
        output += '''       Last Seen:  %s''' % self.last_seen 
        return output
alchemy.Base.metadata.create_all(alchemy.engine)
