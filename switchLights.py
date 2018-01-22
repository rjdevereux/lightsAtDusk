from ouimeaux.environment import Environment
import time
import json
import datetime
import codecs
from urllib2 import urlopen
from dateutil import tz

def on_switch(switch):
    print "Switch found!", switch.name

def on_motion(motion):
    print "Motion found!", motion.name

env = Environment(on_switch, on_motion)

env.start()

env.discover(seconds = 3)

switch = env.get_switch("Wemo Mini")

from_zone = tz.tzutc()
to_zone = tz.tzlocal()

resp = urlopen("https://api.sunrise-sunset.org/json?lat=40.94&lng=-73.83").read()

reader = codecs.getreader("utf-8")

j = json.loads(resp)

timeString = j['results']['civil_twilight_end']
datetime_object = datetime.datetime.strptime(timeString, '%I:%M:%S %p')

todayDate = datetime.datetime.today().date()
todayTime = datetime.datetime.combine(todayDate, datetime_object.time())

utc = todayTime.replace(tzinfo=from_zone)

localOnTime = utc.astimezone(to_zone)
localOnTime = localOnTime - datetime.timedelta(minutes=25)

offDateTime = datetime.datetime.combine(todayDate, datetime.time(22, 0, 0))
offDateTime = offDateTime.replace(tzinfo=to_zone)

print "On time:", localOnTime
print "Off time:", offDateTime
print

now = datetime.datetime.now()
now = now.replace(tzinfo=to_zone)

print "Now:", now

if now > localOnTime and offDateTime > now:
    print "turn on"
    switch.on()
else:
    print "turn off"
    switch.off()
print "finished"
