$.getJSON('dnsBlocking.json', function(jsonData) {
	var domainCount = 0;
	$.each( jsonData, function(domain, data) {
		var newTr = document.createElement('tr');
		// domain collum
		newTr.innerHTML =   "<td class='lalign'>" + domain + "</td>";
		// ip collum
		var newTd = document.createElement('td');
		newTd.innerHTML = data.ip[0];
		newTr.appendChild(newTd);
		// date collum
		newTr.innerHTML +=	"<td>" + data.blockDate + "</td>";
		// isp collum
		for(var eachIsp in data.isp){
			if(data.isp[eachIsp].blocked == true){
				newTr.innerHTML += "<td><span class='hidden'>N</span><img alt='Blocked' src='web/media/blocked.png'></td>";
			}
			else{
				newTr.innerHTML += "<td><span class='hidden'>Y</span><img alt='Not blocked' src='web/media/notBlocked.png'></td>";
			}
			newTd = document.createElement('td');
			newTd.innerHTML = data.isp[eachIsp].dnsResponse[0];
			newTd.setAttribute('data-blocked', data.isp[eachIsp].blocked);
			newTr.appendChild(newTd);
		}
		// append the row		
		document.getElementById('tableBody').appendChild(newTr);
		domainCount++;
	});
	document.getElementById('domainCount').innerHTML = domainCount;
	$('#mainTable').tablesorter();
});