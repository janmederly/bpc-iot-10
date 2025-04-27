# HTML templates for the web interface

# Dashboard page with charts and current values
dashboard_html = """<html><head><title>Dashboard</title>
<script src='https://cdn.jsdelivr.net/npm/chart.js'></script>
<style>body{background:#200;color:white;font-family:sans-serif;text-align:center;}
.menu{margin:10px;}a{color:lightblue;text-decoration:none;font-size:18px;margin:0 10px;}
.status-container{background:white;color:black;padding:10px;border-radius:10px;width:90%;max-width:400px;margin:10px auto;font-size:18px;}
.charts-wrapper{display:flex;flex-wrap:wrap;justify-content:center;gap:10px;margin:20px auto;max-width:1200px;}
.chart-container{background:white;padding:10px;border-radius:10px;width:300px;}canvas{background:white;border-radius:10px;}</style>
<script>
var labels=[],tempData=[],voltData=[],currData=[],powerData=[],latestData={};
function createCharts(){
 tempChart=new Chart(document.getElementById('tempChart').getContext('2d'),{type:'line',data:{labels:labels,datasets:[{label:'Temp (C)',data:tempData,borderColor:'red',fill:true}]},options:{scales:{y:{beginAtZero:true}}}});
 voltCurrChart=new Chart(document.getElementById('voltCurrChart').getContext('2d'),{type:'line',data:{labels:labels,datasets:[{label:'Volt (V)',data:voltData,borderColor:'blue',fill:false},{label:'Curr (A)',data:currData,borderColor:'orange',fill:false}]},options:{scales:{y:{beginAtZero:true}}}});
 powerChart=new Chart(document.getElementById('powerChart').getContext('2d'),{type:'line',data:{labels:labels,datasets:[{label:'Power (W)',data:powerData,borderColor:'green',fill:true}]},options:{scales:{y:{beginAtZero:true}}}});
}
function updateValues(){fetch('/data').then(r=>r.json()).then(data=>{
 latestData=data;
 document.getElementById('tempVal').innerText='Temp: '+data.temp+' C';
 document.getElementById('voltVal').innerText='Volt: '+data.volt+' V';
 document.getElementById('currVal').innerText='Curr: '+data.curr+' A';
 document.getElementById('powerVal').innerText='Power: '+data.power+' W';
 document.getElementById('consumptionVal').innerText='Consumption: '+data.consumption+' kWh';
 document.getElementById('currSpeed').innerText='Current fan speed: '+data.currSpeed+' %';
});}
function updateCharts(){
 if(!latestData.temp)return;
 var t=new Date().toLocaleTimeString();
 labels.push(t);
 tempData.push(latestData.temp);
 voltData.push(latestData.volt);
 currData.push(latestData.curr);
 powerData.push(latestData.power);
 if(labels.length>20){labels.shift();tempData.shift();voltData.shift();currData.shift();powerData.shift();}
 tempChart.update();voltCurrChart.update();powerChart.update();
}
window.onload=function(){createCharts();setInterval(updateValues,1000);setInterval(updateCharts,5000);}
</script></head>
<body><div class='menu'><a href='/'>Dashboard</a> | <a href='/settings'>Settings</a></div>
<div class='status-container'>
<h2>Current Values</h2>
<p id='tempVal'>Temperature: -- C</p>
<p id='voltVal'>Voltage: -- V</p>
<p id='currVal'>Current: -- A</p>
<p id='powerVal'>Power: -- W</p>
<p id='consumptionVal'>consumption: -- kWh</p>
<p id='currSpeed'>Current fan speed: -- %</p>
</div>
<div class='charts-wrapper'>
<div class='chart-container'><canvas id='tempChart' width='300' height='250'></canvas></div>
<div class='chart-container'><canvas id='voltCurrChart' width='300' height='250'></canvas></div>
<div class='chart-container'><canvas id='powerChart' width='300' height='250'></canvas></div>
</div>
</body></html>"""

# Settings page for fan control and temperature thresholds
settings_html = """<html><head><title>Settings</title>
<style>body{background:#200;color:white;text-align:center;font-family:sans-serif;}
.menu{margin:10px;}a{color:lightblue;margin:10px;text-decoration:none;font-size:18px;}
.settings{background:white;color:black;padding:20px;border-radius:10px;width:90%;max-width:400px;margin:auto;margin-top:20px;}
input,button{margin:5px;padding:5px;border-radius:5px;}button{background:red;color:white;border:none;}</style>
<script>
function setCurve(){
 var l=document.getElementById('low').value,m=document.getElementById('medium').value,h=document.getElementById('high').value;
 fetch(`/set_curve?low=${l}&medium=${m}&high=${h}`).then(r=>alert('Settings updated'));
}
function toggleFan(s){fetch('/fan/'+s);}
</script></head>
<body><div class='menu'><a href='/'>Dashboard</a> | <a href='/settings'>Settings</a></div>
<div class='settings'>
<h2>Fan Curve</h2>
Low (C): <input id='low' value='20'><br>
Medium (C): <input id='medium' value='50'><br>
High (C): <input id='high' value='100'><br><br>
<button onclick='setCurve()'>Save</button><br><br>
<button onclick='toggleFan("on")'>Fan On</button>
<button onclick='toggleFan("off")'>Fan Off</button>
</div></body></html>"""

# Wi-Fi Setup page for initial configuration
wifi_setup_html = """<html><head><title>WiFi Setup</title>
<style>body{background:#200;color:white;text-align:center;font-family:sans-serif;}
input,button{margin:5px;padding:10px;border-radius:5px;}button{background:red;color:white;border:none;}</style></head>
<body><h2>Configure WiFi</h2>
<form action="/wifi_save" method="GET">
SSID: <input type="text" name="ssid"><br>
Password: <input type="password" name="pswd"><br><br>
<button type="submit">Save & Connect</button></form></body></html>"""
