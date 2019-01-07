#!/opt/local/bin/python

from os.path import expanduser
from fritzconnection import FritzCall
from string import Template
import datetime
import osascript
import configparser

# create an AppleScript to execute
def appleScript(callInfo):
    template = Template("""
set dtstart to (current date)
set day of dtstart to 1
set year of dtstart to $startyear
set month of dtstart to $startmonth
set day of dtstart to $startday
set hours of dtstart to $starthour
set minutes of dtstart to $startminute
set seconds of dtstart to $startsecond

set dtend to (current date)
set day of dtend to 1
set year of dtend to $endyear
set month of dtend to $endmonth
set day of dtend to $endday
set hours of dtend to $endhour
set minutes of dtend to $endminute
set seconds of dtend to $endsecond

tell application "TimingHelper"
	add task from ((dtstart)) to ((dtend)) with title "Telefonat mit $caller" project (front project whose name is "Telefon")
end tell
""")
    return template.substitute(callInfo)

# read config file
cfgname = expanduser("~/.phonetotiming.ini")
config = configparser.ConfigParser()
config.read(cfgname)
fritzPassword = config['main']['password']
firstRun = 'firstrun' in config['main']
if firstRun:
    del config['main']['firstrun']
    config['main']['lastprocessed'] = '0'

debug = 'debug' in config['main'] and config['main']['debug'] == 'true' 
if debug:
    print ("phonetotiming.py running at " + str(datetime.datetime.now()))

lastprocessed = int(config['main']['lastprocessed'])
currentprocessed = lastprocessed
hadError = False

# connect to Fritz!Box
fCall = FritzCall(password=fritzPassword)

# read call list
calls = fCall.get_calls()

for call in calls:
    callInfo = {}
    # process all calls with id after lastprocessed
    if call['Id'] > lastprocessed:
        if debug:
            print("Found new Call with Id " + str(call['Id']))
        currentprocessed = max(currentprocessed, call['Id'])

        if not firstRun:
            # if there is a phonebook entry for the caller, use that
            if call['Name'] != None:
                callInfo['caller'] = call['Name']
            # else read the remote phone number depending on the type of call
            else:
                if call['Type'] == 3:
                    # outgoing call
                    callInfo['caller'] = call['Called']
                else:
                    # incoming and missed calls
                    callInfo['caller'] = call['Caller']

            callDuration = call['Duration']
            if callDuration.total_seconds() < 5:
                if debug:
                    print ("skipping call, because it is too short (<5s)")
                continue

            # decompose start and end date
            startDate = call['Date']
            callInfo['startyear'] = startDate.year
            callInfo['startmonth'] = startDate.month
            callInfo['startday'] = startDate.day
            callInfo['starthour'] = startDate.hour
            callInfo['startminute'] = startDate.minute
            callInfo['startsecond'] = startDate.second
            
            endDate = startDate + callDuration
            callInfo['endyear'] = endDate.year
            callInfo['endmonth'] = endDate.month
            callInfo['endday'] = endDate.day
            callInfo['endhour'] = endDate.hour
            callInfo['endminute'] = endDate.minute
            callInfo['endsecond'] = endDate.second

            # fill AppleScript template
            if debug:
                print("Executing AppleScript")
            script = appleScript(callInfo)
            code,out,err = osascript.run(script)
            if code != 0:
                print ("osascript return code = " + str(code))
                print (out)
                print (err)
                hadError = True

# finally write new lastprocessed into config
if not hadError:
    config['main']['lastprocessed'] = str(currentprocessed)
    with open(cfgname, 'w') as configfile:
        config.write(configfile)

if firstRun:
    print(r'\o/ - everything seems to work. The latest call on your call list has the Id ' + str(currentprocessed) + '.')

if debug:
    print("phonetotiming.py done at " + str(datetime.datetime.now()))
