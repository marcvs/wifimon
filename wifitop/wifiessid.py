'''informatin about many essids'''

# vim: foldmethod=indent : tw=100
#
# This code is distributed under the MIT License
#
# pylint: disable=invalid-name, superfluous-parens
# pylint: disable=logging-not-lazy, logging-format-interpolation

import logging
import copy
import operator
from xtermcolor import colorize

from wifitop.parse_args import args
from wifitop.wificell import WifiCell
from wifitop.helpers import crypto_filter
import wifitop.logsetup
import wifitop.alchemy as alchemy

logger = logging.getLogger(__name__)

class WifiEssid:
    '''collect wifi cells with the same essid'''
    def __init__(self):
        self.cells      = {} # dict: maps mac to cell
        self.encryption = False
        self.crypto     = ""

    def display(self):
        '''pretty print'''
        # preformatting: Crypto
        output = ""
        temp = []
        # print (F" Crypto: {self.crypto}")
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
        # alchemy.session.add(cell)
        # print(alchemy.session.dirty)
        # alchemy.session.commit()
