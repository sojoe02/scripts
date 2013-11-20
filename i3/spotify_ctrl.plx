#!/usr/bin/perl
#zeroconf_init.plx
use warnings;
use strict;
use v5.10.0;

use Net::DBus; #qw(:typing);

my $bus = Net::DBus->session;

# Init spotify service and the interface:
my $spotify_service = $bus->get_service("com.spotify.qt");
my $spotify_interface = $spotify_service->get_object("/", "org.freedesktop.MediaPlayer2");

# Init notify-daemon interface and service:
 my $notify_service = $bus->get_service("org.freedesktop.Notifications");
 my $notify_interface = $notify_service->get_object("/org/freedesktop/Notifications","org.freedesktop.Notifications");

my $num_args = $#ARGV +1;
#Handle user arguments:
 if($num_args < 1){
	print "Usage: argument to send command to Spotify via DBus: \n  PlayPause | Next | Previous \n";
	exit;
}

my $app_name          = "spotify_ctrl";
my $id_num_to_replace = 1;
my $icon              = "/usr/share/icons/hicolor/32x32/apps/spotify-client.png";
my $actions_list      = []; #empty array reference
my $hint              = {}; #empty hash reference
my $time              = 1000;   # Use seconds x 1000

my $cmd = $ARGV[0];

if ($cmd eq 'Next' or $cmd eq 'Previous' or $cmd eq 'PlayPause'){
	#print metadata to shell:
	#my @keys = keys %$meta_data;
	#print "$_ $meta_data->{$_}\n" for (keys %$meta_data); 

	$spotify_interface->$cmd;

	my $meta_data = $spotify_interface->GetMetadata();
	
	$notify_interface->Notify(
		$app_name,$id_num_to_replace,'icon'
		,$meta_data->{'xesam:artist'}[0]
		,$meta_data->{'xesam:title'}
		,$actions_list,$hint,$time);

} else {print "Command '$cmd' unknown\n";}
#
