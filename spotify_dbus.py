#!/usr/bin/python3

import dbus
import argparse
import sys
# Setup of Dbus:
bus = dbus.SessionBus()
player = bus.get_object('org.mpris.MediaPlayer2.spotify', '/org/mpris/MediaPlayer2')
# Create the interface:
iface = dbus.Interface(player, 'org.mpris.MediaPlayer2.Player')
prob_iface = dbus.Interface(player, 'org.freedesktop.DBus.Properties')

        
class Player_Handler:
    
    def notify(self, title, body):
        item              = "org.freedesktop.Notifications"
        path              = "/org/freedesktop/Notifications"
        interface         = "org.freedesktop.Notifications"
        app_name          = "spotify_ctrl"
        id_num_to_replace = 1 
        icon              = "/usr/share/icons/hicolor/32x32/apps/spotify-client.png"
        actions_list      = ''
        hint              = ''
        time              = 1000   # Use seconds x 1000

        notif = bus.get_object(item, path)
        notify = dbus.Interface(notif, interface)
        notify.Notify(app_name, id_num_to_replace, icon, \
                title , body, actions_list, hint, time)


    def notify_songinfo(self):
        # Read the interface data:
        #info = iface.GetMetadata()
        info = prob_iface.Get('org.mpris.MediaPlayer2.Player','Metadata')
        # print(info)
        # OUT: [dbus.String(u'xesam:album'), dbus.String(u'xesam:title'), 
        # dbus.String(u'xesam:trackNumber'), dbus.String(u'xesam:artist'), 
        # dbus.String(u'xesam:discNumber'), dbus.String(u'mpris:trackid'), 
        # dbus.String(u'mpris:length'), dbus.String(u'mpris:artUrl'), 
        # dbus.String(u'xesam:autoRating'), dbus.String(u'xesam:contentCreated'), 
        # dbus.String(u'xesam:url')]
        self.notify(str(info['xesam:artist'][0]), str(info['xesam:title']))

    def next(self):
        iface.Next()
        self.notify_songinfo()

    def previous(self):
        iface.Previous()
        self.notify_songinfo()

    def play_pause(self):
        iface.PlayPause()
        self.notify_songinfo()

    

handler = Player_Handler()

#Initiating the parser, to call dbus interface methods:
parser = argparse.ArgumentParser(description=\
        'Script to control spotify via Dbus \
        and notify via the active notification deamon.')

parser.add_argument('--next',dest='cmd',action='store_const',\
        const=handler.next, help='Next number on active playlist')

parser.add_argument('--previous',dest='cmd',action='store_const',\
        const=handler.previous,help='Previous number on active playlist')

parser.add_argument('--play_pause',dest='cmd',action='store_const',\
        const=handler.play_pause,help='Play/Pause current active number')

parser.add_argument('--stop',dest='cmd',action='store_const',\
        const=iface.Stop,help='Stop current active number')

parser.add_argument('--play',dest='cmd',action='store_const',\
        const=iface.Play,help='Play current active number')

if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(1)


args = parser.parse_args()
args.cmd()

