# File: jtemp.py
# Author: Tyler Jordan
# Modified: 8/28/2015
# Purpose: Assist CBP engineers with Juniper configuration tasks

import sys,fileinput,code,re,csv
import utility
import math
import pprint
import re

from utility import *
from storage import *

from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from lxml import etree
from getpass import getpass

# Global Variables
csv_path = '.\\csv\\'
template_path = '.\\template\\'

pp = pprint.PrettyPrinter(indent=2)

wan_router = {}
lan_router = {}
link_map = {}

# Display single chassis systems and their components. Side can be "Front", "Rear", or "Both".
def displayChassisHardware(hostname, viewside='Both'):
	if lan_router.has_key(hostname):
		# Get the hostname chassis type, determine if single or VC
		chassis_mod = lan_router[hostname]['chassis_mod']
		# Display Hostname
		print "Hostname: " + hostname
		# Virtual Chassis Views
		if chassis_mod == 'Virtual_Chassis':
			if viewside == 'Front' or viewside == 'Both':
				print "Side: Front"
				for fpc in lan_router[hostname]['interfaces']['physical'].keys():
					chassis_mod = lan_router[hostname]['interfaces']['physical'][fpc]['fpc_mod']
					chassisStackView(hostname, fpc, chassis_mod, 'Front')
			if viewside == 'Rear' or viewside == 'Both':
				print "Side: Rear"
				for fpc in lan_router[hostname]['interfaces']['physical'].keys():
					chassis_mod = lan_router[hostname]['interfaces']['physical'][fpc]['fpc_mod']
					chassisStackView(hostname, fpc, chassis_mod, 'Rear')		
		# Modular Chassis Views
		elif chassis_mod == 'EX6210':
			chassis_side = "Front"
			print "Side: Front"
			chassisModularView(hostname, chassis_mod, chassis_side)
		# Stackable Chassis Views
		else:
			fpc = 0
			if viewside == 'Front' or viewside == 'Both':
				print "Side: Front"
				chassisStackView(hostname, fpc, chassis_mod, "Front")
			if viewside == 'Rear' or viewside == 'Both':
				print "Side: Rear"
				chassisStackView(hostname, fpc, chassis_mod, "Rear")
	else:
		print "Hostname: " + hostname
		print "--- No Image Available ---"

# Assemble and print the contents of device(s)
def assembleViewPrint(chassisWidth, hostname, fpc, myList, onPorts, onLabels, onBorders):
	pic = 0
	if onPorts:
		#'ports', 's1', 'vb1', 's1' 'pic2', 's1', 'vb1', 's1', 'e', '0'
		#print myList
		for loopNum in range(1, 5):
			theLine = '|'
			myport = 0 # new addition
			for prtcmd in myList:			
				if loopNum == 1:
					# Matches a port
					if re.match(r'^\d{1,3}$', prtcmd) or re.match(r'^\d{1}p\d{1,3}$', prtcmd):
						theLine += "-----+"
					# A series of ports starting
					elif prtcmd == 'e':
						theLine += "+"
					# A space or spaces
					elif re.match(r'^s\d{1,3}$', prtcmd):
						#myspace = re.match(r'^s\d{1,3}$', prtcmd).group(0)	
						numlist = prtcmd.split('s')						
						theLine += " "*int(numlist[1])
					# A vertial border or borders
					elif re.match(r'^vb\d{1,3}$', prtcmd):
						numlist = prtcmd.split('b')
						theLine += "|"*int(numlist[1])		
				elif loopNum == 2:
					# Matches native chassis ports
					if re.match(r'^\d{1,3}$', prtcmd):
						myport = int(prtcmd)
						#print "FPC: " + str(fpc) + " PIC: " + str(pic) + " PORT: " + str(myport)
						# NEED TO REVERSE PRINTING EVENTUALLY
						if lan_router[hostname]['interfaces']['physical'][fpc][pic].has_key(myport):
							if lan_router[hostname]['interfaces']['physical'][fpc][pic][myport]['is_linked']:
								theLine += "X "
							else:
								theLine += "  "								
						else:
							print "ERROR - NO MATCH - NATIVE!"
							#pp.pprint(lan_router[hostname])
						# Determine if port is 1 digit or 2 digits so ports print correctly
						if myport > 9:
							theLine += str(myport) + " |"
						else:
							theLine += str(myport) + "  |"
					# Match expansion module ports
					elif re.match(r'^\d{1}p\d{1,3}$', prtcmd):
						numlist = prtcmd.split('p')
						modpic = int(numlist[0])
						myport = int(numlist[1])
						
						#print "FPC: " + str(fpc) + " PIC: " + str(pic) + " PORT: " + str(myport)
						# NEED TO REVERSE PRINTING EVENTUALLY
						if lan_router[hostname]['interfaces']['physical'][fpc][modpic].has_key(myport):
							if lan_router[hostname]['interfaces']['physical'][fpc][modpic][myport]['is_linked']:
								theLine += "X "
							else:
								theLine += "  "								
						else:
							print "ERROR - NO MATCH - EXPAN!"
						# Determine if port is 1 digit or 2 digits so ports print correctly
						if myport > 9:
							theLine += str(myport) + " |"
						else:
							theLine += str(myport) + "  |"					
					# A series of ports starting
					elif prtcmd == 'e':
						theLine += "|"
					# A space or spaces
					elif re.match(r'^s\d{1,3}$', prtcmd):
						numlist = prtcmd.split('s')						
						theLine += " "*int(numlist[1])
					# A vertial border or borders
					elif re.match(r'^vb\d{1,3}$', prtcmd):
						numlist = prtcmd.split('b')
						theLine += "|"*int(numlist[1])
					# Prevent this term from being printed
					elif re.match(r'bpic\d{1}$', prtcmd):
						# Do nothing
						pass
					# This should only be hit with the hostnamename
					elif prtcmd != 'end':
						theLine += prtcmd								
				elif loopNum == 3:
					# Matches native chassis ports
					#print "PRTCMD: " + prtcmd
					if re.match(r'^\d{1,3}$', prtcmd):
						myport = int(prtcmd)
						#print "FPC: " + str(fpc) + " PIC: " + str(pic) + " PORT: " + str(myport)
						# NEED TO REVERSE PRINTING EVENTUALLY
						if myport in lan_router[hostname]['interfaces']['physical'][fpc][pic]:
							if "access_mode" in lan_router[hostname]['interfaces']['physical'][fpc][pic][myport]:
								access_mode = lan_router[hostname]['interfaces']['physical'][fpc][pic][myport]['access_mode'] 
								theLine += access_mode + " "*(5 - (len(access_mode))) + "|"
							else:
								theLine += "     |"								
						else:
							print "ERROR - NO MATCH - NATIVE!"
							#pp.pprint(lan_router[hostname])
					# Match expansion module ports
					elif re.match(r'^\d{1}p\d{1,3}$', prtcmd):
						numlist = prtcmd.split('p')
						modpic = int(numlist[0])
						myport = int(numlist[1])
						#lan_router[hostname]['interfaces']['physical'][fpc][pic][myport]['access_mode'] = "VCP"
						#print "FPC: " + str(fpc) + " PIC: " + str(pic) + " PORT: " + str(myport)
						#print "Access Mode: " + lan_router[hostname]['interfaces']['physical'][fpc][pic][myport]['access_mode']
						#pp.pprint(lan_router[hostname]['interfaces']['physical'][fpc][modpic][myport])
						# NEED TO REVERSE PRINTING EVENTUALLY
						if myport in lan_router[hostname]['interfaces']['physical'][fpc][modpic]:
							#print "First IF..."
							if "access_mode" in lan_router[hostname]['interfaces']['physical'][fpc][modpic][myport]:
								#print "Second IF..."
								access_mode = lan_router[hostname]['interfaces']['physical'][fpc][modpic][myport]['access_mode'] 
								theLine += access_mode + " "*(5 - (len(access_mode))) + "|"
							else:
								theLine += "     |"							
						else:
							print "ERROR - NO MATCH - EXPAN!"
						#pp.pprint(lan_router[hostname]['interfaces']['physical'][fpc][modpic][myport])
					# A port
					#if re.match(r'^\d{1,3}$', prtcmd) or re.match(r'^\d{1}p\d{1,3}$', prtcmd):
					#	theLine += "     |"
					# A series of ports starting
					elif prtcmd == 'e':
						theLine += "|"
					# A space or spaces
					elif re.match(r'^s\d{1,3}$', prtcmd):
						numlist = prtcmd.split('s')						
						theLine += " "*int(numlist[1])
					# A vertial border or borders
					elif re.match(r'^vb\d{1,3}$', prtcmd):
						numlist = prtcmd.split('b')
						theLine += "|"*int(numlist[1])
				if loopNum == 4:
					# A port
					if re.match(r'^\d{1,3}$', prtcmd) or re.match(r'^\d{1}p\d{1,3}$', prtcmd):
						theLine += "-----+"
					# A series of ports starting
					elif prtcmd == 'e':
						theLine += "+"
					# A space or spaces
					elif re.match(r'^s\d{1,3}$', prtcmd):
						#myspace = re.match(r'^s\d{1,3}$', prtcmd).group(0)	
						numlist = prtcmd.split('s')						
						theLine += " "*int(numlist[1])
					# A vertial border or borders
					elif re.match(r'^vb\d{1,3}$', prtcmd):
						numlist = prtcmd.split('b')
						theLine += "|"*int(numlist[1])
					# A PIC border
					elif re.match(r'bpic\d{1}$', prtcmd):
						numlist = prtcmd.split('c')
						theLine += "+-----------PIC" + " " + numlist[1] + "-----------+"								
				if prtcmd == 'end':
					rem = chassisWidth - len(theLine)
					theLine += " "*(rem - 1) + "|"
			# Display the whole line on the screen
			print theLine

	#'labels', 's1', 'pic2', 'sX', '32x 1G SFP', 'sX', 'auxpic0', 'end'
	elif onLabels:
		#print "On Labels"
		#print myList
		theLine = '|'
		for prtcmd in myList:
			# A space or spaces
			if re.match(r'^s\d{1,3}$', prtcmd):
				numlist = prtcmd.split('s')						
				theLine += " "*int(numlist[1])
			# A vertial border or borders
			elif re.match(r'^vb\d{1,3}$', prtcmd):
				numlist = prtcmd.split('b')
				theLine += "|"*int(numlist[1])
			# Dynamic spacing function so SLOT looks right
			elif re.match(r'^dyns\d{1,3}$', prtcmd):
				numlist = prtcmd.split('s')
				rem = int(numlist[1]) - len(theLine)
				theLine += " "*rem
			elif prtcmd == 'end':
				rem = chassisWidth - len(theLine)
				theLine += " "*(rem - 1) + "|"
			else:
				theLine += prtcmd

		# Display the whole line on the screen
		print theLine				

	# 'border', 's1', 'cb1', 'hb29', 'cb1', 'end'
	elif onBorders:
		#print "On Borders"
		#print myList
		theLine = '|'
		for prtcmd in myList:
			# A corner border or borders
			if re.match(r'^cb\d{1,3}$', prtcmd):
				numlist = prtcmd.split('b')						
				theLine += "+"*int(numlist[1])
			# A horizontal border or borders
			elif re.match(r'^hb\d{1,3}$', prtcmd):
				numlist = prtcmd.split('b')						
				theLine += "-"*int(numlist[1])					
			# A space or spaces
			elif re.match(r'^s\d{1,3}$', prtcmd):
				numlist = prtcmd.split('s')						
				theLine += " "*int(numlist[1])
			# A vertial border or borders
			elif re.match(r'^vb\d{1,3}$', prtcmd):
				numlist = prtcmd.split('b')
				theLine += "|"*int(numlist[1])
			# Add FPC info to print out
			elif re.match(r'^fpc$', prtcmd):
				theLine += "FPC " + str(fpc)
			# Catch anything else (text)
			elif prtcmd != 'end':
				theLine += prtcmd
			# Display the whole int on the screen
			if prtcmd == 'end':
				rem = chassisWidth - len(theLine)
				theLine += " "*(rem - 1) + "|"
		# Display the whole line on the screen
		print theLine
	else:
		print "Unknown Line"

# Creates and displays the images
def chassisModularView(hostname, chassis_mod, chassis_side):
	print "Router Model: " + chassis_mod
	#pp.pprint(lan_router[hostname])
	chassisWidth = 162
	chassisTop = "+" + "-"*160 + "+"
	# Create top of chassis
	print chassisTop
	# Start looping through chassis mappings
	for slot in sorted(visual_chassis[chassis_mod][chassis_side].keys()):
		# Determine FPC
		fpc = int(slot.split('S')[1])
		for tier in sorted(visual_chassis[chassis_mod][chassis_side][slot].keys()):
			myList = []
			theLine = ""
			onPorts = False
			onLabels = False
			onBorders = False
			# Loop through each tier
			for prtcmd in visual_chassis[chassis_mod][chassis_side][slot][tier]:
				if prtcmd == 'ports': 
					onPorts = True
				elif prtcmd == 'labels': 
					onLabels = True
				elif prtcmd == 'border': 
					onBorders = True
				# Keep checking for slots
				elif prtcmd == 'slot':
					# If a module is in this slot...
					#print "Matched slot!"
					#print "FPC = " + str(fpc)
					if lan_router[hostname]['interfaces']['physical'].has_key(fpc):
						#print "Inside Loop"
						fpc_mod = lan_router[hostname]['interfaces']['physical'][fpc]['fpc_mod']
						#print "FPC: " + fpc_mod
						for fpccmd in visual_modules[fpc_mod][tier]:
							myList.append(fpccmd)
					# If a module is not in this slot...
					else:
						# Could use the empty slot module...
						#print "BLANK SLOT"
						fpc_mod = "EX6200-BLANK"
						for fpccmd in visual_modules[fpc_mod][tier]:
							myList.append(fpccmd)
				# Add Slot Number to Chassis
				elif prtcmd == 'slot_num':
					myList.append("SLOT " + str(fpc))
				else:
					myList.append(prtcmd)
			# Assembles and prints out content of device(s)
			assembleViewPrint(chassisWidth, hostname, fpc, myList, onPorts, onLabels, onBorders)
		# Print bottom border of chassis 
		print chassisTop

# Creates and displays the images
def chassisStackView(hostname, fpc, chassis_mod, chassis_side):
	chassisWidth = 180
	chassisTop = "+" + "-"*178 + "+"
	# Create top of chassis
	print chassisTop
	# Start looping through chassis mappings
	for tier in sorted(visual_chassis[chassis_mod][chassis_side].keys()):
		myList = []
		loopNum = 0
		theLine = ""
		onPorts = False
		onLabels = False
		onBorders = False
		# Loop through each tier
		for prtcmd in visual_chassis[chassis_mod][chassis_side][tier]:
			if prtcmd == 'ports': 
				onPorts = True
			elif prtcmd == 'labels': 
				onLabels = True
			elif prtcmd == 'border': 
				onBorders = True
			# Keep checking for PICs
			elif re.match(r'^pic\d{1}$', prtcmd):
				# Extract the PIC number and convert to an integer
				pic = int(prtcmd.split('c')[1])
				# If a module is in this slot...
				if lan_router[hostname]['interfaces']['physical'][fpc].has_key(pic):
					#print "PIC Exists"
					pic_mod = lan_router[hostname]['interfaces']['physical'][fpc][pic]['module_mod']
					#pic_mod += " (" + str(pic) + ")"
					#print "PIC Module: " + pic_mod
					for piccmd in visual_modules[pic_mod][tier]:
						if re.match(r'^\d{1,3}$', piccmd):
							piccmd = str(pic) + 'p' + piccmd
							myList.append(piccmd)
						else:
							myList.append(piccmd)
				# If a module is not in this slot...
				else:
					# Could use the empty slot module...
					pic_mod = "EX4300-BLANK"
					for piccmd in visual_modules[pic_mod][tier]:
						myList.append(piccmd)						
					#print "PIC Slot Empty"
			#	for piccmd in visual_modules[module_mod]
			elif re.match(r'^auxpic\d{1}$', prtcmd):
				pic = int(prtcmd.split('c')[1])
				if lan_router[hostname]['interfaces']['physical'][fpc][pic]['has_aux']:
					#print "Aux PIC Exists"
					pic_mod = lan_router[hostname]['interfaces']['physical'][fpc][pic]['aux_mod']
					#pic_mod += " (" + str(pic) + ")"
				#print "PIC Module: " + pic_mod
					for piccmd in visual_modules[pic_mod][tier]:
						if re.match(r'^\d{1,3}$', piccmd):
							piccmd = str(pic) + 'p' + piccmd
							myList.append(piccmd)
						else:
							myList.append(piccmd)
				else:
					print "Error: PIC not in router"										
			else:
				myList.append(prtcmd)
		# Assembles and prints out content of device(s)
		assembleViewPrint(chassisWidth, hostname, fpc, myList, onPorts, onLabels, onBorders)
	# Print bottom border of chassis
	print chassisTop

# Adds the interfaces that are common to this chassis, includes native and built-in interfaces
def addNativeInterfaces(hostname, chassis_mod, is_vc, fpc, pic):
	# Get number of ports for this model
	port_num = system_model[chassis_mod]['port_num']

	# Build out base of interface heirarchy
	lan_router[hostname]['interfaces']['physical'].update({ fpc : {} })
	lan_router[hostname]['interfaces']['physical'][fpc].update({ 'fpc_mod' : chassis_mod })
	
	
	# Configure default VC priority, if system is a VC
	if is_vc:
		if fpc == 0 or fpc == 1:
			lan_router[hostname]['interfaces']['physical'][fpc].update({ 'vc_priority' : 255 })
		elif fpc == 2: lan_router[hostname]['interfaces']['physical'][fpc].update({ 'vc_priority' : 10 })
		elif fpc == 3: lan_router[hostname]['interfaces']['physical'][fpc].update({ 'vc_priority' : 9 })
		elif fpc == 4: lan_router[hostname]['interfaces']['physical'][fpc].update({ 'vc_priority' : 8 })
		elif fpc == 5: lan_router[hostname]['interfaces']['physical'][fpc].update({ 'vc_priority' : 7 })				
		elif fpc == 6: lan_router[hostname]['interfaces']['physical'][fpc].update({ 'vc_priority' : 6 })
		elif fpc == 7: lan_router[hostname]['interfaces']['physical'][fpc].update({ 'vc_priority' : 5 })				
		elif fpc == 8: lan_router[hostname]['interfaces']['physical'][fpc].update({ 'vc_priority' : 4 })
		elif fpc == 9: lan_router[hostname]['interfaces']['physical'][fpc].update({ 'vc_priority' : 3 })
		
	# Configure the PICs
	lan_router[hostname]['interfaces']['physical'][fpc].update({ pic : {} })
	lan_router[hostname]['interfaces']['physical'][fpc][pic].update({ 'module_type' : 'native' })
	lan_router[hostname]['interfaces']['physical'][fpc][pic].update({ 'module_mod' : chassis_mod })
	lan_router[hostname]['interfaces']['physical'][fpc][pic].update({ 'has_aux' : False })
	
	# Create ports
	for port in range(0, port_num):
		lan_router[hostname]['interfaces']['physical'][fpc][pic].update({ port : {} })
		lan_router[hostname]['interfaces']['physical'][fpc][pic][port].update({ 'port' : port })
		lan_router[hostname]['interfaces']['physical'][fpc][pic][port].update({ 'is_linked' : False })
		lan_router[hostname]['interfaces']['physical'][fpc][pic][port].update({ 'is_bundled' : False })
	
	print("Successfully added NATIVE interfaces...\n")

# Set system hostname
def setSystemHostname(oldhost=""):
	newhost = ""
	if oldhost:
		# For changing hostname after initial config
		print "The current hostname is: " + oldhost
		newhost = getInputAnswer("Enter hostname")
		while not isUniqueHostname(newhost):
			newhost = getInputAnswer("Enter hostname")
		lan_router[newhost] = lan_router[oldhost]
		del lan_router[oldhost]
	else:
		# For during initial configuration
		newhost = getInputAnswer("Enter hostname")
		while not isUniqueHostname(newhost):
			newhost = getInputAnswer("Enter hostname")
		lan_router.update({ newhost : {} })
	
	return newhost

# Create basic system configuration
def setSystemCommon():
	# Set System Type (MDF or IDF)
	system_type = ""
	hostname = None
	question = "Select system type"
	option = [ "MDF", "IDF", "Go Back" ]
	selection = getOptionTRAnswer(question, option)
	if selection == 0:
		system_type = "mdf"
		# Set Hostname
		hostname = setSystemHostname()
		# Set System Info
		lan_router[hostname].update({ 'system_type' : system_type })		
		
	elif selection == 1:
		system_type = "idf"
		# Set Hostname
		hostname = setSystemHostname()
		# Set System Info
		lan_router[hostname].update({ 'system_type' : system_type })
			
	return hostname

# Create actual module interfaces
def addModuleInterfaces(hostname, fpc, pic, mod):
	# Get the number of ports for this module
	port_num = modular_model[mod]['port_num']

	# Specifically match this module, its interfaces are added onto the end of FPC 0, 32 - 35
	if mod == 'EX4300-UM-4XSFP':
		# Create PIC
		if not lan_router[hostname]['interfaces']['physical'][fpc].has_key(pic):
			lan_router[hostname]['interfaces']['physical'][fpc].update({ pic : {} })
		if modular_model[mod]['built_in']:
			lan_router[hostname]['interfaces']['physical'][fpc][pic].update({ 'aux_type' : 'builtin' })
		else:
			lan_router[hostname]['interfaces']['physical'][fpc][pic].update({ 'aux_type' : 'expan' })
		lan_router[hostname]['interfaces']['physical'][fpc][pic].update({ 'has_aux' : True })
		lan_router[hostname]['interfaces']['physical'][fpc][pic].update({ 'aux_mod' : mod })		
	
		# Create PIC ports
		for port in range(32, 36):
			lan_router[hostname]['interfaces']['physical'][fpc][pic].update({ port : {} })
			lan_router[hostname]['interfaces']['physical'][fpc][pic][port].update({ 'port' : port })
			lan_router[hostname]['interfaces']['physical'][fpc][pic][port].update({ 'is_linked' : False })
			lan_router[hostname]['interfaces']['physical'][fpc][pic][port].update({ 'is_bundled' : False })
			lan_router[hostname]['interfaces']['physical'][fpc][pic][port].update({ 'is_aux' : True })
			lan_router[hostname]['interfaces']['physical'][fpc][pic][port].update({ 'access_mode' : ' ' })

	# All other modules hit here
	else:
		# Create PIC
		lan_router[hostname]['interfaces']['physical'][fpc].update({ pic : {} })
		if modular_model[mod]['built_in']:
			lan_router[hostname]['interfaces']['physical'][fpc][pic].update({ 'module_type' : 'builtin' })
		else:
			lan_router[hostname]['interfaces']['physical'][fpc][pic].update({ 'module_type' : 'expan' })
		lan_router[hostname]['interfaces']['physical'][fpc][pic].update({ 'has_aux' : False })
		lan_router[hostname]['interfaces']['physical'][fpc][pic].update({ 'module_mod' : mod })
		
		# Create PIC ports
		for port in range(0, port_num):
			lan_router[hostname]['interfaces']['physical'][fpc][pic].update({ port : {} })
			lan_router[hostname]['interfaces']['physical'][fpc][pic][port].update({ 'port' : port })
			lan_router[hostname]['interfaces']['physical'][fpc][pic][port].update({ 'is_linked' : False })
			lan_router[hostname]['interfaces']['physical'][fpc][pic][port].update({ 'is_bundled' : False })
			lan_router[hostname]['interfaces']['physical'][fpc][pic][port].update({ 'access_mode' : ' ' })

	print("Successfully added " + mod + " to slot " + str(pic) + " ...\n")
	
# Check if slot is used
def slotUsed(hostname, fpc, pic):
	if lan_router[hostname]['interfaces']['physical'][fpc].has_key(pic):
		print "Slot is USED"
		return True
	else:
		print "Slot is NOT USED"
		return False

###############################	
# ========== LINKS ========== #	
###############################

# Check user input and see if link is valid/unused
def parseInterface(intf):
	parts = {}
	if re.match(r'^\d{1,2}\/\d{1,2}\/\d{1,2}$', intf):
		portLoc = intf.split('/')
		parts = {
			'fpc' : int(portLoc[0]),
			'pic' : int(portLoc[1]),
			'port' : int(portLoc[2])
		}
	return parts

# Check if an interface exists
def isInterfaceExists(intf, hostname):
	portLoc = parseInterface(intf)
	if lan_router[hostname]['interfaces']['physical'].has_key(portLoc['fpc']):
		if lan_router[hostname]['interfaces']['physical'][portLoc['fpc']].has_key(portLoc['pic']):
			if lan_router[hostname]['interfaces']['physical'][portLoc['fpc']][portLoc['pic']].has_key(portLoc['port']):
				if lan_router[hostname]['interfaces']['physical'][portLoc['fpc']][portLoc['pic']].has_key('module_mod'):
					#print "Mod of PIC is: " + lan_router[hostname]['interfaces']['physical'][portLoc['fpc']][portLoc['pic']]['module_mod']
					pass
				elif lan_router[hostname]['interfaces']['physical'][portLoc['fpc']].has_key('fpc_mod'):
					#print "Mod of FPC is: " + lan_router[hostname]['interfaces']['physical'][portLoc['fpc']]['fpc_mod']
					pass
				return True
			else:
				print "PORT was invalid"
				return False
		else:
			print "PIC was invalid"
			return False
	else:
		print "FPC was invalid"
		return False

# Check if an interface is assigned to a link (true) or not (false)
def isInterfaceAvailable(intf, hostname):
	portLoc = parseInterface(intf)
	if isInterfaceExists(intf, hostname):
		if lan_router[hostname]['interfaces']['physical'][portLoc['fpc']][portLoc['pic']][portLoc['port']]['is_linked']:
			return False
		else:
			return True
	else:
		return False
	
# Get a parameter
def getParameter(hostname, iparams, parameter):
	results = []
	# Check if an "aux" pic exists
	if lan_router[hostname]['interfaces']['physical'][iparams[0]].has_key('aux'):
		# Check if this interface is the appropriate one
		if lan_router[hostname]['interfaces']['physical'][iparams[0]]['aux'].has_key(iparams[1]):
			pass
	if lan_router[hostname]['interfaces']['physical'][iparams[0]].has_key(iparams[1]):
		pass

# Create a P2P link
def createLink():
	hosts = selectDevices('both')
	intfsValid = False
	links = {}
	firstLoopValid = False
	linkNum = 0
	one = 1
	two = 2
	speedOptions = []
	
	# Loop on hosts
	for hostname in hosts:
		linkNum += one
		# Display chassis
		displayChassisHardware(hostname, "Both")
		# Display menu to ask for interface
		print "Checking host: " + hostname
		intfsValid = False
		# Check if this host is a lan host
		if hostname in lan_router:
			while not intfsValid:
				myIntf = getInputAnswer("Enter the " + hostname + " side interface to use")
				# If the interface exists
				if isInterfaceExists(myIntf, hostname):
					intfsValid = True
					# GET possible port properties and ADD to dictionary
					props = parseInterface(myIntf)
					# Candidate Interface Dictionary
					links.update({ linkNum : {} })
					links[linkNum].update({ 'Hostname' : hostname })
					links[linkNum].update({ 'PosSpeed' : [] })
					links[linkNum].update({ 'PosMedia' : [] })
					links[linkNum].update({ 'FPC' : props['fpc'] })
					links[linkNum].update({ 'PIC' : props['pic'] })
					links[linkNum].update({ 'PORT' : props['port'] })				
					
					# Check if this interface is already linked...
					if lan_router[hostname]['interfaces']['physical'][props['fpc']][props['pic']][props['port']]['is_linked']:
						print "Interface " + str(props['fpc']) + '/' + str(props['pic']) + '/' + str(props['port']) + " already linked!"
						intfsValid = False
					# Checks if this port is in a expansion module, get model from PIC
					# Check if this is an auxiliary port
					elif lan_router[hostname]['interfaces']['physical'][props['fpc']][props['pic']].has_key('has_aux') and lan_router[hostname]['interfaces']['physical'][props['fpc']][props['pic']][props['port']].has_key('is_aux'):
						model = lan_router[hostname]['interfaces']['physical'][props['fpc']][props['pic']]['aux_mod']
						#print "Aux Port: " + model + " (PIC)"
						for speed in modular_model[model]['speed']:
							links[linkNum]['PosSpeed'].append(speed)
						for media in modular_model[model]['intf_type']:
							links[linkNum]['PosMedia'].append(media)
							
					# Check if this is anything else, but a native interface
					elif lan_router[hostname]['interfaces']['physical'][props['fpc']][props['pic']]['module_type'] != 'native':
						# If this is a non-auxiliary port
						model = lan_router[hostname]['interfaces']['physical'][props['fpc']][props['pic']]['module_mod']
						#print "Expan Port: " + model + " (PIC)"
						if modular_model.has_key(model):
							for speed in modular_model[model]['speed']:
								links[linkNum]['PosSpeed'].append(speed)
							for media in modular_model[model]['intf_type']:
								links[linkNum]['PosMedia'].append(media)
						else:
							for speed in system_model[model]['speed']:
								links[linkNum]['PosSpeed'].append(speed)
							for media in system_model[model]['intf_type']:
								links[linkNum]['PosMedia'].append(media)
					# Otherwise port is in a native module, get model from FPC
					else:
						model = lan_router[hostname]['interfaces']['physical'][props['fpc']]['fpc_mod']
						#print "Native Port: " + model + " (FPC)"
						for speed in system_model[model]['speed']:
							links[linkNum]['PosSpeed'].append(speed)
						for media in system_model[model]['intf_type']:
							links[linkNum]['PosMedia'].append(media)					
					#print "***** PPRINT *****"
					#pp.pprint(links)
				else:
					print "Invalid link..."
					intfsValid = False
		# If not a lan host...
		else:
			print "Host " + hostname + " is a WAN device."
			question = "Enter the " + hostname + " side interface to use"
			option = wan_router[hostname]['intf_name']
			selection = getOptionAnswer(question, option)
			
			# Candidate Interface Dictionary
			links.update({ linkNum : {} })
			links[linkNum].update({ 'Hostname' : hostname })
			links[linkNum].update({ 'PORT' : selection })			
			intfsValid = True


	isMediaValid = False
	isSpeedValid = False
	print "Interfaces are both valid"
	print "Checking interfaces..."
	
	
	# Checks if host one is a wan_router...
	if links[one]['Hostname'] in wan_router:
		for speedOne in links[two]['PosSpeed']:
			speedOptions.append(speedOne)
		# Choose speed from lan_router options
		question = "Choose a speed"
		selection = getOptionAnswer(question, speedOptions)
		# Select the speed for this link
		if selection != "Go Back":
			print "Speed selected is: " + selection
			# Add the link
			links[linkNum].update({ 'ActSpeed' : selection })
			if len(links[two]['PosMedia']) > 1:
				if links[two]['ActSpeed'] == '10G':
					links[linkNum].update({ 'ActMedia' : 'SFP+' })
				else:
					links[linkNum].update({ 'ActMedia' : 'SFP' })
			addLinks(links)
	
	# Checks if host two is a wan_router...
	elif links[two]['Hostname'] in wan_router:
		for speedTwo in links[one]['PosSpeed']:
			speedOptions.append(speedTwo)
		# Choose speed from lan_router options
		question = "Choose a speed"
		selection = getOptionAnswer(question, speedOptions)
		# Select the speed for this link
		if selection != "Go Back":
			print "Speed selected is: " + selection
			# Add the link
			links[linkNum].update({ 'ActSpeed' : selection })
			if len(links[one]['PosMedia']) > 1:
				if links[one]['ActSpeed'] == '10G':
					links[linkNum].update({ 'ActMedia' : 'SFP+' })
				else:
					links[linkNum].update({ 'ActMedia' : 'SFP' })
			addLinks(links)			
	
	# Otherwise they are both lan_routers...
	else:
		if links[one]['Hostname'] != links[two]['Hostname']:
			#print 'Hostnames are unique...'
			for mediaOne in links[one]['PosMedia']:
				#print "Media 1"
				for mediaTwo in links[two]['PosMedia']: 
					#print "Media 2"
					if links[one]['PosMedia'] == links[two]['PosMedia']:
						#print "Match! -> Link 1: " + mediaOne + " and Link 2: " + mediaTwo
						isMediaValid = True
						break					
					elif re.match(r'^SFP\+?$', mediaOne) and re.match(r'^SFP\+?$', mediaTwo):
						#print "Match! -> Link 1: " + mediaOne + " and Link 2: " + mediaTwo
						isMediaValid = True
						break
					elif re.match(r'^(SFP\+?|RJ45)$', mediaOne) and re.match(r'^(SFP\+?|RJ45)$', mediaTwo):
						#print "Tenative Match! -> Link 1: " + mediaOne + " and Link 2: " + mediaTwo
						print "Warning: One side of this link is RJ45 (copper) and the other is SFP. Make sure you have a RJ45 (copper) SFP."
						isMediaValid = True
					else:
						#print "Link 1: " + mediaOne + " and Link 2: " + mediaTwo
						pass
			if isMediaValid:
				for speedOne in links[one]['PosSpeed']:
					#print "Speed 1"
					for speedTwo in links[two]['PosSpeed']: 
						#print "Speed 2"
						if speedOne == speedTwo:
							print "Match! -> Link 1: " + speedOne + " and Link 2: " + speedTwo
							speedOptions.append(speedOne)
							isSpeedValid = True
							break
						else:
							#print "Link 1: " + speedOne + " and Link 2: " + speedTwo
							pass
				if isSpeedValid:
					print "Link request valid!!!"
					question = "Choose a speed"
					selection = getOptionAnswer(question, speedOptions)
					# Select the speed for this link
					if selection != "Go Back":
						print "Speed selected is: " + selection
						# Add the link
						if len(links[one]['PosMedia']) > 1:
							if selection == '10G':
								links[one].update({ 'ActMedia' : 'SFP+' })
							else:
								links[one].update({ 'ActMedia' : 'SFP' })						
						links[one].update({ 'ActSpeed' : selection })
						if len(links[two]['PosMedia']) > 1:
							if selection == '10G':
								links[two].update({ 'ActMedia' : 'SFP+' })
							else:
								links[two].update({ 'ActMedia' : 'SFP' })
						links[two].update({ 'ActSpeed' : selection })
						addLinks(links)
				else:
					print "Speed is not compatible...try again"
					print "Link request invalid!"
			else:
				print "Media is not compatible...try again"
				print "Link request invalid!"
		else:
			print "Links must be between different hosts"
			print "Link request invalid!"
	
# Create link and add ports

# links.update({ linkNum : {} })
# links[linkNum].update({ 'Hostname' : hostname })
# links[linkNum].update({ 'PosSpeed' : [] })
# links[linkNum].update({ 'PosMedia' : [] })
# links[linkNum].update({ 'ActSpeed' : speed })
# links[linkNum].update({ 'ActMedia' : media })
# links[linkNum].update({ 'FPC' : props['fpc'] })
# links[linkNum].update({ 'PIC' : props['pic'] })
# links[linkNum].update({ 'PORT' : props['port'] })

def addLinks(links):
	host = ""
	# Add attributes to ports
	for linkNum in links:
		if links[linkNum]['Hostname'] in lan_router:
			host = links[linkNum]['Hostname']
			media = links[linkNum]['ActMedia']
			speed = links[linkNum]['ActSpeed']
			fpc = links[linkNum]['FPC']
			pic = links[linkNum]['PIC']
			aport = links[linkNum]['PORT']
	
			# Set port attributes
			lan_router[host]['interfaces']['physical'][fpc][pic][aport].update({ 'is_linked' : True })
			lan_router[host]['interfaces']['physical'][fpc][pic][aport].update({ 'type' : media })
			lan_router[host]['interfaces']['physical'][fpc][pic][aport].update({ 'speed' : speed })
			#lan_router[host]['interfaces']['physical'][fpc][pic][aport].update({ 'access_mode' : 'VCP' })

	# Create link
	# link_map[]
	newKey = 1
	# Create link_id
	if link_map.has_key(newKey):
		newKey = max(link_map.keys()) + 1
		link_map.update({ newKey : {} })
	else:
		link_map.update({ newKey : {} })
	
	# Add attributes to new link
	if links[1]['Hostname'] in wan_router:
		# Side A
		link_map[newKey].update({ 'sideA_host' : links[1]['Hostname'] })
		intf = str(links[1]['PORT'])
		link_map[newKey].update({ 'sideA_port' : intf })
		# Side B
		link_map[newKey].update({ 'sideB_host' : links[2]['Hostname'] })
		intf = str(links[2]['FPC']) + '/' + str(links[2]['PIC']) + '/' + str(links[2]['PORT'])
		link_map[newKey].update({ 'sideB_port' : intf })
		link_map[newKey].update({ 'speed' : speed })
		link_map[newKey].update({ 'type' : media })

	elif links[2]['Hostname'] in wan_router:
		# Side A
		link_map[newKey].update({ 'sideA_host' : links[1]['Hostname'] })
		intf = str(links[1]['FPC']) + '/' + str(links[1]['PIC']) + '/' + str(links[1]['PORT'])
		link_map[newKey].update({ 'sideA_port' : intf })
		# Side B
		link_map[newKey].update({ 'sideB_host' : links[2]['Hostname'] })
		intf = str(links[2]['PORT'])
		link_map[newKey].update({ 'sideB_port' : intf })
		link_map[newKey].update({ 'speed' : speed })
		link_map[newKey].update({ 'type' : media })
	
	else:
		# Side A
		link_map[newKey].update({ 'sideA_host' : links[1]['Hostname'] })
		intf = str(links[1]['FPC']) + '/' + str(links[1]['PIC']) + '/' + str(links[1]['PORT'])
		link_map[newKey].update({ 'sideA_port' : intf })
		# Side B
		link_map[newKey].update({ 'sideB_host' : links[2]['Hostname'] })
		intf = str(links[2]['FPC']) + '/' + str(links[2]['PIC']) + '/' + str(links[2]['PORT'])
		link_map[newKey].update({ 'sideB_port' : intf })
		link_map[newKey].update({ 'speed' : speed })
		link_map[newKey].update({ 'type' : media })
	
	print "[Link Map]"
	pp.pprint(link_map)
	#print "Lan Router " + "(" + host + ")"
	#pp.pprint(lan_router[host])

# Creates dictionary of the passed chassis's modules
def moduleDict(hostname):
	chassis_mod_dict = {}
	for fpc in lan_router[hostname]['interfaces']['physical'].keys():
		chassis_mod_dict.update({ fpc : {} })
		# Loop over member components, following "if" targets PICs
		for pic in lan_router[hostname]['interfaces']['physical'][fpc].keys():
			#pp.pprint(lan_router[hostname])
			# General modules (inclduing VCP, Expansion, Builtin)
			if(isinstance( pic, ( int, long ) )):
				chassis_mod_dict[fpc].update({ pic : [] })
				chassis_mod_dict[fpc][pic].append(lan_router[hostname]['interfaces']['physical'][fpc][pic]['module_mod'])
				# Check for auxillary modules (EX4300-UM-4XSFP)
				if lan_router[hostname]['interfaces']['physical'][fpc][pic].has_key('aux_mod'):
					chassis_mod_dict[fpc][pic].append(lan_router[hostname]['interfaces']['physical'][fpc][pic]['aux_mod'])
	return chassis_mod_dict

# Assign VCPs Menu
def assignVCPsMenu():
	hostname = selectChassisMenu("vc")
	if hostname:
		chassisStat = vcScan(hostname)
		question = "Select a chassis operation"
		if chassisStat == "VCP" or chassisStat == "QSFP":
			option = [ "Automatic Add", "Manual Add", "Go Back" ]
			selection = ""
			#while True:
			selection = getOptionTRAnswer(question, option)
			if selection == 0:
				assignVCPs(hostname, "auto", moduleDict(hostname))
			elif selection == 1:
				assignVCPs(hostname, "manual", moduleDict(hostname))
		
		elif chassisStat == "NONE":
			option = [ "Manual Add", "Go Back" ]
			selection = ""
			#while True:
			selection = getOptionTRAnswer(question, option)
			if selection == 0:
				assignVCPs(hostname, "manual", moduleDict(hostname))

# Assign VCPs - two options, automatic and manual. Automatic is for VC stacks with all QSFP+ or VCP links only
# Create link and add ports

# links.update({ linkNum : {} })
# links[linkNum].update({ 'Hostname' : hostname })
# links[linkNum].update({ 'PosSpeed' : [] })
# links[linkNum].update({ 'PosMedia' : [] })
# links[linkNum].update({ 'FPC' : props['fpc'] })
# links[linkNum].update({ 'PIC' : props['pic'] })
# links[linkNum].update({ 'PORT' : props['port'] })

def reserveVCPs(host, a_fpc, modDict):
	intf_num = 1
	inc = 0
	mylink = {}
	print "Neighor Member " + str(a_fpc)
	# Loop over PICs in neighbor FPC
	for a_pic in modDict[a_fpc].keys():
		for module in modDict[a_fpc][a_pic]:
			print "Checking module: " + module + "..."
			if module in modular_model.keys():
				print "Valid module!"
				type_list = modular_model[module]['intf_type']
				intf_speed = modular_model[module]['speed'][-1] # Use the last element in this list
				if ("QSFP+" in type_list) or ("VCP" in type_list):
					intf_type = modular_model[module]['intf_type'][-1] # Use the last element in this list
					print "Module VCP capable..."
					for a_port in lan_router[host]['interfaces']['physical'][a_fpc][a_pic]:
						if(isinstance( a_port, ( int, long ) )):
							print "Model: " + module + " FPC: " + str(a_fpc) + " PIC: " + str(a_pic) + " PORT: " + str(a_port)
							intf = str(a_fpc) + "/" + str(a_pic) + "/" + str(a_port)
							if isInterfaceAvailable(intf, host):
								# Modify port parameters for this link
								print "Interface found"
								lan_router[host]['interfaces']['physical'][a_fpc][a_pic][a_port].update({ 'access_mode' : 'VCP' })
								#lan_router[host]['interfaces']['physical'][a_fpc][a_pic][a_port].update({ 'type' : intf_type })
								#lan_router[host]['interfaces']['physical'][a_fpc][a_pic][a_port].update({ 'speed' : intf_speed })
								print "Inteface Speed: " + intf_speed
								# Parameters for creating link
								mylink.update({ 'Hostname' : host })
								mylink.update({ 'ActSpeed' : intf_speed })
								mylink.update({ 'ActMedia' : intf_type })
								mylink.update({ 'FPC' : a_fpc })
								mylink.update({ 'PIC' : a_pic })
								mylink.update({ 'PORT' : a_port })
								inc += 1
							else:
								print "Interface used"
						if inc == intf_num:
							print "Break 1"
							break
			if inc == intf_num:
				print "Break 2"
				break
		if inc == intf_num:
			print "Break 3"
			break
	
	return mylink


def assignVCPs(host, mode, modDict):
	# Number of FPCs or members in this stack
	links = {}
	stack_size = len(lan_router[host]['interfaces']['physical'])
	# Loop through modDict for each FPC in stack. This is the LOCAL member
	for fpc in modDict.keys():
		# Get the neighbors of this FPC, put them in a list, fpc_a and fpc_b
		mymap = link_mapping("braided", stack_size, fpc)
		a_fpc = mymap[0]
		b_fpc = mymap[1]
		# Loop over neighbor list
		for a_fpc in mymap:
			# Check if LOCAL member is lower #, if yes, reserve ports and create link
			if a_fpc > fpc:
				neigh_dict = reserveVCPs(host, a_fpc, modDict)
				local_dict = reserveVCPs(host, fpc, modDict)
				#print "Neigh Dict"
				#pp.pprint(neigh_dict)
				#print "Local Dict"
				#pp.pprint(local_dict)
				#print "Combined Dict"
				links.update({ 1 : {} })
				links.update({ 2 : {} })
				links[1].update(neigh_dict)
				links[2].update(local_dict)
				pp.pprint(links)
				addLinks(links)
			else:
				# Go to next neighbor
				pass
			

# VCP Links
def vcScan(hostname):
	modDict = moduleDict(hostname)
	print "Hostname: " + hostname
	pp.pprint(modDict)
	
	noChassQSFP = False
	noChassVCP = False
	# Loop over FPCs modules and check for VCP capability
	for fpc in modDict.keys():
		noFpcQSFP = True
		noFpcVCP = True
		# Loop over PICs in FPC
		for pic in modDict[fpc].keys():
			for module in modDict[fpc][pic]:
				if module in modular_model.keys():
					# VCP levels are... 1. DEFAULT (VCP or QSFP+), 2. 10G (optical SFP+), 3. NONE (no VCP capable ports)
					intf_type = modular_model[module]['intf_type']
				else:
					intf_type = system_model[module]['intf_type']
				# Determine the port types
				for mytype in intf_type:
					if mytype == "QSFP+":
						noFpcQSFP = False
					elif mytype == "VCP":
						noFpcVCP = False

		if noFpcQSFP:
			noChassQSFP = True
		elif noFpcVCP:
			noChassVCP = True

		#print "FPC: " + str(fpc) + " PIC: " + str(pic) + " Module: " + module
		
	if noChassQSFP and noChassVCP:
		print "Virtual Chassis has no standard VCP ports!"
		myVCP = "NONE"
	elif not noChassQSFP:
		print "Virtual Chassis has QSFP+ for VCP"
		myVCP = "VCP"
	elif not noChassVCP:
		print "Virtual Chassis has VCP for VCP"
		myVCP = "QSFP"

	return myVCP
	
	#stack_size = len(lan_router[hostname]['interfaces']['physical'])
	#for fpc in modDict.keys():
	#	neigh_list = link_mapping("braided", stack_size, fpc)


# Function for determining which VC members a specific chassis will link with
def link_mapping(map_type, stack_size, member_num):
	s1 = 0
	s2 = 0
	# Determine mappings for "long loop" type member
	if map_type == 'longloop':
		if stack_size == 2 and member_num == 1:
			s1 = 0
			s2 = 0
		elif member_num == 0:
			s1 = 1
			s2 = stack_size - 1
		elif member_num == (stack_size - 1):
			s1 = 0
			s2 = stack_size - 2
		else:
			s1 = member_num - 1
			s2 = member_num + 1
	# Determine mappings for "braided" type member
	else:
		if stack_size == 2 and member_num == 0:
			s1 = 1
			s2 = 1
		elif stack_size == 2 and member_num == 1:
			s1 = 0
			s2 = 0
		elif stack_size == 3 and member_num == 1:
			s1 = 0
			s2 = 2
		elif stack_size == 4 and member_num == 2:
			s1 = 0
			s2 = 3
		elif member_num == 0:
			s1 = 1
			s2 = 2
		elif member_num == 1:
			s1 = 0
			s2 = 3
		elif member_num == (stack_size - 1):
			s1 = member_num - 2
			s2 = member_num - 1
		elif member_num == (stack_size - 2):
			s1 = member_num - 2
			s2 = member_num + 1
		else:
			s1 = member_num - 2
			s2 = member_num + 2
	s_list = []
	s_list.append(s1)
	s_list.append(s2)
	
	print "( " + str(s1) + ", " + str(s2) + " )"
	
	return s_list

	
###############################	
# ========== MENUS ========== #	
###############################
# Primary Menu
def mainMenu():
	fn = "mydict.csv"
	question = "Select an operation"
	option = [ "Build Chassis", "Define Inter-Connects", "Show Devices", "Modify Chassis", "Save Topology", "Load Topology", "Exit" ]
	selection = ""
	while True:
		selection = getOptionTRAnswer(question, option)
		if selection == 0:
			buildChassisMenu()
		elif selection == 1:
			linkMenu()
		elif selection == 2:
			showDeviceMenu()
		elif selection == 3:
			modChassisMenu()			
		elif selection == 4:
			global lan_router
			global wan_router
			saveDict(lan_router, 'lan_router')
			saveDict(wan_router, 'wan_router')
		elif selection == 5:
			lan_router.clear()
			wan_router.clear()
			lan_router = openDict('lan_router')
			wan_router = openDict('wan_router')
			#print lan_router
			#print wan_router
		else: break
	
# Build chassis Menu
def buildChassisMenu():
	question = "Select a chassis operation"
	option = [ "Add WAN Device", "Add LAN Device", "Show Devices", "Go Back" ]
	selection = ""
	while True:
		selection = getOptionTRAnswer(question, option)
		if selection == 0:
			addWANDevice()
		elif selection == 1:
			addDeviceMenu()
		elif selection == 2:
			showDeviceMenu()
		else: break

# Link Menu
def linkMenu():
	question = "Select a link operation"
	option = [ "Create Links", "Display Interfaces", "Assign VCPs", "Go Back" ]
	selection = ""
	while True:
		selection = getOptionTRAnswer(question, option)
		if selection == 0:
			createLink()
		elif selection == 1:
			displayIntfMenu()
		elif selection == 2:
			assignVCPsMenu()
		else: break

# Link Menu - Select Devices - options ('lan', 'wan', 'both') default to 'lan'
# This function gets the current hostnames, ask for user to select one, and returns that hostname.
def selectDevices(devices='lan'):
	# Create option list
	option = []
	
	# Add hostnames to list depending on argument
	if devices == 'lan' or devices == 'both':
		for hostname in lan_router.keys():
			option.append(hostname)
	if devices == 'wan' or devices == 'both':
		for hostname in wan_router.keys():
			option.append(hostname)
	option.append("Go Back")

	# Ask user to select 2 devices
	question = "Choose a system"
	selection = getMultiAnswer(question, option, 2)
	
	for host in selection:
		print "Host -> " + host
	return selection

# Display Interfaces Menu
def displayIntfMenu():
	try:
		displayInterfaces(selectChassisMenu())
	except Exception as err:
		pass
	
# Menu for displaying chassis		
def showDeviceMenu():
	# Display a basic display of chassis
	displayChassisBasic()
	print "Choose a switch for more detail:"
	hostname = selectChassisMenu()

	if hostname:
		# Display Detailed Chassis View
		print "\n" + "=" * 95
		print "Hostname:\t" + hostname
				
		# For Single Chassis or Virtual Chassis
		if hostname in lan_router.keys():
			print "System Type:\t" + lan_router[hostname]['system_type']
			if lan_router[hostname]['chassis_type'] == 'stackable':
				# Virtual Chassis
				if lan_router[hostname]['is_vc']:
					print "Model:\t\tVirtual Chassis"
					for fpc in lan_router[hostname]['interfaces']['physical'].keys():
						print "-" * 95
						print "VC " + str(fpc) + ":\t" + lan_router[hostname]['interfaces']['physical'][fpc]['fpc_mod'] + "\t" + \
							str(lan_router[hostname]['interfaces']['physical'][fpc]['vc_priority'])
						for pic in lan_router[hostname]['interfaces']['physical'][fpc].keys():
							#pp.pprint(lan_router[hostname])
							# General modules (inclduing VCP, Expansion, Builtin)
							if(isinstance( pic, ( int, long ) )):
								module_mod = lan_router[hostname]['interfaces']['physical'][fpc][pic]['module_mod']
								# If it's a module
								if module_mod in modular_model.keys():
									if 'VCP' in modular_model[module_mod]['intf_type']:
										print "\tPIC " + str(pic) + "\t(" + lan_router[hostname]['interfaces']['physical'][fpc][pic]['module_type'] + "):\t" + \
											lan_router[hostname]['interfaces']['physical'][fpc][pic]['module_mod'] + " (VCP)"
									else:
										print "\tPIC " + str(pic) + "\t(" + lan_router[hostname]['interfaces']['physical'][fpc][pic]['module_type'] + "):\t" + \
											lan_router[hostname]['interfaces']['physical'][fpc][pic]['module_mod']
								# If it's native
								else:
									print "\tPIC " + str(pic) + "\t(" + lan_router[hostname]['interfaces']['physical'][fpc][pic]['module_type'] + "):\t" + \
										lan_router[hostname]['interfaces']['physical'][fpc][pic]['module_mod']
								# Check for auxillary modules (EX4300-UM-4XSFPP)
								if lan_router[hostname]['interfaces']['physical'][fpc][pic].has_key('aux_mod'):
									print "\tPIC " + str(pic) + "\t(" + lan_router[hostname]['interfaces']['physical'][fpc][pic]['aux_type'] + "):\t" + \
										lan_router[hostname]['interfaces']['physical'][fpc][pic]['aux_mod']							
						print "-" * 95
					print "=" * 95
				# Single Chassis
				else:
					fpc = 0
					print "Model:\t\t" + lan_router[hostname]['chassis_mod']
					print "-" * 95
					print "FPC " + str(fpc) + ":\t" + lan_router[hostname]['chassis_mod']
					for pic in lan_router[hostname]['interfaces']['physical'][fpc].keys():
						#pp.pprint(lan_router[hostname])
						# General modules (inclduing VCP, Expansion, Builtin)
						if(isinstance( pic, ( int, long ) )):
							module_mod = lan_router[hostname]['interfaces']['physical'][fpc][pic]['module_mod']
							# If it's a module
							if module_mod in modular_model.keys():
								if 'VCP' in modular_model[module_mod]['intf_type']:
									print "\tPIC " + str(pic) + "\t(" + lan_router[hostname]['interfaces']['physical'][fpc][pic]['module_type'] + "):\t" + \
										lan_router[hostname]['interfaces']['physical'][fpc][pic]['module_mod'] + " (vcp)"
								else:
									print "\tPIC " + str(pic) + "\t(" + lan_router[hostname]['interfaces']['physical'][fpc][pic]['module_type'] + "):\t" + \
										lan_router[hostname]['interfaces']['physical'][fpc][pic]['module_mod']
							# If it's native
							else:
								print "\tPIC " + str(pic) + "\t(" + lan_router[hostname]['interfaces']['physical'][fpc][pic]['module_type'] + "):\t" + \
									lan_router[hostname]['interfaces']['physical'][fpc][pic]['module_mod']						
							# Check for auxillary modules (EX4300-UM-4XSFPP)
							if lan_router[hostname]['interfaces']['physical'][fpc][pic].has_key('aux_mod'):
								print "\tPIC " + str(pic) + "\t(" + lan_router[hostname]['interfaces']['physical'][fpc][pic]['aux_type'] + "):\t" + \
									lan_router[hostname]['interfaces']['physical'][fpc][pic]['aux_mod']
					print "=" * 95
			# For Modular Chassis 
			else:
				print "Model:\t\t" + lan_router[hostname]['chassis_mod']
				for fpc in sorted(lan_router[hostname]['interfaces']['physical'].keys()):
					print "-" * 95
					print "FPC " + str(fpc) + ":\t" + lan_router[hostname]['interfaces']['physical'][fpc]['fpc_mod']
					print "-" * 95
				print "=" * 95
			# Display Chassis Visualization
			displayChassisHardware(hostname, "Both")
		# Should only match WAN system
		else:
			print "System Type:\twan"
			print "Model:"
			for wanlink in wan_router[hostname]['intf_name']:
				print "Link:\t" + wanlink
	
# Create a WAN device
def addWANDevice():
	wan_hostname = getInputAnswer("Enter a hostname")
	wan_router.update({ wan_hostname : {} })
	wan_intf = []
	while True:
		wan_intfname = getInputAnswer("Enter " + wan_hostname + " interface name")
		if wan_intfname == "q":
			wan_router[wan_hostname].update({ 'intf_name' : wan_intf })
			break
		else:
			wan_intf.append(wan_intfname)
	is_preferred = getYNAnswer("Is " + wan_hostname + " the preferred egress")
	if is_preferred == "y":
		wan_router[wan_hostname].update({ 'pref_egress' : True })
	else:
		wan_router[wan_hostname].update({ 'pref_egress' : False })
		
	pp.pprint(wan_router)

# Delete system menu
def deleteChassisMenu():
	# Create option list
	option = []
	for hostname in sorted(lan_router.keys()):
		option.append(hostname)
	option.append("Go Back")

	# Display the chassis members and ask which one to remove
	question = "Select chassis to delete"
	selection = getOptionAnswer(question, option)
	
	# Delete entire system
	if selection != "Go Back":
		del lan_router[selection]

# Create a MDF/IDF device
def addDeviceMenu():
	question = "Select a system type to create"
	option = [ "Single Chassis", "Virtual Chassis", "Delete Chassis", "Show Devices", "Go Back" ]
	selection = ""
	while selection != 4:
		selection = getOptionTRAnswer(question, option)
		# Single Chassis Selection
		if selection == 0:	
			addSystemSingleChassis(setSystemCommon())
		# Virtual Chassis Selection
		elif selection == 1:			
			createVC()
		elif selection == 2:
			deleteChassisMenu()			
		elif selection == 3:
			showDeviceMenu()
		else: break

# Modify Menu
def modChassisMenu():
	displayChassisBasic()
	hostname = selectChassisMenu()
	question = "Please choose an action" 
	if hostname is not None:
		if lan_router[hostname]['chassis_type'] == 'modular':
			while True:
				option = [ "Change Hostname", "Add FPCs", "Delete FPCs", "Show Devices", "Go Back" ]
				print "Device: " + hostname
				selection = getOptionTRAnswer(question, option)
				if selection == 0:
					setSystemHostname(selectChassisMenu('single'))
				elif selection == 1:
					addFPC(hostname)
				elif selection == 2:
					delFPC(hostname)
				elif selection == 3:
					showDeviceMenu()
				else:break
				
		elif lan_router[hostname]['is_vc']:
			while True:
				option = [ "Change Hostname", "Add Member", "Delete Member", "Show Devices", "Go Back" ]
				print "Device: " + hostname
				selection = getOptionTRAnswer(question, option)
				if selection == 0:
					setSystemHostname(hostname)
				elif selection == 1:
					addSystemVirtualChassis(hostname, nextMember(hostname))
				elif selection == 2:
					delSystemChassisMenu(hostname)
				elif selection == 3:
					showDeviceMenu()					
				else:break
				
		else:
			while True:
				option = [ "Change Hostname", "Add Modules", "Delete Modules", "Show Devices", "Go Back" ]
				print "Device: " + hostname
				selection = getOptionTRAnswer(question, option)
				if selection == 0:
					setSystemHostname(hostname)
				elif selection == 1:
					addModules(hostname, 'expan', 0)
				elif selection == 2:
					delModules(hostname)
				elif selection == 3:
					showDeviceMenu()
				else:break

# Asks user to select a chassis and return the name vc/single/all
def selectChassisMenu(chassis_type="all"):
	# Create option list
	option = []
	for hostname in sorted(wan_router.keys()):
		option.append(hostname)
	for hostname in sorted(lan_router.keys()):
		# For virtual chassis
		if chassis_type == "vc":
			if lan_router[hostname]['chassis_type'] == 'stackable' and lan_router[hostname]['is_vc']:
				option.append(hostname)
		# For single chassis
		elif chassis_type == "single":
			# Stackable Chassis
			if lan_router[hostname]['chassis_type'] == 'stackable' and not lan_router[hostname]['is_vc']:
				option.append(hostname)
			# Modular Chassis
			elif lan_router[hostname]['chassis_type'] == 'modular':
				option.append(hostname)
		# For ALL chassis
		else:
			option.append(hostname)
	option.append("Go Back")

	# Display the chassis members and ask which one to remove
	question = "Select chassis"
	selection = getOptionAnswer(question, option)
	
	# If ask to "Go Back" return None
	if selection == "Go Back":
		return False
	# Otherwise, return the chassis name
	else:
		return selection

##################################################	
# ========== SINGLE CHASSIS FUNCTIONS ========== #	
##################################################	

# Creates a single chassis system
def addSystemSingleChassis(hostname, fpc=0):
	if hostname is not None:
		# Set Router Model
		model = getOptionAnswer("Select the router model", system_model.keys())
	
		# If this is a modular system
		if system_model[model]['chassis_type'] == "modular":
			# Set Dictionary Format for chassis
			lan_router[hostname].update({ 'chassis_type' : 'modular' })
			lan_router[hostname].update({ 'is_vc' : False })
			lan_router[hostname].update({ 'chassis_mod' : model })		
			lan_router[hostname].update({ 'interfaces' : {} })
			lan_router[hostname]['interfaces'].update({ 'physical' : {} })
			
			# Add first FPC, must have at least one RE
			addFPC(hostname)
			
			# Add FPCs to chassis
			getfpc = 'y'
			while getfpc is 'y':
				getfpc = getYNAnswer("Add another FPC")
				if getfpc is 'y':
					addFPC(hostname)
			
		# If this is a stackable system
		else:
			# Set Dictionary Format for stackable
			lan_router[hostname].update({ 'chassis_type' : 'stackable' })
			lan_router[hostname].update({ 'is_vc' : False })
			lan_router[hostname].update({ 'chassis_mod' : model })
		
			# Add Native Ports
			if fpc == 0:
				lan_router[hostname].update({ 'interfaces' : {} })
				lan_router[hostname]['interfaces'].update({ 'physical' : {} })
			addNativeInterfaces(hostname, model, False, fpc, 0)
			
			# Add Built-in Modules
			addModules(hostname, 'builtin', fpc)
			
			# Add Expansion Modules
			print "Enter Expansion..."
			
			if getYNAnswer("Will this system have expansion modules") == 'y':
				addModules(hostname, 'expan', fpc)
			print "Finished system creation."

# Adding Modules
def addModules(hostname, module_type, fpc=0):
	print "\n************************************"
	print "* Add Expansion Modules to Chassis *"
	print "************************************\n"	
	# Common Variables
	expan_mod = ""
	expan_slot = ""
	model = ""
	# Determine if this is a virtual chassis module or standalone to reference correct chassis mod
	if lan_router[hostname]['chassis_mod'] == 'Virtual_Chassis':
		model = lan_router[hostname]['interfaces']['physical'][fpc]['fpc_mod']
	else:
		model = lan_router[hostname]['chassis_mod']
	# Build Expansion Modules
	if module_type == 'expan':
		# Get Expansion Module
		question1 = "Select Expansion Module"
		opt1 = []
		for module in system_model[model]['expan_mods']:
			opt1.append(module)
		opt1.append("Go Back")
		while True:
			# Loop through possible expansion slots
			for slot in system_model[model]['expan_slots']:
				not_matched = True
				# Loop through keys under FPC
				for pic in lan_router[hostname]['interfaces']['physical'][fpc].keys():
					# Check if switch has this slot populated
					if str(slot) == str(pic):
						#print "Matched!!"
						not_matched = False
						if lan_router[hostname]['interfaces']['physical'][fpc][pic]['module_type'] == 'expan':
							print "PIC Slot " + str(pic) + " currently contains " + lan_router[hostname]['interfaces']['physical'][fpc][pic]['module_mod']
						else:
							print "PIC Slot " + str(pic)
						
				# This matches if nothing is matched in the for loop
				if not_matched:
					print "PIC Slot " + str(slot) + " is empty"
			# Ask user to select an expansion model to add
			expan_mod = getOptionAnswer(question1, opt1)
			
			if expan_mod == "Go Back":
				break
			else:
				# Get Available Slot
				question2 = "Select a slot"
				opt2 = []
				for slot in system_model[model]['expan_slots']:
					opt2.append(str(slot))
				opt2.append("Go Back")
				while True:
					# Ask user which slot to put the PIC in
					expan_slot = getOptionAnswer(question2, opt2)
					if expan_slot == "Go Back":
						break
					else:
						addModuleInterfaces(hostname, fpc, int(expan_slot), expan_mod)
						break
				
	# Build Built-In Modules
	elif module_type == 'builtin':
		opt1 = []
		opt2 = []
		for slot in system_model[model]['builtin_slots']:
			opt1.append(slot)
		for module in system_model[model]['builtin_mods']:
			opt2.append(module)
		# Combine lists into dict
		built_dict = dict(zip(opt1, opt2))
		
		# Loop over built-in slots/mods
		for builtin_slot, builtin_mod in built_dict.iteritems():
			addModuleInterfaces(hostname, fpc, int(builtin_slot), builtin_mod)

# Add chassis FPCs, includes linecards and routing engines
def addFPC(hostname):
	#pp.pprint(lan_router)
	# Get hosts chassis model
	chassis_model = lan_router[hostname]['chassis_mod']
	
	# Create option list
	option = []
	module = ""
	
	# Create a list of the possible modules
	if not lan_router[hostname]['interfaces']['physical'].keys():
		for module_mod in modular_model.keys():
			if chassis_model in modular_model[module_mod]['supported_chassis'] and "SRE" in module_mod:
				option.append(module_mod)
		option.append("Go Back")
		question = "No SREs detected, you MUST have at least one SRE"
		module = getOptionAnswer(question, option)

	else:
		# Display the chassis members and ask which one to add
		for module_mod in modular_model.keys():
			if chassis_model in modular_model[module_mod]['supported_chassis']:
				option.append(module_mod)
		option.append("Go Back")
		question = "Select module to add"
		module = getOptionAnswer(question, option)
		
	if module != "Go Back":
		# Possible FPCs
		possFPCs = []
		availFPCs = []

		# Check if this is an SRE or LINECARD
		if "SRE" in module:
			possFPCs = system_model[chassis_model]['sre_slots']
		else:
			possFPCs = system_model[chassis_model]['expan_slots']
		print "possFPCs: " + str(possFPCs)
		# Used FPCs on host
		usedFPCs = lan_router[hostname]['interfaces']['physical'].keys()
		print "usedFPCs: " + str(usedFPCs)
		# Determine available FPC slots
		for fpc in possFPCs:
			if fpc not in usedFPCs:
				availFPCs.append(str(fpc))
		availFPCs.append("Go Back")
		print "AvailFPCs"
		print availFPCs


		# Ask user to select an FPC
		question = "Select an FPC to add this module to"
		fpc_add = getOptionAnswer(question, availFPCs)

		#print "FPC_add: " + fpc_add

		if fpc_add != "Go Back":
			# Add interfaces
			print "Adding interfaces..."
			addChassisInterfaces(hostname, module, int(fpc_add))

# Delete chassis FPCs, includes linecards and routing engines
def delFPC(hostname):
	# Display the FPCs in the chassis
	if lan_router[hostname]['interfaces']['physical'].has_key():
		usedFPCs = lan_router[hostname]['interfaces']['physical'].keys()
		question = "Select an FPC to delete"
		fpc_delete = getOptionAnswer(question, map(str, usedFPCs))
		
		# Delete the chosen FPC from the lan_router dictionary
		try:
			del lan_router[hostname]['interfaces']['physical'][int(fpc_delete)]
		except Exception as exception:
			print "Failed deleting FPC " + fpc_delete
		finally:
			print "Successfully deleted FPC " + fpc_delete
	else:
		print "Error: No FPCs to delete"
	
# Adds interfaces to a chassis-based system
def addChassisInterfaces(hostname, fpc_mod, fpc):
	pic = 0
	# Get number of ports for this fpc model
	port_num = modular_model[fpc_mod]['port_num']

	# Build out base of interface heirarchy
	lan_router[hostname]['interfaces']['physical'].update({ fpc : {} })
	lan_router[hostname]['interfaces']['physical'][fpc].update({ 'fpc_mod' : fpc_mod })
	lan_router[hostname]['interfaces']['physical'][fpc].update({ pic : {} })
	print "Successfully added " + fpc_mod + " into FPC " + str(fpc) + "..."
	
	# Create ports
	for port in range(0, port_num):	
		lan_router[hostname]['interfaces']['physical'][fpc][pic].update({ port : {} })
		lan_router[hostname]['interfaces']['physical'][fpc][pic][port].update({ 'port' : port })
		lan_router[hostname]['interfaces']['physical'][fpc][pic][port].update({ 'is_linked' : False })
		lan_router[hostname]['interfaces']['physical'][fpc][pic][port].update({ 'is_bundled' : False })
	
	print "Successfully added interfaces...\n"

# Deleteing Modules for Single Chassis
def delModules(hostname, fpc=0):
	model = lan_router[hostname]['chassis_mod']
	filled_mod_list = []
	# Loop through possible expansion slots
	for slot in system_model[model]['expan_slots']:
		not_matched = True
		# Loop through keys under FPC
		for pic in lan_router[hostname]['interfaces']['physical'][fpc].keys():
			# Check if switch has this slot populated
			if str(slot) == str(pic):
				#print "Matched!!"
				not_matched = False
				if lan_router[hostname]['interfaces']['physical'][fpc][pic]['module_type'] == 'expan':
					print "Slot " + str(pic) + " currently contains " + lan_router[hostname]['interfaces']['physical'][fpc][pic]['module_mod']
					filled_mod_list.append(str(pic))
				else:
					print "Slot " + str(pic)
		# This matches if nothing is matched in the for loop
		if not_matched:
			print "Slot " + str(slot) + " is empty"
	#
	filled_mod_list.append("Go Back")
	if filled_mod_list:
		question = "Select a Module to Delete"
		select_mod = getOptionAnswer(question, filled_mod_list)
		if select_mod == "Go Back":
			print "Delete Cancelled!"
		else:
			del lan_router[hostname]['interfaces']['physical'][fpc][int(select_mod)]
			print "Deleted PIC!"

###################################################	
# ========== VIRTUAL CHASSIS FUNCTIONS ========== #	
###################################################	

# Create initial virtual chassis configuration
def createVC():
	# Run the basic system configuration
	print "\n**************************"
	print "* Create Virtual Chassis *"
	print "**************************\n"		
	host = setSystemCommon()
	# Add new chassis to stack
	addSystemVirtualChassis(host, nextMember(host))
	
# Determine the next available member number
def nextMember(hostname):
	#top_member = 0
	next_member = 0
	if 'interfaces' in lan_router[hostname]:
		index = 0
		for member in lan_router[hostname]['interfaces']['physical'].keys():
			if index == member:
				index += 1
			else:
				next_member = index
				break
		next_member = index
	
	return next_member
		
# Create virtual chassis system
def addSystemVirtualChassis(hostname, fpc=0):
	chassis_mod = ''
	# Keep looping through this until we are done adding chassis to the stack
	while True:
		options = []
		for model in system_model.keys():
			if system_model[model]['chassis_type'] == 'stackable':
				options.append(model)
		options.append('Go Back')
		chassis_mod = getOptionAnswer("Select a router model to add", options)
		if chassis_mod == "Go Back":
			break
		elif checkStackValid(hostname, chassis_mod):
			# Only do these things during the creation of FPC 0 (first FPC)
			if fpc == 0:
				# Set Dictionary Format for VC
				lan_router[hostname].update({ 'is_vc' : True })
				lan_router[hostname].update({ 'chassis_type' : 'stackable' })
				lan_router[hostname].update({ 'chassis_mod' : 'Virtual_Chassis' })
				# Set Native Ports
				lan_router[hostname].update({ 'interfaces' : {} })
				lan_router[hostname]['interfaces'].update({ 'physical' : {} })
			addNativeInterfaces(hostname, chassis_mod, True, fpc, 0)
		
			# Add Built-in Modules
			addModules(hostname, 'builtin', fpc)
		
			if getYNAnswer("Add an expansion modules") == 'y':
				addModules(hostname, 'expan', fpc)
			fpc += 1

# Menu for selecting which chassis to delete from a stack
def delSystemChassisMenu(hostname):
	# Get the number of chassis in this stack
	fpc_num = len(lan_router[hostname]['interfaces']['physical'].keys())
	
	# Check if there are at least 1 chassis
	if(fpc_num):
		# Create option list
		option = []
		for key in lan_router[hostname]['interfaces']['physical'].keys():
			model = lan_router[hostname]['interfaces']['physical'][key]['chassis_mod']
			option.append("Member " + str(key) + " (" + model + ")")
		option.append("Go Back")
		
		# Display the chassis members and ask which one to remove
		question = "Select chassis to delete"
		selection = ""
		print "Length: " + str(len(option))
		while selection != len(option)-1:
			selection = getOptionTRAnswer(question, option)
			if selection > 0 and selection < len(option)-1:
				delSystemChassis(hostname, selection)
				break

# Delete specified chassis from stack
def delSystemChassis(hostname, fpc):
	try:
		del lan_router[hostname]['interfaces']['physical'][fpc]
	except Exception as exception:
		print type(exception)
		print "Error deleteing FPC " + str(fpc)	

# Returns True or False if hostname is already in use
def isUniqueHostname(hostname):
	isUnique = True
	for host in lan_router.keys():
		if host == hostname:
			isUnique = False
			print "ERROR: This hostname is already used, please create a unique hostname."
	return isUnique

# Checks VC stack combinations, be sure its valid
def checkStackValid(hostname, modelAdd):
	ex4245_exists = False
	ex4300_exists = False
	ex4600_exists = False
	
	# Check if interfaces have already been created
	if lan_router[hostname].has_key('interfaces'):
		fpc_list = lan_router[hostname]['interfaces']['physical']

	
		# Determine what types of devices are in this stack already
		for fpc in fpc_list:
			model = lan_router[hostname]['interfaces']['physical'][fpc]['fpc_mod']

			matchEX4245 = re.match( r'^EX4[2,5][0-9]0', model )
			matchEX4300 = re.match( r'^EX4300', model )
			matchEX4600 = re.match( r'^EX4600', model )

			if matchEX4245:
				ex4245_exists = True
			elif matchEX4300:
				ex4300_exists = True
			elif matchEX4600:
				ex4600_exists = True
			
	# Check conditions to determine if new switch can be added to stack
	if re.match( r'^EX4[2,5][0-9]0', modelAdd ):
		if ex4300_exists or ex4600_exists:
			print "Model " + modelAdd + " and EX4300/EX4600 cannot be in the same stack."
			return False	
	elif re.match( r'^EX4300', modelAdd ):
		if ex4245_exists:
			print "Model " + modelAdd + " and EX4200/EX4500/EX4550 cannot be in the same stack."
			return False
		elif ex4600_exists:
			print "WARNING: EX4600 must be the RE in a mixed-mode stack if it includes" + modelAdd + "s."
	elif re.match( r'^EX4600', modelAdd ):
		if ex4245_exists:
			print "Model " + modelAdd + " and EX4200/EX4500/EX4550 cannot be in the same stack."
			return False
		elif ex4300_exists:
			print "WARNING: " + modelAdd + " must be the RE in a mixed-mode stack if it includes EX4300s."		

	return True

#############################################################
# =================== DISPLAY FUNCTIONS =================== #
#############################################################

# Display interfaces
def displayInterfaces(hostname):
	# Make sure hostname
	if hostname in lan_router.keys():
		# Option for displaying Virtual Chassis Interfaces
		print "\n" + "=" * 95
		print "Hostname: " + hostname
		if lan_router[hostname]['is_vc']:
			print "System Type: Virtual Chassis"			
			for fpc in lan_router[hostname]['interfaces']['physical'].keys():
				print "\n" + "=" * 95
				print "Member: " + str(fpc)
				print "Model\t\t\tFPC\tPIC\tPorts\tType\t\tSpeed\t\tPoE\tVCP"
				print "-" * 95
				printInterfaces(hostname, fpc, True)
		# Option for displaying Standalone Chassis Interfaces
		elif lan_router[hostname]['chassis_type'] == 'stackable':			
			for fpc in lan_router[hostname]['interfaces']['physical'].keys():
				model = lan_router[hostname]['chassis_mod']
				print "System Type: " + model
				print "\n" + "=" * 95
				print "Model\t\t\tFPC\tPIC\tPorts\tType\t\tSpeed\t\tPoE\tVCP"
				print "-" * 95
				printInterfaces(hostname, fpc, False)
		# Option for displaying Modular Chassis Intefaces
		else:
			print "System Type: " + lan_router[hostname]['chassis_mod']
			for fpc in lan_router[hostname]['interfaces']['physical'].keys():
				print "\n" + "=" * 95
				print "Slot: " + str(fpc)
				print "Model\t\t\tFPC\tPIC\tPorts\tType\t\tSpeed\t\tPoE\tVCP"
				print "-" * 95
				printInterfaces(hostname, fpc, False)
		print "\n" + "=" * 95
		displayChassisHardware(hostname, "Both")
		print "\n" + "=" * 95
	
	# Print WAN info
	elif hostname in wan_router.keys():
		print "\n" + "=" * 95
		print "Hostname: " + hostname
		print "System type: wan"
		print "Preferred Egress: " + str(wan_router[hostname]['pref_egress'])
		print "\n" + "=" * 95
		print "Ports"
		print "-" * 95
		for wanintf in wan_router[hostname]['intf_name']:
			print wanintf
		print "\n" + "=" * 95	
		
	# Print error about invalid hostname
	else:
		print "Invalid Host: " + hostname	

# Generic interface print function
def printInterfaces(hostname, fpc, is_vc):
	# This will print out the primary built-in ports for the chassis
	pic = 0
	# A stackable device
	if lan_router[hostname]['chassis_type'] == 'stackable':
		# Virtual Chassis system
		if is_vc:
			model = lan_router[hostname]['interfaces']['physical'][fpc]['fpc_mod']		
		# Single Chassis system
		else:
			model = lan_router[hostname]['chassis_mod']
		# Common output
		ports = system_model[model]['port_num']
		poe = system_model[model]['poe_capable']
		vcp = system_model[model]['vcp_capable']
		type_list = ''
		speed_list = ''
		type_len = len(system_model[model]['intf_type'])
		speed_len = len(system_model[model]['speed'])
		for intftype in system_model[model]['intf_type']:
			type_list += intftype
			if type_len > 1:
				type_list += "|"
				type_len -= 1
		for speed in system_model[model]['speed']:
			speed_list += speed
			if speed_len > 1:
				speed_list += "|"
				speed_len -= 1
	# A modular device
	else:
		model = lan_router[hostname]['interfaces']['physical'][fpc]['fpc_mod']
		ports = modular_model[model]['port_num']
		poe = modular_model[model]['poe_capable']
		vcp = modular_model[model]['vcp_capable']
		type_list = ''
		speed_list = ''
		type_len = len(modular_model[model]['intf_type'])
		speed_len = len(modular_model[model]['speed'])
		for intftype in modular_model[model]['intf_type']:
			type_list += intftype
			if type_len > 1:
				type_list += "|"
				type_len -= 1
		for speed in modular_model[model]['speed']:
			speed_list += speed
			if speed_len > 1:
				speed_list += "|"
				speed_len -= 1		
	
	# Print the line
	print model + str(useTab(model, 3)) + str(fpc) + "\t" + str(pic) + "\t" + str(ports) + "\t" + type_list + str(useTab(type_list, 2)) + speed_list + str(useTab(speed_list, 2)) + str(poe) + "\t" + str(vcp)

	if lan_router[hostname]['chassis_type'] == 'stackable':
		# This will handle displaying any expansion modules
		for pic in lan_router[hostname]['interfaces']['physical'][fpc].keys():
			# Make sure we're getting a PIC key
			if isinstance(pic,int):
				if pic != 0:
					model = lan_router[hostname]['interfaces']['physical'][fpc][pic]['module_mod']
					# Common Terms
					ports = modular_model[model]['port_num']
					vcp = modular_model[model]['vcp_capable']
					type_list = ''
					speed_list = ''
					type_len = len(modular_model[model]['intf_type'])
					speed_len = len(modular_model[model]['speed'])
					for intftype in modular_model[model]['intf_type']:
						type_list += intftype
						if type_len > 1:
							type_list += "|"
							type_len -= 1
					for speed in modular_model[model]['speed']:
						speed_list += speed
						if speed_len > 1:
							speed_list += "|"
							speed_len -= 1								
					print model + str(useTab(model, 3)) + str(fpc) + "\t" + str(pic) + "\t" + str(ports) + "\t" + type_list + str(useTab(type_list, 2)) + speed_list + str(useTab(speed_list, 2)) + str(poe) + "\t" + str(vcp)	
					
				# Check if aux exists 
				elif pic == 0 and lan_router[hostname]['interfaces']['physical'][fpc][pic]['has_aux']:
					model = lan_router[hostname]['interfaces']['physical'][fpc][pic]['aux_mod']
					# Common Terms
					ports = modular_model[model]['port_num']
					vcp = modular_model[model]['vcp_capable']
					type_list = ''
					speed_list = ''
					type_len = len(modular_model[model]['intf_type'])
					speed_len = len(modular_model[model]['speed'])
					for intftype in modular_model[model]['intf_type']:
						type_list += intftype
						if type_len > 1:
							type_list += "|"
							type_len -= 1
					for speed in modular_model[model]['speed']:
						speed_list += speed
						if speed_len > 1:
							speed_list += "|"
							speed_len -= 1								
					print model + str(useTab(model, 3)) + str(fpc) + "\t" + str(pic) + "\t" + str(ports) + "\t" + type_list + str(useTab(type_list, 2)) + speed_list + str(useTab(speed_list, 2)) + str(poe) + "\t" + str(vcp)

# Compute Tabs
def useTab(mystr, menuTab):
	tabSpc = 8
	useTabs = 0
	length = len(mystr)
	try:
		useTabs = math.ceil(((menuTab * tabSpc) - length) / 8.0)
	except:
		print "ERROR: Failure computing tabs"
	else:
		prtTabs = '\t' * int(useTabs)
		return prtTabs

# Create Tabs
def myTab(myStr):
	myTabbedStr = ""
	if len(myStr) < 8: myTabbedStr = myStr + "\t\t"
	elif len(myStr) < 16: myTabbedStr = myStr + "\t"
	else: myTabbedStr = myStr
	 
	return myTabbedStr
	
# Display basic chassis information
def displayChassisBasic():
	# Check if any hosts exist in dictionary
	if lan_router.keys() or wan_router.keys():		
		print "\n" + "="*63
		print "Hostname\tSystem Type\tModel\t\tVirtual Chassis"
		print "-"*63
		for hostname in sorted(wan_router.keys()):
			print myTab(hostname) + myTab("wan")
		
		for hostname in sorted(lan_router.keys()):
			if lan_router[hostname]['chassis_type'] == 'stackable':
				print myTab(hostname) + myTab(lan_router[hostname]['system_type']) + myTab(lan_router[hostname]['chassis_mod']) + str(lan_router[hostname]['is_vc'])	
			else:
				print myTab(hostname) + myTab(lan_router[hostname]['system_type']) + myTab(lan_router[hostname]['chassis_mod']) + 'False'			

	else:
		print "\n--- NO CHASSIS ---\n"
	print "\n" + "="*63

####################################
# ============= MAIN ============= #
####################################

# Main Function
def main():
	print("\nWelcome to Junos Configuration Creation Tool \n")
	mainMenu()
	
if __name__ == '__main__':
	main()