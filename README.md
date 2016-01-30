# [List of websites blocked in Portugal][1]

This repo contains (some of) the domains currently being blocked by ISP's in Portugal.

**blockList.txt** - A simple list of the blocked domains domains

**blockList.json** - A detailed JSON file with all the domains, that follows the following format:
```JSON
{
	"domain.name" : {
		"blockDate" : "yyyy-MM",
		"ip" : ["0.0.0.0"],
		"isp" : {
			"ispName" : {
				"status" : 0,
				"dnsResponse" : [
					"255.255.255.255"
				]
			}
		},
		"reason": "Why was the website blocked? (Copyright | Gambling | 'Mistake' | Unknown)"
	}
}
```
**domainScan.py** - the script used to scan and generate the data for all the domains

**dnsServerList.json** - the list of DNS servers (ISP's DNS and open DNS's)

**/web** - The folder with the static resources to the [web viewer][1]

## Acknowledgements

- [dnspython](https://github.com/rthalley/dnspython)
- [jquery](https://jquery.com/)
- [tablesorter](https://github.com/christianbach/tablesorter)
- [GitHub Corners](https://github.com/tholman/github-corners)


## License

MIT

[1]: <http://tofran.github.io/PortugalWebBlocking/>
