#!/usr/bin/python3

import time
import requests
import dbus
import argparse
import sys
import imghdr

from pathlib import Path

# Setup of Dbus:
# Grab the session bus and spotify object
bus = dbus.SessionBus()
player = bus.get_object('org.mpris.MediaPlayer2.spotify', '/org/mpris/MediaPlayer2')

# Create the interface:
iface = dbus.Interface(player, 'org.mpris.MediaPlayer2.Player')
prob_iface = dbus.Interface(player, 'org.freedesktop.DBus.Properties')

# Set a directory for the album-art cache:
cache_path = Path('~/.cache/spotify_control').expanduser()
# Create the directory if it does not exist:
cache_path.mkdir(parents=True, exist_ok=True)

###
# Handles album art path and type checks via the spotify metadata field and the pre-defined cache dir
# Makes sure there is album art as the icon field in the notification, if possible.
###
class Album_Art_Handler:

    default_icon_path_str ="/usr/share/icons/hicolor/32x32/apps/spotify.png"
    
    def get_image_path_str(self, spotify_path_str) :
        # Get the hash of the image (it's name)
        hash = spotify_path_str.split('/')[-1]
        image_path = cache_path / hash

        return_path_str = self.default_icon_path_str

        # Get a new album art image if it does not exist
        if not image_path.exists() :

            # Try and look it up via the hash given by spotify
            request = requests.get(spotify_path_str)
                
            # If the request is successful retrieve the image at the destination
            if request.status_code == requests.codes.ok : 
                open(image_path, 'wb').write(request.content)
                
                # Check if the retrieved file is indeed an image
                if not imghdr.what(image_path) is None :        
                    # Set the return path string to the newly aquired image as a string
                    return_path_str = image_path.as_posix()

                else :
                    # If it is not an image remove the file
                    image_path.unlink()
            
        else:
            return_path_str = image_path.as_posix()

        return return_path_str

###
# Handles all dbus communication between the given control arguments, Spotify and the notification server (Dunst)
###
class Player_Handler:
    
    def notify(self, title, body, album_art):
        item              = "org.freedesktop.Notifications"
        path              = "/org/freedesktop/Notifications"
        interface         = "org.freedesktop.Notifications"
        app_name          = "spotify_ctrl"
        id_num_to_replace = 1 
        actions_list      = ''
        hint              = ''
        delay              = 1500   # Use seconds x 1000

        # Replace '&' with 'and' because of some quirk in dunsts pango engine
        body = body.replace('&', 'and')
        body = '<span size="x-large">' + body + '</span>'
       
        title = title.replace('&', 'and')
        title = '<span size="large" font_weight="bold">' + title+ '</span>'

        notif = bus.get_object(item, path)
        notify = dbus.Interface(notif, interface)
        # Send the notification data to the notification server:
        notify.Notify(app_name, id_num_to_replace, album_art, title, body, actions_list, hint, delay)

    def notify_songinfo(self):
        # Give Spotify a bit of time to update the metadata attribute.
        time.sleep(.2)
        # Read the interface data:
        info = prob_iface.Get('org.mpris.MediaPlayer2.Player','Metadata')

        # Grab a path to the album art image via the 'AlbumArt_Handler
        art_handler = Album_Art_Handler()
        image_path_str = art_handler.get_image_path_str(str(info['mpris:artUrl']))

        # Send it to the notification method
        self.notify(str(info['xesam:artist'][0]), str(info['xesam:title']), image_path_str)

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
    
# Make a handler instance to handle all the Spotify and notification control
handler = Player_Handler()

# Initiating the parser, to call dbus interface methods:
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

