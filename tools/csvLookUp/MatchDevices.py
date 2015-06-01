'''
Created on Jun 24, 2014
'''
import argparse
import csv
import json
import sys, glob
import uuid

"""
Read the CSV file from WebCTRL. The CSV should have the following columns:

Location | Control Program| Name | Object ID | Device ID | Object Name

The first row is a title row. Each row afterwards is a "Network IO" point,
corresponding to a BACnet data point. This program reads the CSV file and
convert the tabular data to JSON object

@author: tliu
@param fileName: the path of the CSV file
@return devList: list of JSON object.
"""
def readCSV(csvFile):
    f = open(csvFile, 'rb')
    lineCount = 0;
    locationDict = {};
    try:
        reader = csv.reader(f)
        reader.next()
        for row in reader:
            if (len(row) != 6):
                print "Skipping bad line:", row
                continue
            
            location = row[0]
            readableName = row[1] + ':' + row[2]
            deviceID = row[4]
            if deviceID.startswith('DEV:'):
                # Change device id to JSON like notation
                deviceID = 'device' + deviceID[4:]
            objectName = row[5]
            
            # Use the "location" as the key
            if location in locationDict:
                locationDict[location].append((readableName, deviceID, objectName))
            else:
                locationDict[location] = [(readableName, deviceID, objectName)]
            
            lineCount += 1
    finally:
        f.close()
        
    print "Read", lineCount, 'points'
    return locationDict

def createDevice(objs, props, name, desc):
    dev = {}
    dev['objs'] = objs
    dev['props'] = props
    dev['name'] = name
    dev['desc'] = desc
    return dev

def createBacnetObject(unit, props, name, data_type, desc):
    obj = {}
    obj['unit'] = unit
    obj['props'] = props
    obj['name'] = name
    obj['data_type'] = data_type
    obj['desc'] = desc
    return obj

# deviceList format:
#
# deviceList -> [dev1, dev2, ...]
#
# dev1 -> {  'objs': [obj1, obj2, ...],
#            'props': {  'mac':
#                        'max_apdu':
#                        'adr':
#                        'net':
#                        'device_id':
#                     }
#            'name':
#            'desc':
#         }
#
# obj1 -> {  'unit':
#            'props': {  'type_str':
#                        'instance':
#                        'type':
#                     }
#            'name':
#            'data_type':
#            'desc':
#         }
def readJSON():
    fileList = glob.glob("../data/range_240000-299999/*.json")
    # fileList = glob.glob("../data/scan_range_0_70999_1000/*.json")
    deviceDict = {}
    for jsonFile in fileList:
        #print jsonFile

        f = open(jsonFile, 'rb')
        deviceList = None
        try:
            deviceList = json.load(f)
        except ValueError:
            print 'Invalid JSON file: ', jsonFile
            continue
        finally:
            f.close()
        # print the object.
        # Put the devices in the list into a dict. Key: device name. Value: device object.
        for dev in deviceList:
            devName = dev['name']
            if devName == None:
                print "Null device name"
            elif devName in deviceDict:
                print "Duplicate device name:", devName, dev['props']['device_id']
            else:
                deviceDict[devName] = dev
                print devName, ',', dev['props']['device_id'], ',', len(dev['objs'])
    return deviceDict

def generateDriverIni(sourceName, jsonName, port):
    reportDeliveryLocation = 'http://localhost:8079/add/rU3eqtaE4zBSzZKjoUS9Q7fVPbTmKmD2eOUr'
    uid = str(uuid.uuid4())
    iface = 'eth1'
    jsonPath = '/usr/local/share/smap_sources/smap-data-read-only/python/conf/json/' + jsonName
    ini = """
[report 0]
ReportDeliveryLocation = """ + reportDeliveryLocation + """
[/]
uuid = """ + uid + """
Metadata/SourceName = """ + sourceName + """
[server]
port = """ + str(port) + """
[/""" + sourceName + """]
type = smap.drivers.pybacnet.driver.BACnetDriver
iface = """ + iface + """
db = """ + jsonPath + """
# Rate = 1
# Metadata/Extra/Foo = baz, boop
# DatacheckInterval = 2
# DatacheckWindow = 10
#   [[myconf]]
#   password = 0

Metadata/Location/State = CA
Metadata/Location/City = Merced
"""
    with open(sourceName+'.ini', 'wb') as f:
        f.write(ini)
        f.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("csvFile", help="Path to the CSV file from WebCtrl")
    args = parser.parse_args()
    
    print 'Reading', args.csvFile
    locationDict = readCSV(args.csvFile)
    deviceDict = readJSON()

    print "=== MATCHING ==="
    # Loading finished.
    # For each (device, object) tuple in each location in locationDict,
    # look for the (device, object) tuple in deviceDict.
    
    missingObjects = [];
    missingDevices = [];
    allFoundList = [];
    
    # for sMAP driver ini files.
    reportingPort = 4123

    for location in locationDict:
        # Set a list of all devices using in the location.
#         if location[-9:] != 'Penthouse':
#             continue
        
        objCnt = 0
        foundCnt = 0
        foundDevDict = {};
        for (name, devID, objName) in locationDict[location]:
            objCnt += 1
            if (devID) in deviceDict:
                foundCnt += 1
                #print 'Found', devID, 'in', location
                # Prepare to store the object and device
                
                dev = deviceDict[devID]
                foundObj = None
                for bacnetObj in dev['objs']:
                    if bacnetObj['name'] == objName:
                        #print '    Found ojbect:', objName
                        foundObj = bacnetObj
                        break;
                
                # found the device and the object. Store them.
                if foundObj:
                    if devID in foundDevDict:
                        foundDev = foundDevDict[devID]
                    else:
                        foundDev = createDevice([], dev['props'], dev['name'], dev['desc'])
                        foundDev['desc'] = location[location.find(': ') + 2 :]
                        # foundDev['name'] = foundDev['desc']
                        foundDevDict[devID] = foundDev
                    foundObj['desc'] = name
                    foundObj['name'] += ' | ' + name
                    foundDev['objs'].append(foundObj)
                else:
                    # can not found the object. Add it to the missing
                    missingObjects.append(location +','+ name +','+ devID +','+ objName)
            else:
                missingObjects.append(location +','+ name +','+ devID +','+ objName)
                if devID not in missingDevices:
                    missingDevices.append(devID)
        
        print 'Found', foundCnt, 'of', objCnt, 'objects for', location
        if not foundDevDict:
            continue
        # Convert the found device dict to a list
        foundList = []
        for (devID,dev) in foundDevDict.items():
            foundList.append(dev)
        jsonStr = json.dumps(foundList);
        tmp = location[location.find(': ') + 2 :]
        tmp = tmp.replace('/', '_')
        tmp = tmp.replace(' ', '_')
        tmp = tmp.replace(':', '_')
        fn = 'SE1_' + tmp + '.json'
        with open(fn, 'wb') as f:
            f.write(jsonStr)
            print 'Found devices written to', fn
        f.close()
        # Now generate corresponding ini files.
        generateDriverIni('SE1_' + tmp, fn, reportingPort)
        reportingPort += 1
    
    # report missing
    if missingObjects:
        with open('missing.csv', 'wb') as f:
            for s in missingObjects:
                f.write(s + '\n')
    if missingDevices:
        with open('missing_devices.csv', 'wb') as f:
            for s in missingDevices:
                f.write(s + '\n')
