import json
from xml.dom.minidom import parseString
import re

def getPositions (name):   
    x = name    #name des items
    s = 0       #start des counters
    a = []      #liste der gesuchten items
    while s < len(json_data["annotations"]):
        if x in json_data["annotations"][s]["content"]:
#            print s, x, "\n", len(json_data["annotations"][s]["content"])
            a.append(s)
        s = s+1
    return a

def getTime (name):  #Gibt Zeit eines items auf dem Tisch zurueck
    a = getPositions(name)  #liste mit positionen des items
    s=0         #start des counters
    x=0         #variable fuer die dauer
    while s < len(a):
        t = (json_data["annotations"][a[s]]["end"]) - (json_data["annotations"][a[s]]["begin"])
#        print (json_data["annotations"][a[s]]["end"]) - (json_data["annotations"][a[s]]["begin"])
        x = x+t
        s = s+1
    print "Positions of ", name, ":", a, "\n", "Average time on the table: ", x, "(In seconds:", x/1000.0, ")"
    return x

def getContent (name):
    a = getPositions(name)
    b = []
    s = 0
    while s < len(a):
        inside = json_data["annotations"][a[s]]["content"]
        dom = parseString(inside)
        xmlTag = dom.getElementsByTagName('svg:rect')[0].toxml()
        b.append(xmlTag)
        s = s+1
    return b

def getSize (name):
    b = getContent(name)
    s = 0
    allWidth = 0
    allHeight = 0
    while s < len(b):
        sizeX = re.findall('width="(\w+)', b[s])
#        print "Width nr", s, "= ", sizeX[0]
        sizeY = re.findall('height="(\w+)', b[s])
#        print "Height nr", s, "= ", sizeY[0]
        allWidth = allWidth+int(sizeX[0])
        allHeight = allHeight+int(sizeY[0])
        s = s+1
    x = allWidth / len(b)
    y = allHeight / len(b)
    print "Average x =", x, "and average y =", y
    return x, y
#        for l in t.split('" '):
#             if 'x="' in l:
#                     k,  v = l.split('="')
#                     x = int(v)
#        print x

def totalTime():
    t = 0
    for x in range(len(json_data["annotations"])):
        if t < json_data["annotations"][x]["end"]:
            t = json_data["annotations"][x]["end"]
    return t

def onTable():
    t = totalTime() / 2 #end of timeframe
    time = 0    #current point in time
    b = 0 #items per section. temporary counter
    c = 0.0 #total items per section
    sections = 0.0 #total number of points in time
    average = 0.0
    while time <= t:
        for x in range(len(json_data["annotations"])):
            begin = json_data["annotations"][x]["begin"]
            end = json_data["annotations"][x]["end"]
            if (time >= begin and time <= end):
                b = b+1                        
        c = c+b
#        print "time =", time, "c =", c
        time = time + 60000
        b = 0
        sections = sections + 1
    average = c / sections
    print "Average items on table:", average


json_file=open('real_06_08.json')
json_data = json.load(json_file)

print "Length of json file: ", len(json_data["annotations"]), "\n"

allnames = ["Large1", "Small1", "White1", "White2", "Blue1", "Blue2", "Glass1"]

for x in range(len(allnames)):
    getTime(allnames[x])
    getSize(allnames[x])
    print "\n"

test = onTable()

#print json.dumps(json_data, sort_keys=True, indent=4)

json_file.close()
