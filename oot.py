import json
from xml.dom.minidom import parseString
import re
import pprint

def outputFile(data, filename): #create (csv) file with data information
    with open(filename, 'w') as out_handle:
        for line in data:
            out_handle.write(','.join(line) + '\n')
def getJsonPositions (name):    # returns positions in the json file
    x = name
    s = 0
    a = []
    while s < len(json_data["annotations"]):
        if x in json_data["annotations"][s]["content"]:
#            print s, x, "\n", len(json_data["annotations"][s]["content"])
            a.append(s)
        s = s+1
    return a
def getTime (name):    #returns average time on the table in seconds
    a = getJsonPositions(name)
    s=0         
    x=0         
    while s < len(a):
        t = (json_data["annotations"][a[s]]["end"]) - (json_data["annotations"][a[s]]["begin"])
#        print (json_data["annotations"][a[s]]["end"]) - (json_data["annotations"][a[s]]["begin"])
        x = x+t
        s = s+1
    x = x / 1000.0
    return x

def getContent (name):  #returns rectangle data of the 'content' part
    a = getJsonPositions(name)
    b = []
    for s in range(len(a)):
        inside = json_data["annotations"][a[s]]["content"]
        dom = parseString(inside)
        xmlTag = dom.getElementsByTagName('svg:rect')[0].toxml()
        b.append(xmlTag)
    return b
def getNames(): #returns a list with the names of all items
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
    return x, y

def getRelativePositions (name): #returns position on the table
    b = getContent(name)
    positions = []
    for s in range(len(b)):
        tempX = re.findall('x="(\w+)', b[s])
        tempY = re.findall('y="(\w+)', b[s])
        positions.append((int(tempX[0])/10, int(tempY[0])/10)) #/10 for smaller matrix
    return positions

def getOcclusion(name): #returns percentage of the occlusion for one item
    x, y = getSize(name)
    a = (float(x * y) / (640 * 480)) * 100
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
    print "Average items on table:", average, "\n"

def generateOutput(allnames, list): #create output on console - position, time, occlusion, size
    output_list = list
    for x in range(len(allnames)):

        time = getTime(allnames[x])
        pos = getJsonPositions(allnames[x])
        print len(pos), "Position(s) of", allnames[x], ":", pos, "\n", "Average time on the table:", time, "seconds"

        occ = getOcclusion(allnames[x])
        print "Average space occluded:", occ, "percent"

        a, b = getSize(allnames[x])
        print "Average x =", a, "and average y =", b

        print "\n"
        output_list.append((allnames[x], str(time), str(occ), str(a), str(b)))

def createMatrix(col, row): #create a new matrix with value 0
    new_matrix = [[0 for y in range(col)] for x in range(row)]
    return new_matrix

def modifyMatrix(name, matrix): #modify to a heatmap-style matrix
    sizeX, sizeY = getSize(name)
    sizeX = sizeX /10
    sizeY = sizeY /10
#    print sizeX, sizeY, "size X and Y"
    p = getRelativePositions(name)
#    print p, "relative positions"
    m = matrix

    for s in range(len(p)):
        pX = (p[s][0])
        pY = (p[s][1])
#        print "starting px and py", pX, pY
        for x in range(sizeY):
#            print "sizeY", sizeY
            for x in range(sizeX):
                m[pY][pX] = (m[pY][pX])+1
                pX = pX +1
            pY = pY +1
            pX = (p[s][0])
    return m

def outputMatrix(matrix, outputname): #switch int to str
    for x in range(len(matrix)):
        for y in range(len(matrix[x])):
            matrix[x][y]=str(matrix[x][y])
    outputFile(matrix, outputname)



json_file = open('graphical_annotation.json', 'r')
json_data = json.load(json_file)
print "Items in json file: ", len(json_data["annotations"]), "\n"

allnames = getNames()

output_list = [('names', 'time on table', 'occlusion', 'sizeX', 'sizeY')]

onTable(), generateOutput(allnames, output_list), outputFile(output_list, 'output.csv')
#pprint.pprint(output_list)

matrix = createMatrix(70,50)
for s in range(len(allnames)):
    matrix = modifyMatrix(allnames[s],matrix)
outputMatrix(matrix,'matrix.csv')



#newmatrix = createMatrix(70,50)
#newmatrix = modifyMatrix(allnames[9],newmatrix)
#
#outputMatrix(newmatrix, 'matrix9.csv')


json_file.close()