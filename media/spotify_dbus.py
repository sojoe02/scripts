#!/usr/bin/python3

import time
import requests
from requests import HTTPError
import dbus
import argparse
import sys
import imghdr
import logging
import json
from pathlib import Path

# Setup of Dbus:
# Grab the session bus
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

    def request_handler(self, url) :

        try:            
            response = requests.get(url, timeout=1.5)
            #logger.info("response %s",response)
            response.raise_for_status()            
            
        except HTTPError as http_err:
            logger.error(f'HTTP error occurred: %s',http_err) 
        except Exception as err:
            logger.error(f'error occurred: %s',err)  

        else:
            return response

    def process_image_url(self, track_url) : 
        
        open_url = 'https://open.spotify.com/oembed?url='+track_url        
        response = self.request_handler(open_url)
        track_info = json.loads(response.content)
        thumbnail_url = track_info["thumbnail_url"]
        
        return thumbnail_url          
        
    def get_image_path_str(self, track_url, wrong_url) :
        
        # Get the hash of the image (its file name!)
        hash = wrong_url.split('/')[-1]
        image_path = cache_path / hash
        return_path_str = None             

        # Get a new album art image if it does not exist
        if not image_path.exists() :   
            # Try and look it up via the hash given by spotify
            
            art_url = self.process_image_url(track_url)            
            art_image = self.request_handler(art_url).content
 
            open(image_path, 'wb').write(art_image)            
            # Check if the retrieved file is indeed an image
            if not imghdr.what(image_path) is None :        
            # Set the return path string to the newly aquired image as a string
                return_path_str = image_path.as_posix()
            else:
                # If it is not an image remove the file
               logger.warning('Retrieved file is not a valid image file')
               image_path.unlink()
        else :
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
    update_delay = .4

    def __init__(self, player_object):

        self.notifier_object = bus.get_object('org.freedesktop.Notifications',
                '/org/freedesktop/Notifications')

        self.iface = dbus.Interface(self.notifier_object, 'org.freedesktop.Notifications')
        self.prob_iface = dbus.Interface(player_object, 'org.freedesktop.DBus.Properties')

    def notify(self, title, body, album_art, playback_status):

        # Replace '&' with 'and' because of some quirk in dunsts pango engine
        body = body.replace('&', '&amp;')
        body = '<span size="large">' + body + '</span>\n' +\
            '<span size="large">(' + playback_status + ')</span>'
       
        title = title.replace('&', '&amp;')
        # title = '<span size="large">' + title+ '</span>'

        # Send the notification data to the notification server:
        self.iface.Notify(
                self.app_name, 
                self.id_num_to_replace, 
                album_art, 
                title, body, 
                self.actions_list, 
                self.hint, 
                self.delay
                )

    def notify_songinfo(self):        
        # Give Spotify a bit of time to update the metadata attribute.
        time.sleep(self.update_delay)
        # Read property interface data:
        info = self.prob_iface.Get('org.mpris.MediaPlayer2.Player','Metadata')
        playback_status = self.prob_iface.Get('org.mpris.MediaPlayer2.Player', 'PlaybackStatus')
        print(playback_status)
        
        # Grab a path to the album art image via the 'AlbumArt_Handler
        art_handler = Album_Art_Handler()
        
        image_path_str = art_handler.get_image_path_str(str(info['xesam:url']),str(info['mpris:artUrl']))
        
        # Send it to the notification method
        self.notify(str(info['xesam:artist'][0]), str(info['xesam:title']), image_path_str, playback_status)
    
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

        self.iface.Play()
        self.notify()

    def stop(self):

        self.iface.Stop()
        self.notify()

    def openUri(self, uri):

        self.iface.OpenUri(uri)
        self.iface.Play()
        self.notify()
    
# Make a handler instance to handle Spotify and notification control
parser = argparse.ArgumentParser(description=\
        'Script to control spotify via Dbus \
        and notify via the active notification deamon.')

# Initiate parser commands:
parser.add_argument('--next', dest='next', action='store_const',const='next', help='Next number on active playlist')
parser.add_argument('--previous', dest='previous', action='store_const', const='previous', help='Previous number on active playlist')
parser.add_argument('--play_pause', dest='play_pause', action='store_const', const='play_pause', help='Play/Pause current active number')
parser.add_argument('--stop', dest='stop', action='store_const', const='stop', help='Stop current active number')
parser.add_argument('--play', dest='play', action='store_const', const='play', help='Play current active number')
parser.add_argument('--openUri',dest='uri', nargs=1, help='Goto a Spotify URI and play it..')

if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(1)

args = parser.parse_args()

# Initiate the player handler and handle potential Dbus errors:
try:
    player = Player_Handler()

    if args.next is not None :
        player.next()
    elif args.previous is not None:
        player.previous()
    elif args.play_pause is not None:
        player.play_pause()
    elif args.stop is not None:
        player.stop()
    elif args.play is not None:
        player.play()
    elif args.uri is not None:
        player.openUri(args.uri[0])

except dbus.exceptions.DBusException as e:
    logger.error(e)
