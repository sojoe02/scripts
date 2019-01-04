#!/bin/bash

IN="eDP1"
EXT="HDMI2"
EXT2="HDMI2"

if (xrandr | grep "$EXT disconnected") ; then
	xrandr --output $IN --auto --output $EXT --off 
	#--output $EXT2 --off
elif [ $# -gt 0 ]; then
	if [ $1 == "off" ]; then
		xrandr --output $IN --auto --output $EXT --off 
		#--output $EXT2 --off
	fi
else
	#xrandr --output $IN --off --output $IN --off --output $EXT2 --auto --primary --output $EXT 
	xrandr --output $IN --auto --output $EXT --auto --right-of $IN --primary 
	#--auto --right-of $EXT2 
	#feh --bg-scale /home/sojoe/dropbox/wallpaper-2684320.jpg
fi
