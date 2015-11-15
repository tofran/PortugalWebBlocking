$.getJSON('blockList.json', function(jsonData) {
	var domainCount = 0;
	$.each( jsonData, function(domain, data) {
		var newTr = document.createElement('tr');
		// domain collum
		newTr.innerHTML =   "<td class='lalign'>" + domain + "</td>";
		// ip collum
		var newTd = document.createElement('td');
		newTd.innerHTML = data.ip[0];
		newTr.appendChild(newTd);
		// date & reason collum
		newTr.innerHTML +=	"<td>" + data.blockDate + "</td>" + 
							"<td>" + data.reason + "</td>";
		// isps collums
		for(var eachIsp in data.isp){
			if (eachIsp != "cabovisao") { //DISABLE CABOVISAO
				if(typeof data.isp[eachIsp].status === 'undefined'){
					newTr.innerHTML += "<td>n/a</td>";
				}
				else{
					newTr.innerHTML += "<td><img alt='status' src='web/media/" + data.isp[eachIsp].status  + ".png'><span class='status'>" + data.isp[eachIsp].status + "</spam></td>";
				}
				newTd = document.createElement('td');
				newTd.innerHTML = data.isp[eachIsp].dnsResponse[0];
				newTd.setAttribute('data-blocked', data.isp[eachIsp].blocked);
				newTr.appendChild(newTd);
			};
		};
		// append the row		
		document.getElementById('tableBody').appendChild(newTr);
		domainCount++;
		
	});
	document.getElementById('domainCount').innerHTML = domainCount;
	$('#mainTable').tablesorter();
});