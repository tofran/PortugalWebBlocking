#!/usr/bin/python

__author__ = 'ToFran'
__site__ = 'http://tofran.com/'

##########

import socket
import dns.resolver
import json

##########

class DomainScan(object):

	"""
		Atributes:
			jsonData: the hosts data as a JSON object
	"""
	jsonData = {}

	"""
		imports domains from a file
		@param date the date that the domain was blocked
	"""
	@staticmethod
	def importFromTXT(filePath, date):
		counter = 0
		hostFile = open(filePath)
		while True:
			host = hostFile.readline().rstrip()

			if not host:
				break

			if host not in DomainScan.jsonData:
				counter += 1
				DomainScan.jsonData[host] = { 'blockDate' : date, 'highlight' : False, 'ip' : [], 'isp' : { 'cabovisao' : { 'dnsResponse' : [], 'status' : -2 }, 'meo' : { 'dnsResponse' : [], 'status' : -2 }, 'nos' : { 'dnsResponse' : [], 'status' : -2 }, 'vodafone' : { 'dnsResponse' : [], 'status' : -2 } }, 'reason': 'Copyright'}
			else:
				print host + ' already in the list!'
		print 'Imported ' + str(counter) + ' domains'

	"""
		resolves all the domains, saves the value to the ip
	"""
	@staticmethod
	def scanDns(onlyNonScanned = False, dnsAddres = '8.8.8.8'):
		import dns.resolver
		dnsResolver = dns.resolver.Resolver()
		dnsResolver.nameservers=[dnsAddres]
		dnsResolver.timeout = 1
		dnsResolver.lifetime = 1

		for host in DomainScan.jsonData:
			if(( not onlyNonScanned ) or ( onlyNonScanned and (( 'ip' not in DomainScan.jsonData[host] ) or ( len(DomainScan.jsonData[host]['ip']) == 0 )))):
				DomainScan.jsonData[host]['ip'] = []
				try:
					response = dnsResolver.query(host, 'A')
					for eachRecord in response:
						DomainScan.jsonData[host]['ip'].append(str(eachRecord))
				except:
					print 'Could not resolve: ' + host

	'''
		scans all the domains with a specific dns from a given ISP and its IP(dns)
		this method duplicates some code from the mathod above #laziness
		the dns parameter is not working (crashes if dnsResolver.nameservers(dns))
		@todo fix this ^^
	'''
	@staticmethod
	def scanDnsISP(isp, dnsAddres):
		import dns.resolver
		dnsResolver = dns.resolver.Resolver()
		dnsResolver.nameservers=[dnsAddres]
		dnsResolver.timeout = 1
		dnsResolver.lifetime = 1

		for host in DomainScan.jsonData:
			if isp not in DomainScan.jsonData[host]['isp']:
				DomainScan.jsonData[host]['isp'][isp]= {'dnsResponse': []}
			try:
				response = dnsResolver.query(host, 'A')
				for eachRecord in response:
					DomainScan.jsonData[host]['isp'][isp]['dnsResponse'].append(str(eachRecord))

				#check if any of the original ip are in the response
				found = False
				for eachIpRecord in DomainScan.jsonData[host]['ip']:
					for eachResponseRecord in response:
						if str(eachIpRecord) == str(eachResponseRecord):
							found = True
							DomainScan.jsonData[host]['isp'][isp]['status'] = 0
							#the ip appeared in the isp response, so it (may) not be blocked
				if not found:
					DomainScan.jsonData[host]['isp'][isp]['status'] = 2

			except: #(socket.gaierror, dns.exception.Timeout, dns.resolver.NXDOMAIN, dns.resolver.NoAnswer), err:
				print 'Could not resolve: ' + host
				if DomainScan.jsonData[host]['ip'] == None or len(DomainScan.jsonData[host]['ip']) == 0:
					DomainScan.jsonData[host]['isp'][isp]['status'] = -1
					# neither the (open) dns neither the isp replied, site may be have shut down
				else:
					DomainScan.jsonData[host]['isp'][isp]['status'] = 1

	"""
		Load the data from a file
	"""
	@staticmethod
	def loadJson(filePath):
		with open(filePath) as inFile:
			DomainScan.jsonData = json.load(inFile)

	"""
		Saves the data to a file
	"""
	@staticmethod
	def outputToFile(filePath):
		with open(filePath, 'w') as outfile:
		    json.dump(DomainScan.jsonData, outfile, ensure_ascii=True, sort_keys=True, indent=1)

	"""
		Prints the data to the screen yey
	"""
	@staticmethod
	def printData():
		print json.dumps(DomainScan.jsonData, ensure_ascii=True, sort_keys=True, indent=1)

	'''
		This is a stupid method to fix/destroy the data to make really specific things...
		I cant describe waht it does because I update it every time
	'''

	@staticmethod
	def testDns(host = 'google.com', dnsAddres = '8.8.8.8'):
		import dns.resolver
		dnsResolver = dns.resolver.Resolver()
		dnsResolver.nameservers= [dnsAddres]
		try:
			print host + ' resolved into ' + str(dnsResolver.query(host, 'A')[0]) + ' by ' + dnsAddres
		except:
			print 'error querying ' + str(host) + ' @' + dnsAddres

	@staticmethod
	def fixStatus(ispName = 'meo'):
		for host in DomainScan.jsonData:
			#check if any of the original ip are in the response
			found = False
			for eachIpRecord in DomainScan.jsonData[host]['ip']:
				for eachResponseRecord in DomainScan.jsonData[host]['isp'][ispName]['dnsResponse']:
					if str(eachIpRecord) == str(eachResponseRecord):
						found = True
						DomainScan.jsonData[host]['isp'][ispName]['status'] = 0
						#the ip appeared in the isp response, so it (may) not be blocked
			if not found:
				DomainScan.jsonData[host]['isp'][ispName]['status'] = 2

			if len(DomainScan.jsonData[host]['isp'][ispName]['dnsResponse']) == 0:
				if len(DomainScan.jsonData[host]['ip']) == 0:
					DomainScan.jsonData[host]['isp'][ispName]['status'] = -1
				else:
					DomainScan.jsonData[host]['isp'][ispName]['status'] = 1

	@staticmethod
	def fix():
		for host in DomainScan.jsonData:
			#add -2 status to domains without status
			for eachIsp in DomainScan.jsonData[host]['isp']:
				if 'status' not in DomainScan.jsonData[host]['isp'][eachIsp]:
					DomainScan.jsonData[host]['isp'][eachIsp]['status'] = -2

			#add the reason
			DomainScan.jsonData[host]['reason'] = 'Copyright'

			'''
			#fix status blocking for some domains
			if len(DomainScan.jsonData[host]['isp']['meo']['dnsResponse']) > 0 and DomainScan.jsonData[host]['isp']['meo']['dnsResponse'][0] == '213.13.145.120':
				#print str(DomainScan.jsonData[host]['isp']['meo']['dnsResponse'][0])
				DomainScan.jsonData[host]['isp']['meo']['blocked'] = True

			#Add other ISP's (empty)
			DomainScan.jsonData[host]['isp']['nos'] = { 'blocked':True, 'dnsResponse':[] }
			DomainScan.jsonData[host]['isp']['vodafone'] = { 'blocked':True, 'dnsResponse':[] }
			DomainScan.jsonData[host]['isp']['cabovisao'] = { 'blocked':True, 'dnsResponse':[] }
			'''

