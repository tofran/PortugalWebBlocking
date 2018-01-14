# [List of websites blocked in Portugal][list]

**This branch will be the next version, currently it is in development and IT DOES NOT WORK**

This repo contains the domains currently being blocked by ISP's in Portugal.

**blockList.txt** - A simple list of the currently blocked domains

**blockList.json** - A detailed JSON file with all the domains and subdomains, that follows the following format:
```JSON
{
	"<domain name>" : {
		"status" : 0,
		"hosts": {
			"<subdomain or @>": {
				"blockDate" : "yyyy-MM-dd",
				"ips" : ["0.0.0.0"],
				"reason": "<Why was the website blocked? (Copyright, Gambling, 'Mistake', Unknown)>",
				"<ISP>" : {
					"status" : 0,
					"response" : [
						"255.255.255.255"
					]
				}
			}
		}
	}
}
```

Status codes:
* `-2` Not Scanned;
* `-1` Can't be Resolved (Website down);
* `0` Not Blocked (Same response, self-explanatory);
* `1` DNS Blocked (The DNS did not reply, but the domain was resolved by the reference DNS);
* `0` DNS Redirect (The DNS replied with a different IP from what it actually is).


**domainScan.py** - the script used to scan and generate the data for all the domains

**dnsServerList.json** - the list of DNS servers (ISP's DNS and open DNS's)

**/web** - The folder with the static resources to the [web viewer][1]

## Acknowledgements

- [tablesorter](https://github.com/christianbach/tablesorter)
- [GitHub Corners](https://github.com/tholman/github-corners)
- [Stop hand icon](https://en.wikipedia.org/wiki/File:Stop_hand.svg)


## License

The list itself is public domain, it would be great if you made reference to this repo :)
The code and this project are licensed under GPL v3

[list]: <https://tofran.github.io/PortugalWebBlocking/>

