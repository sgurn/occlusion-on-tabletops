import json
from xml.dom.minidom import parseString
import re


def getPositions (name):    # returns positions in the json file
    x = name
    s = 0
    a = []
    while s < len(json_data["annotations"]):
        if x in json_data["annotations"][s]["content"]:
#            print s, x, "\n", len(json_data["annotations"][s]["content"])
            a.append(s)
        s = s+1
    return a



def getTime (name):    #returns average time on the table
    a = getPositions(name)  
    s=0         
    x=0         
    while s < len(a):
        t = (json_data["annotations"][a[s]]["end"]) - (json_data["annotations"][a[s]]["begin"])
#        print (json_data["annotations"][a[s]]["end"]) - (json_data["annotations"][a[s]]["begin"])
        x = x+t
        s = s+1
    print len(a), "Position(s) of", name, ":", a, "\n", "Average time on the table:", x, "(In seconds:", x/1000.0, ")"
    return x


def getContent (name):  #returns rectangle data of the 'content' part
    a = getPositions(name)
    b = []
    for s in range(len(a)):
        inside = json_data["annotations"][a[s]]["content"]
        dom = parseString(inside)
        xmlTag = dom.getElementsByTagName('svg:rect')[0].toxml()
        b.append(xmlTag)
    return b

def getNames(): #returns a list with the names of the items
    names = []
    for s in range(len(json_data["annotations"])):
        inside = json_data["annotations"][s]["content"]
        dom = parseString(inside)
        xmlTag = dom.getElementsByTagName('svg:rect')[0].toxml()
        for l in xmlTag.split('" '):
            if 'name="' in l:
                k,  v = l.split('="')
                name = v                
                if name not in names:
                    names.append(name)
    return names


def getSize (name):    #returns average size
    b = getContent(name)
    allWidth = 0
    allHeight = 0
    for s in range(len(b)):
        sizeX = re.findall('width="(\w+)', b[s])
#        print "Width nr", s, "= ", sizeX[0]
        sizeY = re.findall('height="(\w+)', b[s])
#        print "Height nr", s, "= ", sizeY[0]
        allWidth = allWidth+int(sizeX[0])
        allHeight = allHeight+int(sizeY[0])
    x = allWidth / len(b)
    y = allHeight / len(b)
    print "Average x =", x, "and average y =", y
    return x, y


def getOcclusion(name): #returns percentage of the occlusion for one item
    x, y = getSize(name)
    a = (float(x * y) / (640 * 480)) * 100
    print "Average space occluded:", a, "percent"
    return a

def getTotalTime(): #returns last point in time of the last item on the table
    t = 0
    for s in range(len(json_data["annotations"])):
        if t < json_data["annotations"][s]["end"]:
            t = json_data["annotations"][s]["end"]
    return t


def onTable():      #average items on the table
    t = getTotalTime() #end of timeframe
    time = 0    #current point in time
    b = 0 #items per section. temporary counter
    c = 0.0 #total items per section
    sections = 0.0 #total number of points in time
    average = 0.0
    while time <= t:
        for s in range(len(json_data["annotations"])):
            begin = json_data["annotations"][s]["begin"]
            end = json_data["annotations"][s]["end"]
            if (time >= begin and time <= end):
                b = b+1                        
        c = c+b
#        print "time =", time, "c =", c
        time = time + 60000
        b = 0
        sections = sections + 1
    average = c / sections
    print "Average items on table:", average

json_file=open('graphical_annotation.json', 'r')
json_data = json.load(json_file)

print "Items in json file: ", len(json_data["annotations"]), "\n"

# list of names of the items. needs to be up to date
#allnames = ["Large1", "Small1", "White1", "White2", "Blue1", "Blue2", "Blue3", "Glass1", "Keyboard", "Ipad"]

allnames = getNames()

for x in range(len(allnames)):
    getTime(allnames[x])
#    getSize(allnames[x])
    getOcclusion(allnames[x])
    print "\n"

doit = onTable()



#print json.dumps(json_data, sort_keys=True, indent=4)

json_file.close()
