# File: storage.py
# Author: Tyler Jordan
# Modified: 10/2/2015

import sys

system_model = {
	'EX4550-32F':{
		'chassis_type' : 'stackable',
		'intf_type' : [ 'SFP', 'SFP+' ],
		'port_num' : 32,
		'speed' : [ '1G', '10G' ],
		'poe_capable' : False,
		'vcp_capable' : '10G',
		'builtin_slots' : [],
		'builtin_mods' : [],
		'expan_slots' : [ 1, 2 ],
		'expan_mods' :  [ 'EX4550-EM-8XSFP', 'EX4550-EM-8XT', 'EX4550-EM-2XQSFP', 'EX4550-VC-128G' ]
	},
	'EX4550-32T':{
		'chassis_type' : 'stackable',
		'intf_type' : [ 'RJ45' ],
		'port_num' : 32,
		'speed' : [ '100M', '1G', '10G' ],
		'poe_capable' : True,
		'vcp_capable' : 'NONE',		
		'builtin_slots' : [],
		'builtin_mods' : [],
		'expan_slots' : [ 1, 2 ],
		'expan_mods' : [ 'EX4550-EM-8XSFP', 'EX4550-EM-8XT', 'EX4550-EM-2XQSFP', 'EX4550-VC-128G' ]
	},
	'EX4300-48P':{
		'chassis_type' : 'stackable',
		'intf_type' : [ 'RJ45' ],
		'port_num' : 48,
		'speed' : [ '10M', '100M', '1G' ],
		'poe_capable' : True,
		'vcp_capable' : 'NONE',
		'builtin_slots' : [ 1 ],
		'builtin_mods' : [ 'EX4300-UM-4XQSFP' ],
		'expan_slots' : [ 2 ],
		'expan_mods' : [ 'EX4300-EM-4XSFP' ]
	},
	'EX4300-32F':{
		'chassis_type' : 'stackable',
		'intf_type' : [ 'SFP' ],
		'port_num' : 32,
		'speed' : [ '1G' ],
		'poe_capable' : False,
		'vcp_capable' : 'NONE',
		'builtin_slots' : [ 0, 1 ],
		'builtin_mods' : [ 'EX4300-UM-4XSFP', 'EX4300-UM-2XQSFP' ],
		'expan_slots' : [ 2 ],
		'expan_mods' : [ 'EX4300-EM-2XQSFP', 'EX4300-EM-8XSFP' ]
	},
	'EX6210':{
		'chassis_type' : 'modular',
		'sre_slots' : [ 4, 5 ],
		'sre_mods' : [ 'EX6200-SRE64-4XS' ],
		'expan_slots' : [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9 ],
		'expan_mods' : [ 'EX6200-48T', 'EX6200-48P', 'EX6200-48F' ]
	}
}

modular_model = {
	'EX4550-EM-8XSFP':{
		'intf_type' : [ 'SFP', 'SFP+' ],
		'port_num' : 8,
		'speed' : [ '1G', '10G' ],
		'poe_capable' : False,
		'vcp_capable' : '10G',
		'supported_chassis' : [ 'EX4550-32T', 'EX4550-32F' ],
		'built_in' : False
	},
	'EX4550-EM-8XT':{
		'intf_type' : [ 'RJ45' ],
		'port_num' : 8,
		'speed' : [ '100M', '1G', '10G' ],
		'poe_capable' : False,
		'vcp_capable' : 'NONE',
		'supported_chassis' : [ 'EX4550-32T', 'EX4550-32F' ],
		'built_in' : False		
	},
	'EX4550-EM-2XQSFP':{
		'intf_type' : [ 'QSFP+' ],
		'port_num' : 2,
		'speed' : [ '40G' ],
		'poe_capable' : False,
		'vcp_capable' : 'DEFAULT',
		'supported_chassis' : [ 'EX4550-32T', 'EX4550-32F' ],
		'built_in' : False	
	},
	'EX4550-VC-128G':{
		'intf_type' : [ 'VCP' ],
		'port_num' : 2,
		'speed' : [ '64G' ],
		'poe_capable' : False,
		'vcp_capable' : 'DEFAULT',
		'supported_chassis' : [ 'EX4550-32T', 'EX4550-32F' ],
		'built_in' : False
	},
	'EX4300-EM-4XSFP':{
		'intf_type' : [ 'SFP', 'SFP+' ],
		'port_num' : 4,
		'speed' : [ '1G', '10G' ],
		'poe_capable' : False,
		'vcp_capable' : '10G',
		'supported_chassis' : [ 'EX4300-24T', 'EX4300-24P', 'EX4300-48T', 'EX4300-48P' ],
		'built_in' : False
	},	
	'EX4300-UM-4XQSFP':{
		'intf_type' : [ 'QSFP+' ],
		'port_num' : 4,
		'speed' : [ '40G' ],
		'poe_capable' : False,
		'vcp_capable' : 'DEFAULT',
		'supported_chassis' : [ 'EX4300-24T', 'EX4300-24P', 'EX4300-48T', 'EX4300-48P' ],
		'built_in' : True
	},
	'EX4300-UM-2XQSFP':{
		'intf_type' : [ 'QSFP+' ],
		'port_num' : 2,
		'speed' : [ '40G' ],
		'poe_capable' : False,
		'vcp_capable' : 'DEFAULT',
		'supported_chassis' : [ 'EX4300-32F' ],
		'built_in' : True
	},
	'EX4300-EM-2XQSFP':{
		'intf_type' : [ 'QSFP+' ],
		'port_num' : 2,
		'speed' : [ '40G' ],
		'poe_capable' : False,
		'vcp_capable' : 'DEFAULT',
		'supported_chassis' : [ 'EX4300-32F' ],
		'built_in' : False
	},	
	'EX4300-UM-4XSFP':{
		'intf_type' : [ 'SFP', 'SFP+' ],
		'port_num' : 4,
		'speed' : [ '1G', '10G' ],
		'poe_capable' : False,
		'vcp_capable' : '10G',
		'supported_chassis' : [ 'EX4300-32F' ],
		'built_in' : True
	},
	'EX4300-EM-8XSFP':{
		'intf_type' : [ 'SFP', 'SFP+' ],
		'port_num' : 8,
		'speed' : [ '1G', '10G' ],
		'poe_capable' : False,
		'vcp_capable' : '10G',
		'supported_chassis' : [ 'EX4300-32F' ],
		'built_in' : False
	},
	'EX6200-48T':{
		'intf_type' : [ 'RJ45' ],
		'port_num' : 48,
		'speed' : [ '10M', '100M', '1G' ],
		'poe_capable' : False,
		'vcp_capable' : 'NONE',
		'supported_chassis' : [ 'EX6210' ],
		'built_in' : False
	},
	'EX6200-48P':{
		'intf_type' : [ 'RJ45' ],
		'port_num' : 48,
		'speed' : [ '10M', '100M', '1G' ],
		'poe_capable' : True,
		'vcp_capable' : 'NONE',
		'supported_chassis' : [ 'EX6210' ],
		'built_in' : False
	},
	'EX6200-48F':{
		'intf_type' : [ 'SFP' ],
		'port_num' : 48,
		'speed' : [ '1G' ],
		'poe_capable' : False,
		'vcp_capable' : 'NONE',
		'supported_chassis' : [ 'EX6210' ],
		'built_in' : False
	},
	'EX6200-SRE64-4XS':{
		'intf_type' : [ 'SFP+' ],
		'port_num' : 4,
		'speed' : [ '10G' ],
		'poe_capable' : False,
		'vcp_capable' : 'NONE',
		'supported_chassis' : [ 'EX6210' ],
		'built_in' : False
	}	
}
# 2xQSFP can have different PIC numbers
visual_modules = {
	'EX4300-EM-8XSFP': {
		'T2': [ 'e', '0', '2', '4', '6' ],
		'T3': [ 'e', '1', '3', '5', '7' ],
		'T5': [ 's3', '8x 1G/10G SFP/SFP+', 's4' ]
	},	
	'EX4300-EM-4XSFP': {
		'T2': [ 's25' ],
		'T3': [ 'e', '0', '1', '2', '3' ],
		'T5': [ 's6', '4x 1G/10G SFP/SFP+', 's5' ]
	},	
	'EX4300-EM-2XQSFP': {
		'T2': [ 's25' ],
		'T3': [ 's6', 'e', '0', '1', 's6' ],
		'T5': [ 's7', '2x 40G QSFP', 's7' ]
	},
	'EX4300-UM-4XSFP': {
		'T2': [ 's25' ],
		'T3': [ 'e', '32', '33', '34', '35' ],
		'T5': [ 's6', '4x 1G/10G SFP/SFP+', 's5' ]
	},
	'EX4300-UM-4XQSFP': {
		'T2': [ 's25' ],
		'T3': [ 'e', '0', '1', '2', '3' ],
		'T4': [ 's25' ],
		'T5': [ 's7', '4x 40G QSFP', 's7' ]
	},	
	'EX4300-UM-2XQSFP': {
		'T2': [ 's25' ],
		'T3': [ 's6', 'e', '0', '1', 's6' ],
		'T5': [ 's7', '2x 40G QSFP', 's7' ]
	},
	'EX4300-BLANK': {
		'T2': [ 's25' ],
		'T3': [ 's25' ],
		'T5': [ 's10', 'BLANK', 's10' ]
	},
	'EX4550-EM-8XSFP': {
		'T2': [ 'e', '0', '2', '4', '6' ],
		'T3': [ 'e', '1', '3', '5', '7' ],
		'T5': [ 's3', '8x 1G/10G SFP/SFP+', 's4' ]
	},
	'EX4550-EM-8XT': {
		'T2': [ 'e', '0', '2', '4', '6' ],
		'T3': [ 'e', '1', '3', '5', '7' ],
		'T5': [ 's3', '8x 10G BaseT', 's4' ]
	},
	'EX4550-EM-2XQSFP': {
		'T2': [ 's25' ],
		'T3': [ 's6', 'e', '0', '1', 's6' ],
		'T5': [ 's7', '2x 40G QSFP', 's7' ]
	},	
	'EX4550-VC-128G': {
		'T2': [ 's9', 'e', '1', 's9' ],
		'T3': [ 's9', 'e', '0', 's9' ],
		'T4': [ 's25' ],
		'T5': [ 's5', '2x 64G VCP', 's5' ]
	},
	'EX6200-48F': {
		'T2': [ 'e', '0', '2', '4', '6', '8', '10', '12', '14', '16', '18', '20', '22', '24', '26', '28', '30', '32', '34', '36', '38', '40', '42', '44', '46' ],
		'T3': [ 'e', '1', '3', '5', '7', '9', '11', '13', '15', '17', '19', '21', '23', '25', '27', '29', '31', '33', '35', '37', '39', '41', '43', '45', '47' ],
		'T4': [ 's5', '48x 1G SFP' ]
	},
	'EX6200-48T': {
		'T2': [ 'e', '0', '2', '4', '6', '8', '10', '12', '14', '16', '18', '20', '22', '24', '26', '28', '30', '32', '34', '36', '38', '40', '42', '44', '46' ],
		'T3': [ 'e', '1', '3', '5', '7', '9', '11', '13', '15', '17', '19', '21', '23', '25', '27', '29', '31', '33', '35', '37', '39', '41', '43', '45', '47' ],
		'T4': [ 's5', '48x 1G BaseT' ]
	},
	'EX6200-48P': {
		'T2': [ 'e', '0', '2', '4', '6', '8', '10', '12', '14', '16', '18', '20', '22', '24', '26', '28', '30', '32', '34', '36', '38', '40', '42', '44', '46' ],
		'T3': [ 'e', '1', '3', '5', '7', '9', '11', '13', '15', '17', '19', '21', '23', '25', '27', '29', '31', '33', '35', '37', '39', '41', '43', '45', '47' ],
		'T4': [ 's5', '48x 1G BaseT(PoE)' ]
	},	
	'EX6200-SRE64-4XS': {
		'T2': [ 's145' ],
		'T3': [ 's25', 'e', '0', '1', '2', '3', 's95'],
		'T4': [ 's5', '4x 1G/10G SFP/SFP+' ]
	},
	'EX6200-BLANK': {
		'T2': [ 's145' ],
		'T3': [ 's145' ],
		'T4': [ 's5', 'BLANK' ]
	}		
}
# hb = horizontal border, vb = vertical border, cb = corner border
visual_chassis = {
	'EX4300-32F': {
		'Front': {
			'T1': [ 'border', 's1', 'cb1', 'hb11', 'PIC 2', 'hb11', 'cb1', 's129', 'EX4300-32F', 's1', 'hb1', 's1', 'fpc', 'end' ],
			'T2': [ 'ports', 's1', 'vb1', 's1', 'pic2', 's1', 'vb1', 's1', 'e', '0', '2', '4', '6', 's3', 'e', '8', '10', '12', '14', 's3', 'e', '16', '18', '20', '22', 's3', 'e', '24', '26', '28', '30', 's18', 'end' ],
			'T3': [ 'ports', 's1', 'vb1', 's1', 'pic2', 's1', 'vb1', 's1', 'e', '1', '3', '5', '7', 's3', 'e', '9', '11', '13', '15', 's3', 'e', '17', '19', '21', '23', 's3', 'e', '25', '27', '29', '31', 's10', 'auxpic0', 'end' ],
			'T4': [ 'border', 's1', 'cb1', 'hb27', 'cb1', 'end' ],
			'T5': [ 'labels', 's3', 'pic2', 's53', '32x 1G SFP', 's58', 'auxpic0', 'end' ]
		},
		'Rear': {
			'T1': [ 'border', 's66', 'cb1', 'hb11', 'PIC 1', 'hb11', 'cb1', 's64', 'EX4300-32F', 's1', 'hb1', 's1', 'fpc', 'end' ],
			'T2': [ 'ports', 's66', 'vb1', 's27', 'vb1', 'end' ],
			'T3': [ 'ports', 's66', 'vb1', 's1', 'pic1', 's1', 'vb1', 'end' ],
			'T4': [ 'border', 's66', 'cb1', 'hb27', 'cb1', 'end' ],
			'T5': [ 'labels', 's70', 'pic1', 'end' ]
		}
	},
	'EX4300-48P': {
		'Front': {
			'T1': [ 'border', 's159', 'EX4300-48P', 's1', 'hb1', 's1', 'fpc', 'end' ],
			'T2': [ 'ports', 's1', 'e', '0', '2', '4', '6', '8', '10', '12', '14', '16', '18', '20', '22', '24', '26', '28', '30', '32', '34', '36', '38', '40', '42', '44', '46', 's2', 'bpic2', 'end' ],
			'T3': [ 'ports', 's1', 'e', '1', '3', '5', '7', '9', '11', '13', '15', '17', '19', '21', '23', '25', '27', '29', '31', '33', '35', '37', '39', '41', '43', '45', '47', 's2', 'vb1', 's1', 'pic2', 's1', 'vb1', 's1', 'end' ],
			'T4': [ 'border', 's148', 'cb1', 'hb27', 'cb1', 'end' ],
			'T5': [ 'labels', 's60', '48x 10M/100M/1G BaseT', 's68', 'pic2', 'end' ]
		},
		'Rear': {
			'T1': [ 'border', 's32', 'cb1', 'hb11', 'PIC 1', 'hb11', 'cb1', 's98', 'EX4300-48P', 's1', 'hb1', 's1', 'fpc', 'end' ],
			'T2': [ 'ports', 's32', 'vb1', 's27', 'vb1', 'end' ],
			'T3': [ 'ports', 's32', 'vb1', 's1', 'pic1', 's1', 'vb1', 'end' ],
			'T4': [ 'border', 's32', 'cb1', 'hb27', 'cb1', 'end' ],
			'T5': [ 'labels', 's35', 'pic1', 'end' ]
		}
	},	
	'EX4550-32T': {
		'Front': {
			'T1': [ 'border', 's1', 'cb1', 'hb11', 'PIC 1', 'hb11', 'cb1', 's129', 'EX4550-32T', 's1', 'hb1', 's1', 'fpc', 'end' ],
			'T2': [ 'ports', 's1', 'vb1', 's1', 'pic1', 's1', 'vb1', 's1', 'e', '0', '2', '4', '6', 's3', 'e', '8', '10', '12', '14', 's3', 'e', '16', '18', '20', '22', 's3', 'e', '24', '26', '28', '30', 'end' ],
			'T3': [ 'ports', 's1', 'vb1', 's1', 'pic1', 's1', 'vb1', 's1', 'e', '1', '3', '5', '7', 's3', 'e', '9', '11', '13', '15', 's3', 'e', '17', '19', '21', '23', 's3', 'e', '25', '27', '29', '31', 'end' ],
			'T4': [ 'border', 's1', 'cb1', 'hb27', 'cb1', 'end' ],
			'T5': [ 'labels', 's3', 'pic1', 's53', '32x 100M/1G/10G BaseT', 'end' ]
		},
		'Rear': {
			'T1': [ 'border', 's66', 'cb1', 'hb11', 'PIC 2', 'hb11', 'cb1', 's64', 'EX4550-32T', 's1', 'hb1', 's1', 'fpc', 'end' ],
			'T2': [ 'ports', 's66', 'vb1', 's1', 'pic2', 's1', 'vb1', 'end' ],
			'T3': [ 'ports', 's66', 'vb1', 's1', 'pic2', 's1', 'vb1', 'end' ],
			'T4': [ 'border', 's66', 'cb1', 'hb27', 'cb1', 'end' ],
			'T5': [ 'labels', 's70', 'pic2', 'end' ]
		}
	},	
	'EX4550-32F': {
		'Front': {
			'T1': [ 'border', 's1', 'cb1', 'hb11', 'PIC 1', 'hb11', 'cb1', 's129', 'EX4550-32F', 's1', 'hb1', 's1', 'fpc', 'end' ],
			'T2': [ 'ports', 's1', 'vb1', 's1', 'pic1', 's1', 'vb1', 's1', 'e', '0', '2', '4', '6', 's3', 'e', '8', '10', '12', '14', 's3', 'e', '16', '18', '20', '22', 's3', 'e', '24', '26', '28', '30', 'end' ],
			'T3': [ 'ports', 's1', 'vb1', 's1', 'pic1', 's1', 'vb1', 's1', 'e', '1', '3', '5', '7', 's3', 'e', '9', '11', '13', '15', 's3', 'e', '17', '19', '21', '23', 's3', 'e', '25', '27', '29', '31', 'end' ],
			'T4': [ 'border', 's1', 'cb1', 'hb27', 'cb1', 'end' ],
			'T5': [ 'labels', 's3', 'pic1', 's53', '32x 1G/10G SFP+', 'end' ]
		},
		'Rear': {
			'T1': [ 'border', 's66', 'cb1', 'hb11', 'PIC 2', 'hb11', 'cb1', 's64', 'EX4550-32F', 's1', 'hb1', 's1', 'fpc', 'end' ],
			'T2': [ 'ports', 's66', 'vb1', 's1', 'pic2', 's1', 'vb1', 'end' ],
			'T3': [ 'ports', 's66', 'vb1', 's1', 'pic2', 's1', 'vb1', 'end' ],
			'T4': [ 'border', 's66', 'cb1', 'hb27', 'cb1', 'end' ],
			'T5': [ 'labels', 's70', 'pic2', 'end' ]
		}
	},
	'EX6210': {
		'Front': {
			'S0': {
				'T1': [ 'border', 's1', 'cb1', 'hb151', 'cb1', 'end' ],
				'T2': [ 'ports', 's1', 'vb1', 's3', 'slot', 's3', 'vb1', 'end' ],
				'T3': [ 'ports', 's1', 'vb1', 's3', 'slot', 's3', 'vb1', 'end' ],
				'T4': [ 'labels', 's1', 'vb1', 's60', 'slot', 'dyns154', 'vb1', 'slot_num', 'end' ],
				'T5': [ 'border', 's1', 'cb1', 'hb151', 'cb1', 'end' ]
			},
			'S1': {
				'T1': [ 'border', 's1', 'cb1', 'hb151', 'cb1', 'end' ],
				'T2': [ 'ports', 's1', 'vb1', 's3', 'slot', 's3', 'vb1', 'end' ],
				'T3': [ 'ports', 's1', 'vb1', 's3', 'slot', 's3', 'vb1', 'end' ],
				'T4': [ 'labels', 's1', 'vb1', 's60', 'slot', 'dyns154', 'vb1', 'slot_num', 'end' ],
				'T5': [ 'border', 's1', 'cb1', 'hb151', 'cb1', 'end' ]
			},
			'S2': {
				'T1': [ 'border', 's1', 'cb1', 'hb151', 'cb1', 'end' ],
				'T2': [ 'ports', 's1', 'vb1', 's3', 'slot', 's3', 'vb1', 'end' ],
				'T3': [ 'ports', 's1', 'vb1', 's3', 'slot', 's3', 'vb1', 'end' ],
				'T4': [ 'labels', 's1', 'vb1', 's60', 'slot', 'dyns154', 'vb1', 'slot_num', 'end' ],
				'T5': [ 'border', 's1', 'cb1', 'hb151', 'cb1', 'end' ]
			},
			'S3': {
				'T1': [ 'border', 's1', 'cb1', 'hb151', 'cb1', 'end' ],
				'T2': [ 'ports', 's1', 'vb1', 's3', 'slot', 's3', 'vb1', 'end' ],
				'T3': [ 'ports', 's1', 'vb1', 's3', 'slot', 's3', 'vb1', 'end' ],
				'T4': [ 'labels', 's1', 'vb1', 's60', 'slot', 'dyns154', 'vb1', 'slot_num', 'end' ],
				'T5': [ 'border', 's1', 'cb1', 'hb151', 'cb1', 'end' ]
			},
			'S4': {
				'T1': [ 'border', 's1', 'cb1', 'hb151', 'cb1', 'end' ],
				'T2': [ 'ports', 's1', 'vb1', 's3', 'slot', 's3', 'vb1', 'end' ],
				'T3': [ 'ports', 's1', 'vb1', 's3', 'slot', 's3', 'vb1', 'end' ],
				'T4': [ 'labels', 's1', 'vb1', 's60', 'slot', 'dyns154', 'vb1', 'slot_num', 'end' ],
				'T5': [ 'border', 's1', 'cb1', 'hb151', 'cb1', 'end' ]
			},
			'S5': {
				'T1': [ 'border', 's1', 'cb1', 'hb151', 'cb1', 'end' ],
				'T2': [ 'ports', 's1', 'vb1', 's3', 'slot', 's3', 'vb1', 'end' ],
				'T3': [ 'ports', 's1', 'vb1', 's3', 'slot', 's3', 'vb1', 'end' ],
				'T4': [ 'labels', 's1', 'vb1', 's60', 'slot', 'dyns154', 'vb1', 'slot_num', 'end' ],
				'T5': [ 'border', 's1', 'cb1', 'hb151', 'cb1', 'end' ]
			},
			'S6': {
				'T1': [ 'border', 's1', 'cb1', 'hb151', 'cb1', 'end' ],
				'T2': [ 'ports', 's1', 'vb1', 's3', 'slot', 's3', 'vb1', 'end' ],
				'T3': [ 'ports', 's1', 'vb1', 's3', 'slot', 's3', 'vb1', 'end' ],
				'T4': [ 'labels', 's1', 'vb1', 's60', 'slot', 'dyns154', 'vb1', 'slot_num', 'end' ],
				'T5': [ 'border', 's1', 'cb1', 'hb151', 'cb1', 'end' ]
			},
			'S7': {
				'T1': [ 'border', 's1', 'cb1', 'hb151', 'cb1', 'end' ],
				'T2': [ 'ports', 's1', 'vb1', 's3', 'slot', 's3', 'vb1', 'end' ],
				'T3': [ 'ports', 's1', 'vb1', 's3', 'slot', 's3', 'vb1', 'end' ],
				'T4': [ 'labels', 's1', 'vb1', 's60', 'slot', 'dyns154', 'vb1', 'slot_num', 'end' ],
				'T5': [ 'border', 's1', 'cb1', 'hb151', 'cb1', 'end' ]
			},
			'S8': {
				'T1': [ 'border', 's1', 'cb1', 'hb151', 'cb1', 'end' ],
				'T2': [ 'ports', 's1', 'vb1', 's3', 'slot', 's3', 'vb1', 'end' ],
				'T3': [ 'ports', 's1', 'vb1', 's3', 'slot', 's3', 'vb1', 'end' ],
				'T4': [ 'labels', 's1', 'vb1', 's60', 'slot', 'dyns154', 'vb1', 'slot_num', 'end' ],
				'T5': [ 'border', 's1', 'cb1', 'hb151', 'cb1', 'end' ]
			},
			'S9': {
				'T1': [ 'border', 's1', 'cb1', 'hb151', 'cb1', 'end' ],
				'T2': [ 'ports', 's1', 'vb1', 's3', 'slot', 's3', 'vb1', 'end' ],
				'T3': [ 'ports', 's1', 'vb1', 's3', 'slot', 's3', 'vb1', 'end' ],
				'T4': [ 'labels', 's1', 'vb1', 's60', 'slot', 'dyns154', 'vb1', 'slot_num', 'end' ],
				'T5': [ 'border', 's1', 'cb1', 'hb151', 'cb1', 'end' ]
			}
		}
	}
}
