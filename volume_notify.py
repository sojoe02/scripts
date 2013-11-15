#!/usr/bin/python

from subprocess import call,check_output

import re
import sys
import dbus

#bindsym Shift+Pause exec amixer -q set Master 2dB+ unmute
#bindsym Shift+Scroll_Lock exec amixer -q set Master toggle

#bindsym Shift+Print exec amixer -q set Master 2dB- unmute


if len(sys.argv) == 1:
    sys.exit(1)

#check user arguments and adjust alsamixer accordingly:
if sys.argv[1] == "vol+":
    if len(sys.argv) == 3:
        add = sys.argv[2] + "dB+"
        call(["amixer", "-q", "set", "Master", add, "unmute"])
elif sys.argv[1] == "vol-":
    if len(sys.argv) == 3:
        add = sys.argv[2] + "dB-"
        call(["amixer", "-q", "set", "Master", add, "unmute"])
elif sys.argv[1] == "toggle":
    call(["amixer", "-q", "set", "Master", "toggle"])


# Create the regular expression pattern to match againts:
pattern_volume = re.compile('[0-9]+%')
pattern_mute = re.compile('(\[on\])|(\[off\])')

# Call shell command amixer to retrieve an object 
# containing information on Master
get_amixer = check_output(["amixer", "get", "'Master'"])

# Run the re patter against the amixer output and retrieve volume.
volume = pattern_volume.search(str(get_amixer)).group()
mute = pattern_mute.search(str(get_amixer)).group()

mutestatus = ("sound off" if mute =="[off]" else "sound on")

# init Dbus notification:
item              = "org.freedesktop.Notifications"
path              = "/org/freedesktop/Notifications"
interface         = "org.freedesktop.Notifications"
app_name          = "spotify_ctrl"
id_num_to_replace = 1 
icon              = "/usr/share/icons/hicolor/32x32/apps/spotify-client.png"
actions_list      = ''
hint              = ''
time              = 1000   # Use seconds x 1000

bus = dbus.SessionBus()
notif = bus.get_object(item, path)
notify = dbus.Interface(notif, interface)

#Notify via the active notication daemon:
notify.Notify(app_name, id_num_to_replace, icon, \
        "Volume:" ,volume + " (" + mutestatus +")" , actions_list, hint, time)


