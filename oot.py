import json
from xml.dom.minidom import parseString
import re
import pprint
import math

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
            a.append(s)
        s = s+1
    return a

def getTime (name):    #returns total time on the table in seconds
    a = getJsonPositions(name)
    s=0         
    x=0         
    while s < len(a):
        t = (json_data["annotations"][a[s]]["end"]) - (json_data["annotations"][a[s]]["begin"])
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
        sizeY = re.findall('height="(\w+)', b[s])
        allWidth = allWidth+int(sizeX[0])
        allHeight = allHeight+int(sizeY[0])
    x = allWidth / len(b)
    y = allHeight / len(b) 
    return x, y

def getCategory (allnames):    #returns two list: one with all physical and one with all hybrid items
    physicals = []
    hybrids = []
    x = 'green' #physicals have green stroke
    for s in range(len(json_data["annotations"])):
        for c in range(len(allnames)):
            if allnames[c] in json_data["annotations"][s]["content"]:
                if x in json_data["annotations"][s]["content"]:
                    if allnames[c] not in physicals:
                        physicals.append(allnames[c])
                else:
                    if allnames[c] not in hybrids:
                        hybrids.append(allnames[c])
    return physicals, hybrids


def getRelativePositions (name): #returns position on the table
    b = getContent(name)
    positions = []
    for s in range(len(b)):
        tempX = re.findall('x="(\w+)', b[s])
        tempY = re.findall('y="(\w+)', b[s])
        positions.append((int(tempX[0]), int(tempY[0]))) #/10 for smaller matrix
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

def onTable():      #average items on table: 1. both categories, 2. physical and 3. hybrid
    t = getTotalTime() #end of timeframe
    time = 0    #current point in time
    count_total = 0.0 #total items per timeframe
    count_p = 0.0
    count_h = 0.0
    timeframe = 0.0 #total number of timeframes
    g = 'green'
    while time <= t:
        for s in range(len(json_data["annotations"])):
            begin = json_data["annotations"][s]["begin"]
            end = json_data["annotations"][s]["end"]
            if (time >= begin and time <= end):
                count_total = count_total +1
                if g in json_data["annotations"][s]["content"]:
                    count_p = count_p +1
                else:
                    count_h = count_h +1
#        print "time =", time, "c =", c
        time = time + 10000
        timeframe = timeframe + 1
    average_t = count_total / timeframe
    average_p = count_p / timeframe
    average_h = count_h / timeframe
    return average_t, average_p, average_h

def generateOutput(allnames, list): #create output for console and file
    output_list = list
    p, h = getCategory(allnames)
    ontableT, ontableP, ontableH = onTable()
    gen_occ = 0
    totaltime = getTotalTime()/1000 #total time of the experiment in seconds

    #data for each item:
    #positions, total time on table, average occ, average occ per time, average x and y
    for x in range(len(allnames)):

        time = getTime(allnames[x]) #total time in seconds
        pos = getJsonPositions(allnames[x])
        occ = getOcclusion(allnames[x]) #occlusion
        gen_occ = gen_occ + (time*occ)
        
        print len(pos), "Position(s) of", allnames[x], ":", pos, "\n", "Total time on the table:", time, "seconds"
        print "Average space occluded by this item:", occ, "percent."
        print "Average space occluded throughout the experiment:", (time*occ)/(totaltime)

        a, b = getSize(allnames[x])
        print "Average x =", a, "and average y =", b   
        print "\n"

        output_list.append((allnames[x], str((time/60)), str(occ), str(((time*occ)/(totaltime))), str(a), str(b)))

    print "Physicals:", p, "\n", "Hybrids:", h
    print "Average items on the table:", ontableT
    print "Average physical items on the table:", ontableP
    print "Average hybrid items on the table:", ontableH
    print "Average space of the table occluded:", gen_occ / (totaltime), "percent."
    print "Total duration of the video:", totaltime, "seconds. Thats equal", totaltime/60, "minutes.", "\n"

    # data for physical itemss:
    timeP = 0 # total time 
    posP = [] # positions of physicals
    occP = 0 # total occlusion
    xP = 0
    yP = 0
    gen_occ_P = 0
    for x in range(len(p)):
        timeP = timeP + getTime(p[x])
        occP = occP + getOcclusion(p[x])
        gen_occ_P = gen_occ_P + (getOcclusion(p[x])*getTime(p[x]))
        posP.append(getJsonPositions(p[x]))
        sizexP, sizeyP = getSize(p[x])
        xP = xP + sizexP
        yP = yP + sizeyP

    output_list.append(("physical item", str(((timeP/60))/len(p)), str((occP /len(p))), str(((gen_occ_P/totaltime))), str(xP/len(posP)), str(yP/len(posP))))

    print "Position(s) of PHYSICALS:", posP, "\n", "Average time of PHYSICAL ITEMS on the table:", timeP /len(p), "seconds."
    print "Average space occluded by one physical item:", occP / len(p), "percent."
    print "Average space occluded by physical items:", gen_occ_P /totaltime, "percent."
    print "Average x =", xP / len(posP), "and average y =", yP/len(posP)
    print "len(posP)=", len(posP), "\n", "len(p)=", len(p), "\n"

    #data for hybrid items:
    timeH = 0
    posH = []
    occH = 0
    xH = 0
    yH = 0
    gen_occ_H=0
    for x in range(len(h)):
        timeH = timeH + getTime(h[x])
        occH = occH + getOcclusion(h[x])
        gen_occ_H = gen_occ_H + (getTime(h[x])*getOcclusion(h[x]))
        posH.append(getJsonPositions(h[x]))
        sizexH, sizeyH = getSize(h[x])
        xH = xH + sizexH
        yH = yH + sizeyH

    output_list.append(("hybrid item", str((((timeH/60))/len(h))), str((occH /len(h))), str(((gen_occ_H/totaltime))), str(xH/len(posH)), str(yH/len(posH))))

    print "Position(s) of HYBRIDS:", posH, "\n", "Average time of HYBRID ITEMS on the table:", timeH / len(h), "seconds."
    print "Average space occluded by one hybrid item:", occH / len(h), "percent."
    print "Average space occluded by hybrid items:", gen_occ_H / totaltime , "percent."
    print "Average x =", xH / len(posH), "and average y =", yH/len(posH)
    print "len(posH)=", len(posH), "\n", "len(h)=", len(h), "\n"

def createMatrix(col, row): #create a new matrix with value 0
    new_matrix = [[0 for y in range(col)] for x in range(row)]
    return new_matrix

def modifyMatrix(name, matrix): #modify to a heatmap-style matrix
    m = matrix
    sizeX, sizeY = getSize(name)
#    sizeX = sizeX /10
#    sizeY = sizeY /10

    r = getRelativePositions(name)
    p = getJsonPositions(name)
    plist = []
    # create plist: time for each position. same length as r
    for s in range(len(p)):
        t = (json_data["annotations"][p[s]]["end"]) - (json_data["annotations"][p[s]]["begin"])
        t = t / 10000
        plist.append(t)
#    print plist
    # relativ positions
    for s in range(len(r)):
        pX = (r[s][0])
        pY = (r[s][1])
        # start at relative positions and go through each row and col
        for x in range(sizeY):
            for x in range(sizeX):
                m[pY][pX] = (m[pY][pX])+plist[s] #plist[s]: time spend on this position
                pX = pX +1
            pY = pY +1
            pX = (r[s][0])
    return m

def outputMatrix(matrix, outputname): #switch int to str
    for x in range(len(matrix)):
        for y in range(len(matrix[x])):
            matrix[x][y]=str(int(matrix[x][y]))
    outputFile(matrix, outputname)

json_file = open('graphical_annotation.json', 'r')
json_data = json.load(json_file)
print "Items in json file: ", len(json_data["annotations"]), "\n"

allnames = getNames()
output_list = [('name', 'time on table (in m)', 'occlusion', 'occlusion through experiment', 'sizeX', 'sizeY')]
generateOutput(allnames, output_list)
outputFile(output_list, 'output_1.csv')

#pprint.pprint(output_list)

matrix = createMatrix(700,505)
matrixPhysicals = createMatrix(700,505)
matrixHybrids = createMatrix(700,505)
physicals, hybrids = getCategory(allnames)

for s in range(len(allnames)):
    matrix = modifyMatrix(allnames[s],matrix)
outputMatrix(matrix,'matrix_1_big.csv')

for s in range (len(physicals)):
    matrixPhysicals = modifyMatrix(physicals[s],matrixPhysicals)
outputMatrix (matrixPhysicals, 'matrix_1_big_Physicals.csv')

for s in range (len(hybrids)):
    matrixHybrids = modifyMatrix(hybrids[s], matrixHybrids)
outputMatrix(matrixHybrids, 'matrix_1_big_Hybrids.csv')


json_file.close()