# [List of websites blocked in Portugal]

This repo contais (some of) the domains currently beeing blocked by ISP's in portugal.

**blockList.txt** - A simple list of the blocked domains domains

**blockList.json** - A detailed JSON file with all the domains, that follows the followinf format:
```JSON
{
	"domain.name" : {
		"blockDate" : "2015-10",
		"ip" : ["0.0.0.0"],
		"isp" : {
			"ispName" : {
				"status" : 0,
				"dnsResponse" : [
					"255.255.255.255"
				]
			}
		},
		"highlight" : "false",
		"reason": "Why was the website blocked?"
	}
}
```
**domainScan.py** - the script used to scan and generate the data for all the domains

**dnsServerList.json** - the list of DNS servers (ISP's DNS and open DNS's)

**/web** - The folder with resources to the web viwer


License
----

MIT

[List of websites blocked in Portugal]: <http://tofran.github.io/PortugalWebBlocking/>
