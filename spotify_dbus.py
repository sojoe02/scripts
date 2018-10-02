#!/usr/bin/python3
#import os
import time
import requests
import dbus
import argparse
import sys
from pathlib import Path

# Setup of Dbus:
bus = dbus.SessionBus()
player = bus.get_object('org.mpris.MediaPlayer2.spotify', '/org/mpris/MediaPlayer2')
# Create the interface:
iface = dbus.Interface(player, 'org.mpris.MediaPlayer2.Player')
prob_iface = dbus.Interface(player, 'org.freedesktop.DBus.Properties')
# Set a directory for the album-art cache:
cache_path = Path('~/.cache/spotify_control').expanduser()
# Create the directory if it does not exist:
cache_path.mkdir(parents=True, exist_ok=True)
print (cache_path)

class AlbumArt_Handler:
    #def get_imagePath(self, image_path):
        
    def check_image(self, spotify_path):
        print(spotify_path)
        hash = spotify_path.split('/')[-1]
        image_path = cache_path / hash
        print (image_path)
        if image_path.exists():
            print('path exists ... doing nothing')
            return image_path
        else:
            request = requests.get(spotify_path)
            open(image_path, 'wb').write(request.content)
            print('path doe not exist doing something')
            return image_path



class Player_Handler:
    
    def notify(self, title, body, album_art):
        item              = "org.freedesktop.Notifications"
        path              = "/org/freedesktop/Notifications"
        interface         = "org.freedesktop.Notifications"
        app_name          = "spotify_ctrl"
        id_num_to_replace = 1 
        icon              ="/usr/share/icons/hicolor/32x32/apps/spotify.png"
        print (icon)
        actions_list      = ''
        hint              = ''
        delay              = 1000   # Use seconds x 1000
        body = '<span font="14">' + body + '</span>'
        title = '<span font="16">' + title+ '</span>'

        notif = bus.get_object(item, path)
        notify = dbus.Interface(notif, interface)
        notify.Notify(app_name, id_num_to_replace, album_art, title, body, actions_list, hint, delay)


    def notify_songinfo(self):
        # Read the interface data:
        time.sleep(.2)
        info = prob_iface.Get('org.mpris.MediaPlayer2.Player','Metadata')

        art_handler = AlbumArt_Handler()
        image_path = art_handler.check_image(str(info['mpris:artUrl']))
        print(type(image_path))
        print(image_path.as_posix())


        # print(info)
        # OUT: [dbus.String(u'xesam:album'), dbus.String(u'xesam:title'), 
        # dbus.String(u'xesam:trackNumber'), dbus.String(u'xesam:artist'), 
        # dbus.String(u'xesam:discNumber'), dbus.String(u'mpris:trackid'), 
        # dbus.String(u'mpris:length'), dbus.String(u'mpris:artUrl'), 
        # dbus.String(u'xesam:autoRating'), dbus.String(u'xesam:contentCreated'), 
        # dbus.String(u'xesam:url')]
        self.notify(str(info['xesam:artist'][0]), str(info['xesam:title']), image_path.as_posix())

    def next(self):
        iface.Next()
        self.notify_songinfo()

    def previous(self):
        iface.Previous()
        self.notify_songinfo()

    def play_pause(self):
        iface.PlayPause()
        self.notify_songinfo()

    def play(self):
        iface.Play
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
        const=handler.play,help='Play current active number')

if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(1)


args = parser.parse_args()
args.cmd()

