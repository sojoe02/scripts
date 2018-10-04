#!/usr/bin/python3

import time
import requests
import dbus
import argparse
import sys
import imghdr
import logging

from pathlib import Path

# Setup of Dbus:
# Grab the session bus and spotify object
bus = dbus.SessionBus()

# Set a directory for the album-art cache:
cache_path = Path('~/.cache/spotify_control').expanduser()
# Create the directory if it does not exist:
cache_path.mkdir(parents=True, exist_ok=True)

# Set up logging (mostly for the sake of the requests)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

log_handler = logging.FileHandler(cache_path / 'log', mode='a', encoding=None, delay=False)
log_handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log_handler.setFormatter(formatter)

logger.addHandler(log_handler)

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
            try :
                request = requests.get(spotify_path_str, timeout=1.5)
                
                # If the request is successful retrieve the image at the destination
                if request.status_code == requests.codes.ok : 
                    open(image_path, 'wb').write(request.content)
                
                    # Check if the retrieved file is indeed an image
                    if not imghdr.what(image_path) is None :        
                        # Set the return path string to the newly aquired image as a string
                        return_path_str = image_path.as_posix()

                    else :
                        # If it is not an image remove the file
                        logger.warning('Retrieved file is not a valid image file')
                        image_path.unlink()

            except requests.exceptions.Timeout:
                logger.error('Timeout on album art retrieval request')
            except requests.exceptions.RequestException as e:
                logger.error(e)
                
            
        else:
            return_path_str = image_path.as_posix()

        return return_path_str

###
# Handles communication with the notification server (Dunst)
##
class Notification_Handler:

    app_name = "spotify_ctrl"
    id_num_to_replace = 1
    actions_list = ''
    hint = ''
    delay = 1500

    def __init__(self, player_object):

        self.notifier_object = bus.get_object('org.freedesktop.Notifications', '/org/freedesktop/Notifications')
        self.iface = dbus.Interface(self.notifier_object, 'org.freedesktop.Notifications')
        self.prob_iface = dbus.Interface(player_object, 'org.freedesktop.DBus.Properties')

    def notify(self, title, body, album_art):

        # Replace '&' with 'and' because of some quirk in dunsts pango engine
        body = body.replace('&', 'and')
        body = '<span size="x-large">' + body + '</span>'
       
        title = title.replace('&', 'and')
        title = '<span size="large" font_weight="bold">' + title+ '</span>'

        # Send the notification data to the notification server:
        self.iface.Notify(self.app_name, self.id_num_to_replace, album_art, title, body, self.actions_list, self.hint, self.delay)

    def notify_songinfo(self):
        # Give Spotify a bit of time to update the metadata attribute.
        time.sleep(.2)
        # Read property interface data:
        info = self.prob_iface.Get('org.mpris.MediaPlayer2.Player','Metadata')

        # Grab a path to the album art image via the 'AlbumArt_Handler
        art_handler = Album_Art_Handler()
        image_path_str = art_handler.get_image_path_str(str(info['mpris:artUrl']))

        # Send it to the notification method
        self.notify(str(info['xesam:artist'][0]), str(info['xesam:title']), image_path_str)

    

###
# Handles all dbus communication between the given control arguments and the media player (Spotify)
###
class Player_Handler:

    def __init__(self):

        #Get the dbus object
        self.player_object = bus.get_object('org.mpris.MediaPlayer2.spotify', '/org/mpris/MediaPlayer2')
        # Create the interface:
        self.iface = dbus.Interface(self.player_object, 'org.mpris.MediaPlayer2.Player')
    
    def notify(self):

        try:            
            self.notifier = Notification_Handler(self.player_object) 
            self.notifier.notify_songinfo()
        except dbus.exceptions.DBusException as e:
            logger.warning(e)

    def next(self):

        self.iface.Next()
        self.notify()

    def previous(self):

        self.iface.Previous()
        self.notify()

    def play_pause(self):

        self.iface.PlayPause()
        self.notify()

    def play(self):

        self.iface.Play
        self.notify()

    def stop(self):

        self.iface.Stop
        self.notify()
    
# Make a handler instance to handle Spotify and notification control

parser = argparse.ArgumentParser(description=\
        'Script to control spotify via Dbus \
        and notify via the active notification deamon.')

# Handle potential Dbus errors on the player side:
try:
    player = Player_Handler()

    # Initiate parser commands:
    parser.add_argument('--next',dest='cmd',action='store_const',\
        const=player.next, help='Next number on active playlist')

    parser.add_argument('--previous',dest='cmd',action='store_const',\
        const=player.previous,help='Previous number on active playlist')

    parser.add_argument('--play_pause',dest='cmd',action='store_const',\
        const=player.play_pause,help='Play/Pause current active number')

    parser.add_argument('--stop',dest='cmd',action='store_const',\
        const=player.stop,help='Stop current active number')

    parser.add_argument('--play',dest='cmd',action='store_const',\
        const=player.play,help='Play current active number')

except dbus.exceptions.DBusException as e:
    logger.error(e)

if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(1)


args = parser.parse_args()
args.cmd()

