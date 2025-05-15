from ouimeaux.environment import Environment
import time
import json
import datetime
import codecs
from urllib2 import urlopen
from dateutil import tz
import sys

def on_switch(switch):
    print "Switch found!", switch.name

def on_motion(motion):
    print "Motion found!", motion.name

env = Environment(on_switch, on_motion)

env.start()

env.discover(seconds = 6)

try:
    landscapeLights = env.get_switch("Wemo Mini")
except:
    print "did not find landscape"

try:
    porchLights = env.get_switch("Porch")
except:
    print "did not find porch"

from_zone = tz.tzutc()
to_zone = tz.tzlocal()

resp = urlopen("http://api.sunrise-sunset.org/json?lat=40.94&lng=-73.83").read()

reader = codecs.getreader("utf-8")

j = json.loads(resp)

sunrise = j["results"]["civil_twilight_begin"]
sunriseObject = datetime.datetime.strptime(sunrise, '%I:%M:%S %p')

civilTwilightEnd = j['results']['civil_twilight_end']
datetime_object = datetime.datetime.strptime(civilTwilightEnd, '%I:%M:%S %p')

todayDate = datetime.datetime.today().date()

#handles when civil twilight end is after midnight in UTC
if datetime_object.hour > 12:
    todayTime = datetime.datetime.combine(todayDate, datetime_object.time())
else:
    tomorrow = todayDate + datetime.timedelta(days=1)
    todayTime = datetime.datetime.combine(tomorrow, datetime_object.time())

sunriseTime = datetime.datetime.combine(todayDate, sunriseObject.time())

utc = todayTime.replace(tzinfo=from_zone)

localOnTime = utc.astimezone(to_zone)
localOnTime = localOnTime - datetime.timedelta(minutes=25)

utcSunrise = sunriseTime.replace(tzinfo=from_zone)
localSunrise = utcSunrise.astimezone(to_zone)
print "Local Sunrise:", localSunrise

earliestOnTime = datetime.datetime.combine(todayDate, datetime.time(06, 0, 0))
earliestOnTime = earliestOnTime.replace(tzinfo=to_zone)
offDateTime = datetime.datetime.combine(todayDate, datetime.time(22, 0, 0))
offDateTime = offDateTime.replace(tzinfo=to_zone)

print "Earliest On Time:", earliestOnTime
print "On time night:", localOnTime
print "Off time night:", offDateTime
print

now = datetime.datetime.now()
#now = datetime.datetime(2018,1,23,06,20)
now = now.replace(tzinfo=to_zone)

print "Now:", now

def porchOn():
    try:
        porchLights.on()
    except:
        print('failed turning on porch lights')

def landscapeOn():
    try:
        landscapeLights.on()
    except:
        print('failed turning on landscape lights')

if now > earliestOnTime and now < localSunrise:
    print "turn on morning"
    landscapeOn()
    #landscapeLights.on()
    porchOn()
    sys.exit()

if now > localOnTime and offDateTime > now:
    print "turn on night"
    #landscapeLights.on()
    landscapeOn()
    porchOn()
    #porchLights.on()
    sys.exit()


print "turn off"

try:
    porchLights.off()
except:
    print('failed turning off porch lights')
try:
    landscapeLights.off()
except:
    print('failed turning off landscrape lights')

print "finished"
