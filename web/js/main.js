$.getJSON('blockList.json', function(jsonData) {
	var domainCount = 0;
	var isps = ["meo", "nos", "vodafone"]; //@toodo add this info to the JSON
	var header = document.querySelectorAll("#mainTable tr");
	for(var eachIsp of isps){
		header[0].innerHTML += "<th colspan='2' scope='colgroup'>" + eachIsp + "</th>";
		header[1].innerHTML += "<th scope='col' title='status'><span>S</span></th>" +
								"<th scope='col'><span>IP</span></th>"
	}
	$.each( jsonData, function(domain, data) {
		var newTr = document.createElement('tr');
		// domain & ip & date & reason collum
		newTr.innerHTML +=	"<td class='lalign'>" + domain + "</td>"+
							"<td>" + data.ip[0] + "</td>" + 
							"<td>" + data.blockDate + "</td>" + 
							"<td>" + data.reason + "</td>";
		var ispPos = 0;
		for(var eachIsp of isps){
			if(!eachIsp in data.isp){
				data.isp[eachIsp] = {"dnsResponse": [], "status": -1 };
			}
			newTr.innerHTML += "<td><img alt='status' " + //@todo do this with css
								"src='web/media/" + data.isp[eachIsp].status  + ".png'>" + 
								"<span>" + data.isp[eachIsp].status + 
								"</spam></td>";
			newTd = document.createElement('td');
			newTd.innerHTML = data.isp[eachIsp].dnsResponse[0];
			newTd.setAttribute('data-blocked', data.isp[eachIsp].blocked);
			newTr.appendChild(newTd);
		};
		// append the row		
		document.getElementById('tableBody').appendChild(newTr);
		domainCount++;
		
	});
	document.getElementById('domainCount').innerHTML = domainCount;
	$('#mainTable').tablesorter();
});