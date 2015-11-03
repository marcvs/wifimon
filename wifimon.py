#!/usr/bin/env python
# vim: set tw=120 

import argparse
import os
import subprocess
import re
from datetime import datetime
from time import sleep
from sys import stdout
import copy
import operator
from xtermcolor import colorize
from time import sleep
import threading
import Queue
from getch.getch import getch
import os
import fileinput

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
parser.add_argument('-cc', dest='col_crypto',	default=0x44bb44)
parser.add_argument('-ce', dest='col_essid',	default=0x00ff00)
parser.add_argument('-cm', dest='col_mac',		default=0x66ff66)
parser.add_argument('-ch', dest='col_ch',		default=0xffff22)
parser.add_argument('-cf', dest='col_fr',		default=0xffff99)
parser.add_argument('-cq', dest='col_qu',		default=0x22ffff)
parser.add_argument('-cl', dest='col_le',		default=0x99ffff)
parser.add_argument('-co', dest='col_mo',		default=0xff9999)
parser.add_argument('-ct', dest='col_meter',	default=0x00ff00)
parser.add_argument('-cs', dest='col_speed',	default=0x0000ff)
parser.add_argument('-ci', dest='col_hi',		default=0xff9999)
parser.add_argument('-up', dest='update_interval',	default=2)
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

# conversion strings for crypt strings
crypto_filter = {}
crypto_filter ["IEEE 802.11i/WPA2 Version 1"] = "WPA2"
crypto_filter ["WPA Version 1"] =				"WPA1"
#crypto_filter [""] = "						"

# Read ethermap
try:
	ethermap = {}
	for line in fileinput.input(args.ethersFile):
		entries = re.split('\s*', line)
		key = entries[0]
		ethermap[key] = ' '.join(entries[1:])
except Exception as e:
	print("Error: " + str(e))

#startupCwd = os.getcwd()
#os.chdir(args.basedir)

class wifiCell:
	def __init__(self):
		self.mac				= ""
		self.channel			= 0
		self.frequency			= 0
		self.quality			= ""
		self.encryption			= False
		self.encryption_type	= ""
		self.essid				= ""
		self.bitrates			= ""
		self.bitrate			= ""
		self.txpower			= ""
		self.mode				= ""
		self.last_seen			= ""
		self.crypto				= []
		self.authentication		= []
		self.group_cipher		= []
		self.pair_cipher		= []
		self.connected			= False

	def display(self, show_essid=True):
		multiplier = 1
		bg = 0x000000

		col_mac		= args.col_mac
		col_ch		= args.col_ch
		col_fr		= args.col_fr
		col_qu		= args.col_qu
		col_le		= args.col_le
		col_mo		= args.col_mo
		col_meter	= args.col_meter
		col_speed	= args.col_speed

		if self.connected:
			multiplier = 1
			col_mac		= args.col_hi
			col_ch		= args.col_hi
			col_fr		= args.col_hi
			col_qu		= args.col_hi
			col_le		= args.col_hi
			col_mo		= args.col_hi
			col_meter	= args.col_hi
			col_speed	= args.col_hi

		# preformatting: mac addresses:
		formatted_mac = self.mac
		if args.prettyprintEthers:
			try:
				formatted_mac = ethermap[self.mac]
			except:
				pass

		#stdout.write('	%s' %	colorize(				self.mac,			int(multiplier*col_mac), bg=bg))
		stdout.write('	%s' %	colorize("{:<17}".format(formatted_mac[:17]),	int(multiplier*col_mac), bg=bg))
		stdout.write(' %s'	%	colorize("{:<3}".format(self.channel),		int(multiplier*col_ch), bg=bg))
		stdout.write(' (%s)' %	colorize("{:<5}".format(self.frequency),	int(multiplier*col_fr), bg=bg))
		stdout.write(' %s'	%	colorize("{:<5}".format(self.quality),		int(multiplier*col_qu), bg=bg))
		stdout.write(' (%s)' %	colorize("{:<3}".format(self.level),		int(multiplier*col_le), bg=bg))
		stdout.write(' %s'	%	colorize("{:<7}".format(self.mode),			int(multiplier*col_mo), bg=bg))
		#stdout.write(' (%5s)' % self.frequency )
		#stdout.write(' (%3s)' % self.level)
		if show_essid:
				stdout.write(' '  + self.essid)

		# meter
		stdout.write(colorize(" [", col_meter, bg=bg))
		i=0
		for i in range ((int (self.quality.split("/")[0]))/5):
			stdout.write(colorize("*", col_meter, bg=bg))
		if i==0:
			for i in range (int(70/5)):
				stdout.write(colorize("-", col_meter, bg=bg))
		else:
			for x in range (i+1,int(70/5)):
				stdout.write(colorize("'", col_meter, bg=bg))
		stdout.write(colorize("]", col_meter, bg=bg))

		# speed
		if self.bitrate != "" or self.txpower != "":
			stdout.write(colorize(" [", col_speed, bg=bg))
			if self.bitrate != "":
				stdout.write(colorize("{:} Mb/s  ".format(self.bitrate), col_speed, bg=bg))
			if self.txpower != "":
				stdout.write(colorize("{:>2} dBm".format(self.txpower), col_speed, bg=bg))


			stdout.write(colorize("]", col_speed, bg=bg))


		stdout.write('\n')
		stdout.flush()
#, self.last_seen 
	def display_long(self, show_essid=True):
		print ('''		  %s:
		 Channel:	 %s (%s GHz)
		 Quality:	 %s (%s dBm)
		 Encryption: %s''' % (self.mac, self.channel, self.frequency,
							self.quality, self.level, self.encryption))
		if show_essid:
			print ('''		 ESSID:		 %s''' % self.essid)
		print ('''		 Mode:		 %s''' % self.mode)
		print ('''		 Last Seen:  %s''' % self.last_seen )

class wifiEssid:
	def __init__(self):
		self.cells		= {}
		self.encryption = False
		self.crypto		= ""

	def display(self):
		# preformatting: Crypto
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

		stdout.write ("%s %s\n" % (colorize("%s" % self.essid, args.col_essid),\
								encryption_string.rstrip()))
		#for cell in self.cells.values():
			#cell.display(show_essid=False)
			##cell.display(show_essid=True)
		# Sorted output:
		#for cell in sorted (self.cells.items(), key=self.cells.get):
			##print (str(cell))
			#self.cells[cell[0]].display(show_essid=False)
		def sorter(x, y):
			xq = int(x.quality.split("/")[0])
			yq = int(y.quality.split("/")[0])
			if xq < yq:
				return 1
			if xq > yq:
				return -1
			return 0
		for cell in sorted (self.cells.items(), key=operator.itemgetter(1), cmp=sorter):
			#print (str(cell))
			self.cells[cell[0]].display(show_essid=False)

	def add_cell(self, cell):
		#if not exists(self.cells[cell.mac]):
		#if hasattr(self.cells, cell.mac):
		#if self.cells[cell.mac] in locals():
		if not cell.mac in self.cells.iterkeys():
			self.cells[cell.mac] = copy.deepcopy(cell)
			self.encryption		 = self.cells[cell.mac].encryption
			self.crypto			 = self.cells[cell.mac].crypto
			self.authentication  = self.cells[cell.mac].authentication
			self.group_cipher	 = self.cells[cell.mac].group_cipher
			self.pair_cipher	 = self.cells[cell.mac].pair_cipher
		else: # if the cell already exists we don't copy the crypto settings
			self.cells[cell.mac] = copy.deepcopy(cell)

class WifiInformation:
	#cells	= {}
	essids = {}

	def shellcall(self, commandline):
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
		# Gather input for the currently connected AP
		current_cell = wifiCell()
		try:
			(retval, iwcfgOutput, errors) = self.shellcall("iwconfig "+args.wifiDevice)
		except Exception, e:
			print (str(e))


		#(retval, iwlistOutput, errors) = self.shellcall("ifconfig "+args.wifiDevice+" up")
		if args.inputFromFile == None:
			(retval, iwlistOutput, errors) = self.shellcall("iwlist "+args.wifiDevice+" scan")
		else:
			with open(args.inputFromFile, 'r') as fd:
				iwlistOutput = fd.read()

		status_cell = ""
		status_last_cell = ""
		status_essid = ""
		new_cell = wifiCell()
		for line in iwlistOutput.split("\n"):# {{{
			#print line
			line = line.rstrip().lstrip()
			if re.match("Cell", line):
				f = line.split(" ")
				(cell, number, dash, label, mac) = (f[0], f[1], f[2], f[3], f[4])
				status_last_cell = status_cell
				status_cell = mac
				# if there was a previous cell, that one is finished now
				# and we can add this one to it's coresponding essid
				if status_cell != status_last_cell and status_last_cell != "":
					if not self.essids.has_key (status_essid):
						self.essids[status_essid] = wifiEssid()
					self.essids[status_essid].essid = status_essid
					self.essids[status_essid].add_cell(new_cell)
					#self.essids[status_essid].display()
					#print ("\n")

				new_cell.__init__()
				new_cell.mac = mac
				new_cell.last_seen = datetime.now()


			if re.match("Channel", line):
				new_cell.channel	= line.split(":")[1]

			if re.match("Frequency", line):
				new_cell.frequency	= line.split(":")[1].split(" ")[0]

			if re.match("Quality", line):
				new_cell.quality	= line.split("=")[1].split(" ")[0]

			if re.match("Quality", line):
				new_cell.level		= line.split(" ")[3].split("=")[1]

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
				new_cell.mode				= line.split(":")[1]

			if not re.match("IE: Unknown", line):
				if re.match("IE: ", line):
					new_cell.crypto.append(line.split(":")[1].lstrip())

			if re.match("Group Cipher", line):
				new_cell.group_cipher.append(line.split(" : ")[1].lstrip())

			if re.match("Pairwise Ciphers", line):
				new_cell.pair_cipher.append(line.split(" : ")[1].lstrip())

			if re.match("Authentication Suites", line):
				new_cell.authentication.append(line.split(" : ")[1].lstrip())# }}}


		# at the end of the for loop we also have to add the last cell
		if status_cell != status_last_cell:
			if not self.essids.has_key (status_essid):
				self.essids[status_essid] = wifiEssid()
			self.essids[status_essid].essid = status_essid
			self.essids[status_essid].add_cell(new_cell)

		# Gather input for the currently connected AP
		try:

			current_cell.__init__()
			for line in iwcfgOutput.split("\n"):
				#print line
				line = line.rstrip().lstrip()
				if re.match(args.wifiDevice, line):
					current_cell.essid		= line.split(":")[1].replace('"','')


				if re.match("Mode:", line):
					#current_cell.mode		= line.split(":")[1].split(" ")[0]
					current_cell.frequency	= line.split(":")[2].split(" ")[0]
					current_cell.mac		= line.split(" ")[7]
				if re.match("Link Quality", line):
					current_cell.quality	= line.split("=")[1].split(" ")[0]
					current_cell.level		= line.split("=")[2].split(" ")[0]
				if re.match("Bit Rate", line):
					current_cell.bitrate	= line.split("=")[1].split(" ")[0]
					current_cell.txpower	= line.split("=")[2].split(" ")[0]
				current_cell.last_seen		= datetime.now()
			current_cell.channel			= self.essids[current_cell.essid].cells[current_cell.mac].channel
			current_cell.connected = True
			self.essids[current_cell.essid].add_cell(current_cell)

			#stdout.write(str(current_cell.bitrate))
			#current_cell.display(show_essid=False)
		except Exception, e:
			print (str(e))




	def display(self):
		#print ("Cells")
		#for mac in self.cells.iterkeys():
			#self.cells[mac].display()

		for essid in self.essids.iterkeys():
			self.essids[essid].display()

class InputThread(threading.Thread):#{{{
	def __init__(self, queue):
		threading.Thread.__init__(self)
		self.queue = queue
		self.name = "Keyboard Input Thread"
	def run(self):
		while True:
			kbd_chr = getch()
			try:
				kbd_val = ord(kbd_chr)
			except:
				pass
			self.queue.put((kbd_chr, kbd_val))#}}}

if args.verbose: print ("device: %s" % args.wifiDevice)
wifiInfo = WifiInformation()

#
# initialize input thread
queue		= Queue.Queue()
t = InputThread(queue)
t.setDaemon(True)
#t.start()

wifiInfo.update()
wifiInfo.display()
#while True:
	#wifiInfo.update()
	#wifiInfo.display()
	## Scan input keys
	#sleep(args.update_interval)
	#(kbd_chr, kbd_val) = queue.get()
	#if kbd_val == 61 or kbd_val == 70: # esc or q
		#exit(0)

