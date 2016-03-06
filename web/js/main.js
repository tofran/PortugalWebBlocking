/*
 *	by Tofran 			: 	https://github.com/ToFran
 *	PortugalWebBlocking	: 	https://github.com/ToFran/PortugalWebBlocking
 */

var stats = {};
var domainCount = {'domains': 0, 'hosts': 0};

$.getJSON('blockList.json', function(jsonData) {
	var header = document.querySelectorAll("#mainTable tr");
	for(var eachIsp in jsonData.info.isps){
		header[0].innerHTML += "<th colspan='2' scope='colgroup'>" + eachIsp + "</th>";
		header[1].innerHTML += "<th scope='col' title='status'><span>S</span></th>" +
								"<th scope='col'><span>IP</span></th>";
		stats[eachIsp] = {"-2": 0, "-1": 0, "0": 0, "1": 0, "2": 0};
		
	};
	for(var fqdn in jsonData.domains){
		domainCount.domains++;
		for(var host in jsonData.domains[fqdn].hosts){
			domainCount.hosts++;
			var domain = ((host == '@') ? '': host + '.') + fqdn;
			var current = jsonData.domains[fqdn].hosts[host];
			var newTr = document.createElement('tr');
			newTr.innerHTML +=	"<td class='lalign'>" + domain + "</td>"+
								"<td>" + current.ip[0] + "</td>" + 
								"<td>" + current.blockDate + "</td>" + 
								"<td>" + current.reason + "</td>";
			var ispPos = 0;
			for(var eachIsp in jsonData.info.isps){
				if(!(eachIsp in current.isp)){
					current.isp[eachIsp] = {"dnsResponse": [], "status": -2 };
				};
				newTr.innerHTML += "<td><img alt='status' " +
									"src='web/media/" + current.isp[eachIsp].status  + ".png'>" + 
									"<span>" + current.isp[eachIsp].status + 
									"</spam></td>";
				newTd = document.createElement('td');
				newTd.innerHTML = current.isp[eachIsp].dnsResponse[0];
				newTr.appendChild(newTd);
				stats[eachIsp][current.isp[eachIsp].status]++;
			};
			document.getElementById('tableBody').appendChild(newTr);	
		};
	};

	//stats
	document.getElementById('domainCount').innerHTML = domainCount.domains + ' domains (' + domainCount.hosts + ' hosts)';
	document.getElementById('referenceDns').innerHTML = 
			jsonData.info.reference.name + ' (Last Scan: ' + 
			new Date(jsonData.info.reference.lastScan).toString().slice(0, 24) + ')';
	statsTable = document.querySelector("#statsTable tbody");
	for(var eachIsp in jsonData.info.isps){
		var newTr = document.createElement('tr');
		newTr.innerHTML = "<th>" + eachIsp + "</th>";
		for (var i = -2; i <= 2; i++) {
			newTr.innerHTML += "<td>" + stats[eachIsp][i] + "</td>";
		};
		var date = new Date(jsonData.info.isps[eachIsp].lastScan);
		newTr.innerHTML += "<td>" + date.toString().slice(0, 24) + "</td>";
		statsTable.appendChild(newTr);
	};
	$('#statsTable').tablesorter();
	$('#mainTable').tablesorter();
});