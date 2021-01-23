#!/usr/bin/python3
#
# Write a short webpage based on the data from the piholes
import json, requests, sys
import matplotlib
matplotlib.use('Agg')
matplotlib.rc('axes',edgecolor='#DDDDDD')
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime


dt = datetime.now()
dateTimeNow = str(dt.year) + '-' + str(dt.month) + '-' + str(dt.day) + ' ' + str(dt.hour) + ':' + str("{0:0=2d}".format(dt.minute))

htmlFile = '/var/www/html/pihole.html'

argList=sys.argv
del argList[0]

if len(argList) == 0:
   print('You need to supply at least one pihole server.')
   sys.exit(99)

rows = str(100/len(argList))[0:2]
rows = str((rows + '%'))

hheader = '''<html>
<head>
<title>Pihole Summary</title>
<meta http-equiv="refresh" content="60">
<style type="text/css">
body,html {
  height: 100%;
  padding: 0;
  margin: 0;
  color: #E0E0E0;
  background: #020202;
}
</style>
</head>
<body>
\n'''

hfooter = '</body></html>'


###  Creating the graphs for the webpage  ###

for ph in argList:
    URL='http://' + ph + '/admin/api.php?overTimeData10mins'
    picture='/var/www/html/' + ph + '.png'
    phSummary = requests.get(URL)
    phSummaryJson = json.loads(phSummary.text)
    #print(phSummary.text)
    dot = phSummaryJson["domains_over_time"]
    aot = phSummaryJson["ads_over_time"]

    lengthdot = len(dot)
    i=0
    ts=['']*lengthdot
    doty=['']*lengthdot
    aoty=['']*lengthdot
    maxy=['']*lengthdot

    for x in dot.keys():
        ts[i] = datetime.fromtimestamp(int(x)).strftime('%H:%M')
        doty[i] = dot.get(x,0)
        aoty[i] = aot.get(x,0)
        maxy[i] = doty[i] + aoty[i]
        i += 1
    
    plt.style.use('dark_background')
    fig = plt.figure(figsize=(15,3))
    fig.patch.set_facecolor("#020202")
    #ind = np.arange(lengthdot)
    width = .75

    p1 = plt.bar(ts, doty, width)
    p2 = plt.bar(ts, aoty, width, color="#d62600")


    plt.title('Total queries over last 24 hours')
    plt.xticks(np.arange(0, lengthdot-1, 10))
    plt.yticks(np.arange(0, max(maxy), 100))
    plt.legend((p1[0], p2[0]), ('Allowed', 'Blocked'))

    plt.savefig('/var/www/html/' + ph + '.png')


###  Open the html file and start writing the web page  ###

openFile = open(htmlFile,'w')
openFile.write(hheader)


###  This is the meat of the web page iterated for how  ###
###  ever many pihoes you put on the command line       ###

for ph in argList:
   URL='http://' + ph + '/admin/api.php?summary'
   phSummary = requests.get(URL) 
   phSummaryJson = json.loads(phSummary.text)
   center = '''<div style="width:100%; height:''' + rows + ''';">
<table style="height: 36px; width: 60%; border-collapse: collapse; border-style: none; margin-left: auto; margin-right: auto;" border="0" cellspacing="3" cellpadding="2">
<tbody>
<tr style="height: 30px;">
<td rowspan=2, style="width: 14.2857%; height: 24px; text-align: center;"><h1><center><a href="http://{}/admin">{}</a></center></h1></td>
<td style="width: 14.2857%; height: 24px; text-align: center;"><h3>Domains being blocked</h3></td>
<td style="width: 14.2857%; height: 24px; text-align: center;"><h3>DNS Queries</h3></td>
<td style="width: 14.2857%; height: 24px; text-align: center;"><h3>Ads Blocked</h3></td>
<td style="width: 14.2857%; height: 24px; text-align: center;"><h3>Percent of Ads</h3></td>
</tr>
<tr style="height: 32px;">
<td style="width: 14.2857%; height: 24px; text-align: center;"><h3>{}</h3></td>
<td style="width: 14.2857%; height: 24px; text-align: center;"><h3>{}</h3></td>
<td style="width: 14.2857%; height: 24px; text-align: center;"><h3>{}</h3></td>
<td style="width: 14.2857%; height: 24px; text-align: center;"><h3>{}%</h3></td>
</tr>
</tbody>
</table>
<p><center><img src="''' + ph + '''.png" alt="graph" width=90% height=55%></center>
<p><p><p><p>
</div>\n'''
   openFile.write(center.format(ph,ph,phSummaryJson.get("domains_being_blocked"),phSummaryJson.get("dns_queries_today"),phSummaryJson.get("ads_blocked_today"),phSummaryJson.get("ads_percentage_today")))

openFile.write(hfooter)
openFile.close()
