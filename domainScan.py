#!/usr/bin/python

__author__ = 'ToFran'
__site__ = 'http://tofran.com/'

__license__ = "MIT"
__version__ = "1.2.1"
__maintainer__ = "Francisco Marques"
__email__ = "me@tofran.com"

##########

import socket
import dns.resolver
import json

##########

"""
	jsonData: the hosts data as a JSON object
"""
jsonData = {}


"""
	imports domains from a TXT file
	@param filePath the textfile
	@param date the date that the domain was blocked
"""
def importFromTXT(filePath, date, reason = 'copyright'):
	global jsonData
	counter = 0
	with open(filePath) as f:
		for line in hostFile:
			if host not in jsonData:
				counter += 1
				jsonData[host] = { 'blockDate' : date, 'ip' : [], 'isp' : { 'meo' : { 'dnsResponse' : [], 'status' : -2 }, 'nos' : { 'dnsResponse' : [], 'status' : -2 }, 'vodafone' : { 'dnsResponse' : [], 'status' : -2 } }, 'reason' : reason }
			else:
				print host + ' already in the list!'
	f.close()
	print 'Imported ' + str(counter) + ' domains'

"""
	imports domains from a file in JSON array
	@param filePath the json file
	@param date the date that the domain was blocked
"""
def importFromJsonArray(filePath, date, reason = 'copyright'):
	global jsonData
	counter = 0
	with open(filePath) as f:
		domainArray = json.load(f)
	f.close()

	for host in domainArray:
		if host not in jsonData:
			counter += 1
			jsonData[host] = { 'blockDate' : date, 'ip' : [], 'isp' : { 'meo' : { 'dnsResponse' : [], 'status' : -2 }, 'nos' : { 'dnsResponse' : [], 'status' : -2 }, 'vodafone' : { 'dnsResponse' : [], 'status' : -2 } }, 'reason' : reason }
		else:
			print host + ' already in the list!'
	print 'Imported ' + str(counter) + ' domains'

"""
	Load the data from a json file
"""
def loadJson(filePath):
	global jsonData
	with open(filePath) as f:
		jsonData = json.load(f)
	f.close()

"""
	Saves the data to a json file
"""
def outputToJsonFile(filePath):
	global jsonData
	with open(filePath, 'w') as f:
	    json.dump(jsonData, f, ensure_ascii=True, sort_keys=True, indent=4)
	f.close()

"""
	outputs the list of domains to a text file
"""
def outputToTXTFile(filePath):
	global jsonData
	with open(filePath, 'w') as f:
		for host in jsonData:
			f.write(host + '\n')
		f.close()

"""
	resolves all the domains, saves the value to the ip item (as an array)
"""
def scanDns(onlyNonScanned = False, dnsAddres = '8.8.8.8'):
	global jsonData
	import dns.resolver
	dnsResolver = dns.resolver.Resolver()
	dnsResolver.nameservers=[dnsAddres]
	dnsResolver.timeout = 1
	dnsResolver.lifetime = 1

	for host in jsonData:
		if(( not onlyNonScanned ) or ( onlyNonScanned and (( 'ip' not in jsonData[host] ) or ( len(jsonData[host]['ip']) == 0 )))):
			jsonData[host]['ip'] = []
			try:
				response = dnsResolver.query(host, 'A')
				for eachRecord in response:
					jsonData[host]['ip'].append(str(eachRecord))
			except:
				print 'Could not resolve: ' + host


'''
	scans all the domains with a specific dns (from an ISP)
	@param isp the name of the ISP
	@param dnsAddres the DNS address of the given ISP
'''
def scanDnsISP(isp, dnsAddres):
	global jsonData
	import dns.resolver
	dnsResolver = dns.resolver.Resolver()
	dnsResolver.nameservers=[dnsAddres]
	dnsResolver.timeout = 1
	dnsResolver.lifetime = 1

	for host in jsonData:
		if isp not in jsonData[host]['isp']:
			jsonData[host]['isp'][isp]= {'dnsResponse': []}
		try:
			response = dnsResolver.query(host, 'A')
			for eachRecord in response:
				jsonData[host]['isp'][isp]['dnsResponse'].append(str(eachRecord))

			#check if any of the original ip are in the response
			found = False
			for eachIpRecord in jsonData[host]['ip']:
				for eachResponseRecord in response:
					if str(eachIpRecord) == str(eachResponseRecord):
						found = True
						jsonData[host]['isp'][isp]['status'] = 0
						#the ip appeared in the isp response, so it (may) not be blocked
			if not found:
				jsonData[host]['isp'][isp]['status'] = 3
				#it replied, but with a different ip - DNS Redirect

		except: #(socket.gaierror, dns.exception.Timeout, dns.resolver.NXDOMAIN, dns.resolver.NoAnswer), err:
			print 'Could not resolve: ' + host
			if jsonData[host]['ip'] == None or len(jsonData[host]['ip']) == 0:
				jsonData[host]['isp'][isp]['status'] = -1
				# neither the (open) dns neither the isp replied, site may be have shut down - Can't be Resolved
			else:
				jsonData[host]['isp'][isp]['status'] = 1
				#Neither the reference DNS neither the ISP's DNS could resolve

"""
	Prints the data to the screen, yey
"""
def printData():
	global jsonData
	print json.dumps(jsonData, ensure_ascii=True, sort_keys=True, indent=1)


'''
	Tests a dns (prints to the console)
	@param dnsAddres the dns address
	@param host the host to resolve
'''
def testDns( dnsAddres = '8.8.8.8', host = 'google.com'):
	global jsonData
	dnsResolver = dns.resolver.Resolver()
	dnsResolver.nameservers= [dnsAddres]
	try:
		print host + ' resolved into ' + str(dnsResolver.query(host, 'A')[0]) + ' by ' + dnsAddres
	except:
		print 'error querying ' + str(host) + ' @' + dnsAddres


'''
	Generates and prints ISP scores based on the status of each domain!
	(Less is better)
'''
def printScores():
	global jsonData
	print 'Scores:'
	scores = dict()
	for host in jsonData:
		for eachIsp in jsonData[host]['isp']:
			if jsonData[host]['isp'][eachIsp]['status'] > 0:
				if eachIsp in scores:
					scores[eachIsp] += jsonData[host]['isp'][eachIsp]['status']
				else:
					scores[eachIsp] = jsonData[host]['isp'][eachIsp]['status']

	for isp, score in scores.iteritems():
		print isp + ': ' + str(score)


'''''''''
	These are some stupid methods to fix/destroy the data - to make really specific things...
'''
#fix the status
def fixStatus(ispName = 'meo'):
	global jsonData
	for host in jsonData:
		if not jsonData[host][ispName]['status'] == -2:
			#check if any of the original ip are in the response
			found = False
			for eachIpRecord in jsonData[host]['ip']:
				for eachResponseRecord in jsonData[host]['isp'][ispName]['dnsResponse']:
					if str(eachIpRecord) == str(eachResponseRecord):
						found = True
						jsonData[host]['isp'][ispName]['status'] = 0
						#the ip appeared in the isp response, so it (may) not be blocked
			if not found:
				jsonData[host]['isp'][ispName]['status'] = 2

			if len(jsonData[host]['isp'][ispName]['dnsResponse']) == 0:
				if len(jsonData[host]['ip']) == 0:
					jsonData[host]['isp'][ispName]['status'] = -1
				else:
					jsonData[host]['isp'][ispName]['status'] = 1
#copy reasons from another json
def fix_copyReasonsFromAnotherFile(filePath = 'reasons.json'):
	global jsonData
	with open(filePath) as inFile:
		jsonReasons = json.load(inFile)
	for host in jsonReasons:
		if 'reason' in jsonReasons[host]:
			jsonData[host]['reason'] = jsonReasons[host]['reason']
#add -2 status to domains without status
def fix_addMissingStatus(filePath = 'reasons.json'):
	global jsonData
	for host in jsonData:
		for eachIsp in jsonData[host]['isp']:
			if 'status' not in jsonData[host]['isp'][eachIsp]:
				jsonData[host]['isp'][eachIsp]['status'] = -2
#add missing reason
def fix_addMissingStatus(reason = 'Copyright'):
	global jsonData
	for host in jsonData:
		if 'reason' not in jsonData[host]:
			jsonData[host]['reason'] = reason
''''''''''''

if __name__ == '__main__':
	loadJson('blockList.json')
	importFromJsonArray('newsites.json', '2016-01')
	#importFromTXT('newhosts.txt', '2016-01')

	#scanDns(True)
	#testDns('meo.pt', '192.168.1.254')
	#scanDnsISP('vodafone', '192.168.1.254')

	#printData()
	#printScores()

	outputToJsonFile('new.json')
	outputToTXTFile('new.txt')
	print 'done!'
