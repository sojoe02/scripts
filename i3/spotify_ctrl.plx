#!/usr/bin/perl
#zeroconf_init.plx
use warnings;
use strict;
use v5.10.0;

use Net::DBus qw(:typing);

my $bus = Net::DBus->session;

# Init spotify service and the interface:
# my $spotify_service = $bus->get_service("com.spotify.qt");
# my $spotify_interface = $spotify_service->get_object("/", "org.freedesktop.MediaPlayer2");

# Init notify-daemon interface and service:
 my $notify_service = $bus->get_service("org.freedesktop.Notifications");
 my $notify_interface = $notify_service->get_object("/org/freedesktop/Notifications","org.freedesktop.Notifications");

# my $num_args = $#ARGV +1;

#Handle user arguments:
# if($num_args < 1){
#	print "Usage: command to send to Spotify via DBus i.e \n  play | play_pause | stop | seek-[s]| seek+[s] | next | previous \n";
#	exit;
#}
my $value = dbus_array([dbus_string('')]);

# my $cmd = $ARGV[0];
# if ($ARGV[0] eq 'Seek'){
#	$spotify_interface->$cmd($ARGV[1]);	
# } elsif ($ARGV[0] eq 'Next' or $ARGV[0] eq 'Previous'){
#	$spotify_interface->$cmd;
	$notify_interface->Notify(dbus_string("Test Application")
		,dbus_uint32(0)
		,dbus_string('')
		,dbus_string('Title')
		,dbus_string('Body')
		,$value
		,dbus_dict(dbus_string(''))
		,dbus_int32(1000));
	#`notify-send "playing next number"`
#}else {$spotify_interface->$cmd;}
# interface->Next;
#
#$spotify_interface->GetMetadata;


