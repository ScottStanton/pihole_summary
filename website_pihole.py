#!/usr/bin/python3
#
# Write a short webpage based on the data from the piholes
import json, math, requests, sys
import matplotlib
matplotlib.use('Agg')
matplotlib.rc('axes',edgecolor='#DDDDDD')
import numpy as np
import matplotlib.pyplot as plt
from tenacity import *
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
.glow {
  font-size: 20px;
  font-family: cursive;
  color: #fff;
  text-align: center;
  animation: glow 1s ease-in-out infinite alternate;
}
@-webkit-keyframes glow {
  from {
    text-shadow: 0 0 10px #fff, 0 0 20px #fff, 0 0 30px #e60073, 0 0 40px #e60073, 0 0 50px #e60073, 0 0 60px #e60073, 0 0 70px #e60073;
  }
  
  to {
    text-shadow: 0 0 20px #fff, 0 0 30px #ff4da6, 0 0 40px #ff4da6, 0 0 50px #ff4da6, 0 0 60px #ff4da6, 0 0 70px #ff4da6, 0 0 80px #ff4da6;
  }
}
</style>
</head>
<body>
\n'''

hfooter = '</body></html>'

def roundup(x):
    return x if x % 100 == 0 else x + 100 - x % 100

@retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
def getpage(URL):
    global phSummary
    phSummary = requests.get(URL)


def update_needed(host):
    global core_current
    URL='http://' + host+ '/admin/api.php?versions'
    try:
        getpage(URL)
    except ConnectionError:
        pass
    except RetryError:
        sys.exit(5)
    version = requests.get(URL) 
    versionJSON = json.loads(version.text)
    current = versionJSON["FTL_current"]
    latest = versionJSON["FTL_latest"]
    core_current = versionJSON["core_current"]
    if current != latest:
        output = '<h1 class="glow">Update Needed!</h1>'
    else:
        output = ""
    return output



###  Creating the graphs for the webpage  ###

for ph in argList:
    URL='http://' + ph + '/admin/api.php?overTimeData10mins'
    picture='/var/www/html/' + ph + '.png'

    try:
        getpage(URL)
    except ConnectionError:
        pass
    except RetryError:
        sys.exit(5)

    phSummaryJson = json.loads(phSummary.text)
    try:
        dot = phSummaryJson["domains_over_time"]
    except KeyError:
        sys.exit(6)
    aot = phSummaryJson["ads_over_time"]

    lengthdot = len(dot)
    i=0
    ts=['']*lengthdot
    doty=['']*lengthdot
    aoty=['']*lengthdot
    maxy=['']*lengthdot

    for x in dot.keys():
        ts[i] = datetime.fromtimestamp(int(x)).strftime('%H:%M')
        doty[i] = dot.get(x,0) - aot.get(x,0)
        aoty[i] = aot.get(x,0)
        maxy[i] = doty[i] + aoty[i]
        i += 1
    
    #print(doty)
    #print(max(doty))
    #print(aoty)
    #print(max(aoty))
    #print(maxy)
    #print(max(maxy))
    plt.style.use('dark_background')
    fig = plt.figure(figsize=(15,3))
    fig.patch.set_facecolor("#020202")
    #ind = np.arange(lengthdot)
    width = .75
    maxmaxy = roundup(max(maxy))

    p1 = plt.bar(ts, doty, width)
    p2 = plt.bar(ts, aoty, width, bottom=doty, color="#d62600")


    plt.title('Total queries over last 24 hours')
    plt.xticks(np.arange(0, lengthdot-1, 10))
    plt.yticks(np.arange(0, maxmaxy, 100))
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
   needupdate = update_needed(ph)
   apt=float(phSummaryJson.get("ads_percentage_today"))
   apt='{:0.0f}'.format(apt)
   center = '''<div style="width:100%; height:''' + rows + ''';">
<table style="height: 36px; width: 60%; border-collapse: collapse; border-style: none; margin-left: auto; margin-right: auto;" border="0" cellspacing="3" cellpadding="2">
<tbody>
<tr style="height: 30px;">
<td rowspan=2, style="width: 14.2857%; height: 24px; text-align: center;"><h1><center><a href="http://{}/admin">{}</a></center></h1> ''' + needupdate + '''</td>
<td style="width: 14.2857%; height: 24px; text-align: center;"><h3>Version</h3></td>
<td style="width: 14.2857%; height: 24px; text-align: center;"><h3>Domains being blocked</h3></td>
<td style="width: 14.2857%; height: 24px; text-align: center;"><h3>DNS Queries</h3></td>
<td style="width: 14.2857%; height: 24px; text-align: center;"><h3>Ads Blocked</h3></td>
<td style="width: 14.2857%; height: 24px; text-align: center;"><h3>Percent of Ads</h3></td>
</tr>
<tr style="height: 32px;">
<td style="width: 14.2857%; height: 24px; text-align: center;"><h3>{}</h3></td>
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
   openFile.write(center.format(ph,ph,core_current,phSummaryJson.get("domains_being_blocked"),phSummaryJson.get("dns_queries_today"),phSummaryJson.get("ads_blocked_today"),apt))

openFile.write(hfooter)
openFile.close()
