#!/usr/bin/python

__author__ = 'ToFran'
__site__ = 'http://tofran.com/'

__license__ = "MIT"
__version__ = "2.0"
__maintainer__ = "ToFran"
__email__ = "me@tofran.com"

##########

import socket, json, datetime, dns.resolver, urllib, logging

##########

#jsonData: the hosts data as a JSON object
jsonData = dict()

"""
	imports domains from a TXT file
	@param filePath the textfile
	@param date the date that the domain was blocked
"""
def importFromTXT(filePath, date, reason = 'copyright'):
	global jsonData
	result = {'added': [], 'alreadyInList': []}
	with open(filePath, 'r') as f:
		for domain in f:
			domain = host.strip()
			if add(domain, date, reason):
				result['added'].append(domain)
			else:
				result['alreadyInList'].append(domain)
	f.close()
	print json.dumps(result, ensure_ascii=True, sort_keys=True, indent=3)

"""
	imports domains from a file in JSON array
	@param filePath the json file
	@param date the date that the domain was blocked
	@param reason the reason
"""
def importFromJsonArray(filePath = None, date = None, reason = 'copyright', url = None):
	global jsonData
	domainArray = dict()
	if filePath is not None and url is None:
		with open(filePath, 'r') as f:
			domainArray = json.load(f)
		f.close()
	elif filePath is None and url is not None:
		domainArray = json.loads(urllib.urlopen(url).read())
	else:
		return

	result = {'added': []}
	if date is None:
		date = datetime.datetime.now().strftime('%Y-%m')

	for domain in domainArray:
		if add(domain, date, reason):
			result['added'].append(domain)
	print json.dumps(result, ensure_ascii=True, sort_keys=True, indent=3)

"""
	Add a domain or subdomain to the list
	@param filePath the json file
	@param date the date that the domain was blocked
	@param reason the reason
"""
def add(domain, date, reason):
	global jsonData
	default = { 'blockDate' : date, 'ip' : [], 'isp' : {}, 'reason' : reason }
	result = False
	part = domain.split('.')
	fqdn = part[-2] + '.' + part[-1]
	if domain.count('.') >= 2 and (part[-2] == 'co' or part[-2] == 'com'):
		fqdn = part[-3] + '.' + fqdn
	if fqdn not in jsonData['domains']:
		jsonData['domains'][fqdn] = {'hosts': {'@': default, 'www': default}}
		result = True
	if len(domain) > len(fqdn):
		subdomain = ''
		for i in range(0, len(part) - 2):
			subdomain += part[i] + '.'
		if subdomain[:-1] not in jsonData['domains'][fqdn]['hosts']:
			jsonData['domains'][fqdn]['hosts'][subdomain[:-1]] = default
			result = True
	return result

"""
	Load the data from a json file
"""
def loadJson(filePath):
	global jsonData
	with open(filePath, 'r') as f:
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
		for domain in jsonData['domains']:
			for sub in jsonData['domains'][domain]['hosts']:
				if sub == '@':
					sub = ''
				else:
					sub += '.'
				f.write(sub + domain + '\n')
		f.close()

"""
	resolves all the domains, saves the value to the ip item (as an array)
"""
def resolveAllReference(dnsAddres = '8.8.8.8', onlyNonScanned = False, debug = True):
	global jsonData
	#import dns.resolver
	dnsResolver = dns.resolver.Resolver()
	dnsResolver.nameservers = [dnsAddres]
	dnsResolver.timeout = 1
	dnsResolver.lifetime = 1
	jsonData['info']['reference']['lastScan'] = datetime.datetime.now().isoformat()
	for domain in jsonData['domains']:
		for subdomain in jsonData['domains'][domain]['hosts']:
			if (( not onlyNonScanned ) or
				( onlyNonScanned and (
				( 'ip' not in jsonData['domains'][domain]['hosts'][subdomain] ) or
				( len(jsonData['domains'][domain]['hosts'][subdomain]['ip']) == 0 )))
				):
					jsonData['domains'][domain]['hosts'][subdomain]['ip'] = []
					host = subdomain + '.' + domain if subdomain != '@' else domain
					try:
						response = dnsResolver.query(host, 'A')
						for eachRecord in response:
							jsonData['domains'][domain]['hosts'][subdomain]['ip'].append(str(eachRecord))
					except Exception as e:
						if debug: print 'ERROR (' + str(type(e).__name__) + '): ' + host
					except KeyboardInterrupt:
						raise

'''
	scans all the domains with a specific dns (from an ISP)
	@param isp the name of the ISP
	@param dnsAddres the DNS address of the given ISP
'''
def scanDnsISP(isp, dnsAddres, debug = True):
	global jsonData
	dnsResolver = dns.resolver.Resolver()
	dnsResolver.nameservers = [dnsAddres]
	dnsResolver.timeout = 1
	dnsResolver.lifetime = 1
	jsonData['info']['isps'][isp]['lastScan'] = datetime.datetime.now().isoformat()
	for domain in jsonData['domains']:
		status = None
		for subdomain in jsonData['domains'][domain]['hosts']:
			if isp not in jsonData['domains'][domain]['hosts'][subdomain]['isp']:
				jsonData['domains'][domain]['hosts'][subdomain]['isp'][isp] =  { 'dnsResponse' : [], 'status' : -2 }
			jsonData['domains'][domain]['hosts'][subdomain]['isp'][isp]['dnsResponse'] = []
			host = subdomain + '.' + domain if subdomain != '@' else domain
			try:
				response = dnsResolver.query(host, 'A')
				for eachRecord in response:
					jsonData['domains'][domain]['hosts'][subdomain]['isp'][isp]['dnsResponse'].append(str(eachRecord))

				#check if any of the original ip are in the response
				status = 2
				#default value: it replied, but with a different ip - DNS Redirect, if found will change to 0
				for eachRecord in jsonData['domains'][domain]['hosts'][subdomain]['isp'][isp]['dnsResponse']:
					if eachRecord in  jsonData['domains'][domain]['hosts'][subdomain]['ip']:
						status = 0
						#the ip is in the isp response, so it (may) not be blocked

			except Exception as e: #(socket.gaierror, dns.exception.Timeout, dns.resolver.NXDOMAIN, dns.resolver.NoAnswer)
				if debug: print 'ERROR (' + str(type(e).__name__) + '): ' + host
				if jsonData['domains'][domain]['hosts'][subdomain]['ip'] == None or len(jsonData['domains'][domain]['hosts'][subdomain]['ip']) == 0:
					status = -1
					# neither the (open) dns neither the isp replied, site may be have shut down - Can't be Resolved
				else:
					status = 1
					#the isp did not resolve, but the reference did
			jsonData['domains'][domain]['hosts'][subdomain]['isp'][isp]['status'] = status


"""
	Prints the data to the screen, yey
"""
def printAllData():
	global jsonData
	print json.dumps(jsonData['domains'], ensure_ascii=True, sort_keys=True, indent=1)


'''
	Test a dns (prints to the console)
	@param dnsAddres the dns address
	@param host the host to resolve
'''
def testDns(dnsAddres = '8.8.8.8', host = 'google.com', timeout = 2, lifetime = 2):
	dnsResolver = dns.resolver.Resolver()
	dnsResolver.nameservers = [dnsAddres]
	dnsResolver.timeout = timeout
	dnsResolver.lifetime = lifetime
	try:
		print host + ' resolved into ' + str(dnsResolver.query(host, 'A')[0]) + ' by ' + dnsAddres
	except Exception as e:
		print 'error ' + str(type(e).__name__) + ' querying ' + str(host) + ' @' + dnsAddres

"""
	Remove domains that are not blocked by any ISP
	@todo
"""
def removeNotBlocked():
	global jsonData
	removed = {'list': [], 'tree': []}
	for domain in jsonData['domains']:
		for subdomain in jsonData['domains'][domain]['hosts']:
			host = subdomain + '.' + domain if subdomain != '@' else domain
			remove = True
			for isp in jsonData['domains'][domain]['hosts'][subdomain]['isp']:
				status = jsonData['domains'][domain]['hosts'][subdomain]['isp'][isp]['status']
				if status != 0 and status != -1:
					remove = False
			if remove:
				removed['list'].append(host)
				removed['tree'].append([domain, subdomain])
	for each in removed['tree']:
		del jsonData['domains'][each[0]]['hosts'][each[1]]
	print json.dumps(removed['list'], ensure_ascii=True, sort_keys=True, indent=3)
	print 'count = ' + str(len(removed['list']))

'''
	adds www and @ if missing
'''
def addMissingSubdomains():
	global jsonData
	requiredHosts = ['@', 'www']
	for domain in jsonData['domains']:
		prevData = {}
		for host in jsonData['domains'][domain]['hosts']:
			if bool(jsonData['domains'][domain]['hosts'][host]):
				prevData = jsonData['domains'][domain]['hosts'][host]

		for host in requiredHosts:
			if host not in jsonData['domains'][domain]['hosts'] or not bool(jsonData['domains'][domain]['hosts'][host]):
				jsonData['domains'][domain]['hosts'][host] = {'blockDate': prevData['blockDate'], 'ip': [], 'isp': { }, 'reason': prevData['reason']}


'''''''''
	These are some stupid methods to fix/destroy the data - to make really specific things...
	(some of) THESE FUNCTIONS ARE OUTDATED, AND DO NOT WORK WITH THE NEW DATA STRUCTURE!
#fix the status
def fixStatus(ispName = 'meo'):
	global jsonData
	for host in jsonData['domains']:
		if not jsonData['domains'][host][ispName]['status'] == -2:
			#check if any of the original ip are in the response
			found = False
			for eachIpRecord in jsonData['domains'][host]['ip']:
				for eachResponseRecord in jsonData['domains'][host]['isp'][ispName]['dnsResponse']:
					if str(eachIpRecord) == str(eachResponseRecord):
						found = True
						jsonData['domains'][host]['isp'][ispName]['status'] = 0
						#the ip appeared in the isp response, so it (may) not be blocked
			if not found:
				jsonData['domains'][host]['isp'][ispName]['status'] = 2

			if len(jsonData['domains'][host]['isp'][ispName]['dnsResponse']) == 0:
				if len(jsonData['domains'][host]['ip']) == 0:
					jsonData['domains'][host]['isp'][ispName]['status'] = -1
				else:
					jsonData['domains'][host]['isp'][ispName]['status'] = 1
#copy reasons from another json
def fix_copyReasonsFromAnotherFile(filePath = 'reasons.json'):
	global jsonData
	with open(filePath) as inFile:
		jsonReasons = json.load(inFile)
	for host in jsonReasons:
		if 'reason' in jsonReasons[host]:
			jsonData['domains'][host]['reason'] = jsonReasons[host]['reason']
#add -2 status to domains without status
def fix_addMissingStatus(filePath = 'reasons.json'):
	global jsonData
	for host in jsonData['domains']:
		for eachIsp in jsonData['domains'][host]['isp']:
			if 'status' not in jsonData['domains'][host]['isp'][eachIsp]:
				jsonData['domains'][host]['isp'][eachIsp]['status'] = -2
#add missing reason
def fix_addMissingStatus(reason = 'Copyright'):
	global jsonData
	for host in jsonData['domains']:
		if 'reason' not in jsonData['domains'][host]:
			jsonData['domains'][host]['reason'] = reason
#Generates and prints ISP scores based on the status of each domain!
def printScores(redirectsCountMore = False):
	global jsonData
	print 'Scores:'
	scores = dict()
	value = 1
	for host in jsonData['domains']:
		for eachIsp in jsonData['domains'][host]['isp']:
			if jsonData['domains'][host]['isp'][eachIsp]['status'] > 0:
				if redirectsCountMore:
					value = jsonData['domains'][host]['isp'][eachIsp]['status']
				if eachIsp in scores:
					scores[eachIsp] += value
				else:
					scores[eachIsp] = value

	for isp, score in scores.iteritems():
		print isp + ': ' + str(score)
#convert the data to a new format
def convertNewFormat1():
	global jsonData
	old = jsonData
	jsonData = {'domains': {}}
	jsonData['domains'] = old
#add hosts to each domain, this changes the JSON structure!
def convertNewFormat2():
	global jsonData
	for host in jsonData['domains']:
		part = host.split('.')
		if (host.count('.') == 1 or (host.count('.') == 2 and (part[-2] == 'co' or part[-2] == 'com'))):
			at = jsonData['domains'][host]
			jsonData['domains'][host] = {"hosts": {"@": at}}
		else:
			print host
#merge the subdomains in the same domain, this changes the JSON structure!
def mergeSubdomains():
	global jsonData
	newSubs = {}
	newFQDN = []
	for host in jsonData['domains']:
		part = host.split('.')
		if not (host.count('.') == 1 or (host.count('.') == 2 and (part[-2] == 'co' or part[-2] == 'com'))):
			if (part[-2] + '.' + part[-1]) not in jsonData['domains']:
				newFQDN.append(part[-2] + '.' + part[-1])
			newSubs[host] = jsonData['domains'][host]
	for host in newFQDN:
		jsonData['domains'][host] = {'hosts':{'@':{}}}
	for host in newSubs:
		part = host.split('.')
		subdomain = ''
		for i in range(0, len(part) - 2):
			subdomain += part[i] + '.'
		jsonData['domains'][part[-2] + '.' + part[-1]]['hosts'][subdomain[:-1]] = jsonData['domains'][host]
		del jsonData['domains'][host]

def remCabovisao():
	for domain in jsonData['domains']:
		for subdomain in jsonData['domains'][domain]['hosts']:
			if 'cabovisao' in jsonData['domains'][domain]['hosts'][subdomain]['isp']:
				print subdomain + '.' + domain
				del jsonData['domains'][domain]['hosts'][subdomain]['isp']['cabovisao']
'''''''''''''''
