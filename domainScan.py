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
				DomainScan.jsonData[host] = { 'blockDate' : date, 'ispBlock' : {}, 'highlight': False}
		print 'Imported ' + str(counter) + ' domains'

	"""
		resolves all the domains, saves the value to the ip
	"""
	@staticmethod
	def scanDns(dnsAddres = '8.8.8.8'):
		import dns.resolver
		dnsResolver = dns.resolver.Resolver()
		dnsResolver.nameservers=[dnsAddres]

		for host in DomainScan.jsonData:
			DomainScan.jsonData[host]['ip'] = []
			try:
				response = dnsResolver.query(host, 'A') #only the first A record
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
		dnsResolver.timeout = 2
		dnsResolver.lifetime = 2

		for host in DomainScan.jsonData:
			DomainScan.jsonData[host]['isp'][isp] = {'status': 0,'dnsResponse':[]}
			try:
				response = dnsResolver.query(host, 'A') #only the first A record
				for eachRecord in response:
					DomainScan.jsonData[host]['isp'][isp]['dnsResponse'].append(str(eachRecord))

				#check if any of the original ip are in the response
				for eachIpRecord in DomainScan.jsonData[host]['ip']:
					found = False
					for eachResponseRecord in response:
						if str(eachIpRecord) == str(eachResponseRecord):
							found = True
							DomainScan.jsonData[host]['isp'][isp]['status'] = 0
							#the ip appeared in the isp response, so it (may) not be blocked
					if not Found:
						DomainScan.jsonData[host]['isp'][isp]['status'] = 2

			except: #socket.gaierror, err
				print 'Could not resolve: ' + host
				if DomainScan.jsonData[host]['ip'] == None:
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
	def testDns(dnsAddres = '8.8.8.8', host = 'google.com'):
		import dns.resolver
		dnsResolver = dns.resolver.Resolver()
		dnsResolver.nameservers= [dnsAddres]
		try:
			print host + ' resolved into ' + str(dnsResolver.query(host, 'A')[0]) + ' by ' + dnsAddres
		except:
			print 'error querying ' + str(host) + ' @' + dnsAddres

	@staticmethod
	def fix(ispName = 'vodafone'):
		for host in DomainScan.jsonData:
			#check if any of the original ip are in the response
			for eachIpRecord in DomainScan.jsonData[host]['ip']:
				found = False
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

			''''
			elif DomainScan.jsonData[host]['isp'][ispName]['blocked'] == True:
				DomainScan.jsonData[host]['isp'][ispName]['status'] = 2
			elif DomainScan.jsonData[host]['isp'][ispName]['blocked'] == False:
				DomainScan.jsonData[host]['isp'][ispName]['status'] = 0
			'''
			'''
			#add the reason
			DomainScan.jsonData[host]['reason'] = ''

			#fix status blocking for some domains
			if len(DomainScan.jsonData[host]['isp']['meo']['dnsResponse']) > 0 and DomainScan.jsonData[host]['isp']['meo']['dnsResponse'][0] == '213.13.145.120':
				#print str(DomainScan.jsonData[host]['isp']['meo']['dnsResponse'][0])
				DomainScan.jsonData[host]['isp']['meo']['blocked'] = True

			#Add other ISP's (empty)
			DomainScan.jsonData[host]['isp']['nos'] = { 'blocked':True, 'dnsResponse':[] }
			DomainScan.jsonData[host]['isp']['vodafone'] = { 'blocked':True, 'dnsResponse':[] }
			DomainScan.jsonData[host]['isp']['cabovisao'] = { 'blocked':True, 'dnsResponse':[] }
			'''

